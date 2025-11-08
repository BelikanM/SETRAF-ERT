import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import nodemailer from 'nodemailer';
import User from '../models/User.js';
import Session from '../models/Session.js';

// Générer les tokens JWT
const generateTokens = (userId) => {
  const accessToken = jwt.sign(
    { userId, type: 'access' },
    process.env.JWT_SECRET,
    { expiresIn: '15m' } // Token d'accès valide 15 minutes
  );

  const refreshToken = jwt.sign(
    { userId, type: 'refresh' },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' } // Token de rafraîchissement valide 7 jours
  );

  return { accessToken, refreshToken };
};

// Configuration du transporter email
const createEmailTransporter = () => {
  return nodemailer.createTransporter({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
};

// @desc    Inscription d'un nouvel utilisateur
// @route   POST /api/auth/register
// @access  Public
export const register = async (req, res) => {
  try {
    const { username, email, password, firstName, lastName, organization, country } = req.body;

    // Validation des champs requis
    if (!username || !email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Veuillez fournir tous les champs requis'
      });
    }

    // Vérifier si l'utilisateur existe déjà
    const existingUser = await User.findOne({
      $or: [{ email }, { username }]
    });

    if (existingUser) {
      if (existingUser.email === email) {
        return res.status(400).json({
          success: false,
          message: 'Cet email est déjà utilisé'
        });
      }
      return res.status(400).json({
        success: false,
        message: 'Ce nom d\'utilisateur est déjà pris'
      });
    }

    // Créer un token de vérification
    const verificationToken = crypto.randomBytes(32).toString('hex');

    // Créer le nouvel utilisateur
    const user = await User.create({
      username,
      email,
      password,
      firstName,
      lastName,
      organization,
      country,
      verificationToken
    });

    // Envoyer l'email de vérification
    try {
      const transporter = createEmailTransporter();
      const verificationUrl = `http://localhost:8504/verify-email?token=${verificationToken}`;
      
      await transporter.sendMail({
        from: `"SETRAF-ERT" <${process.env.EMAIL_USER}>`,
        to: email,
        subject: '🔬 Vérification de votre compte SETRAF-ERT',
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2e5c8a;">Bienvenue sur SETRAF-ERT ! 💧</h2>
            <p>Bonjour ${firstName || username},</p>
            <p>Merci de vous être inscrit sur la plateforme SETRAF-ERT - Analyse géophysique avancée.</p>
            <p>Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :</p>
            <div style="text-align: center; margin: 30px 0;">
              <a href="${verificationUrl}" 
                 style="background-color: #2e5c8a; color: white; padding: 12px 30px; 
                        text-decoration: none; border-radius: 5px; display: inline-block;">
                Vérifier mon email
              </a>
            </div>
            <p style="color: #666; font-size: 12px;">
              Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
              <a href="${verificationUrl}">${verificationUrl}</a>
            </p>
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
              Si vous n'avez pas créé ce compte, ignorez cet email.
            </p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #999; font-size: 11px; text-align: center;">
              © 2025 SETRAF-ERT - Tous droits réservés
            </p>
          </div>
        `
      });
    } catch (emailError) {
      console.error('Erreur d\'envoi d\'email:', emailError);
      // Continue quand même, l'utilisateur peut demander un nouvel email
    }

    res.status(201).json({
      success: true,
      message: 'Inscription réussie ! Un email de vérification a été envoyé.',
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName
      }
    });
  } catch (error) {
    console.error('Erreur d\'inscription:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de l\'inscription',
      error: error.message
    });
  }
};

// @desc    Connexion utilisateur
// @route   POST /api/auth/login
// @access  Public
export const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Veuillez fournir email et mot de passe'
      });
    }

    // Trouver l'utilisateur
    const user = await User.findOne({ email }).select('+password');

    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Email ou mot de passe incorrect'
      });
    }

    // Vérifier si le compte est verrouillé
    if (user.isLocked) {
      return res.status(403).json({
        success: false,
        message: 'Compte temporairement verrouillé suite à plusieurs tentatives échouées. Réessayez plus tard.'
      });
    }

    // Vérifier si le compte est actif
    if (!user.isActive) {
      return res.status(403).json({
        success: false,
        message: 'Compte désactivé'
      });
    }

    // Vérifier le mot de passe
    const isPasswordValid = await user.comparePassword(password);

    if (!isPasswordValid) {
      // Incrémenter les tentatives de connexion
      await user.incLoginAttempts();
      
      return res.status(401).json({
        success: false,
        message: 'Email ou mot de passe incorrect'
      });
    }

    // Réinitialiser les tentatives de connexion
    await user.resetLoginAttempts();

    // Générer les tokens
    const { accessToken, refreshToken } = generateTokens(user._id);

    // Créer une session
    const ipAddress = req.ip || req.connection.remoteAddress;
    const userAgent = req.headers['user-agent'];

    await Session.create({
      userId: user._id,
      refreshToken,
      ipAddress,
      userAgent,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 jours
    });

    res.json({
      success: true,
      message: 'Connexion réussie',
      accessToken,
      refreshToken,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        emailVerified: user.emailVerified,
        organization: user.organization,
        country: user.country
      }
    });
  } catch (error) {
    console.error('Erreur de connexion:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la connexion',
      error: error.message
    });
  }
};

// @desc    Rafraîchir le token d'accès
// @route   POST /api/auth/refresh
// @access  Public
export const refreshToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: 'Refresh token manquant'
      });
    }

    // Vérifier le refresh token
    const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);

    // Vérifier la session
    const session = await Session.findOne({
      refreshToken,
      userId: decoded.userId,
      isValid: true
    });

    if (!session) {
      return res.status(401).json({
        success: false,
        message: 'Session invalide ou expirée'
      });
    }

    // Générer un nouveau access token
    const accessToken = jwt.sign(
      { userId: decoded.userId, type: 'access' },
      process.env.JWT_SECRET,
      { expiresIn: '15m' }
    );

    res.json({
      success: true,
      accessToken
    });
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Refresh token expiré'
      });
    }

    console.error('Erreur de rafraîchissement:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors du rafraîchissement du token'
    });
  }
};

// @desc    Déconnexion
// @route   POST /api/auth/logout
// @access  Private
export const logout = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (refreshToken) {
      // Invalider la session
      await Session.updateOne(
        { refreshToken },
        { $set: { isValid: false } }
      );
    }

    res.json({
      success: true,
      message: 'Déconnexion réussie'
    });
  } catch (error) {
    console.error('Erreur de déconnexion:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la déconnexion'
    });
  }
};

// @desc    Vérifier l'email
// @route   GET /api/auth/verify-email/:token
// @access  Public
export const verifyEmail = async (req, res) => {
  try {
    const { token } = req.params;

    const user = await User.findOne({ verificationToken: token });

    if (!user) {
      return res.status(400).json({
        success: false,
        message: 'Token de vérification invalide'
      });
    }

    user.emailVerified = true;
    user.verificationToken = undefined;
    await user.save();

    res.json({
      success: true,
      message: 'Email vérifié avec succès'
    });
  } catch (error) {
    console.error('Erreur de vérification email:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la vérification de l\'email'
    });
  }
};

// @desc    Obtenir le profil utilisateur
// @route   GET /api/auth/me
// @access  Private
export const getProfile = async (req, res) => {
  try {
    res.json({
      success: true,
      user: req.user
    });
  } catch (error) {
    console.error('Erreur récupération profil:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération du profil'
    });
  }
};

// @desc    Réinitialiser le mot de passe (demande)
// @route   POST /api/auth/forgot-password
// @access  Public
export const forgotPassword = async (req, res) => {
  try {
    const { email } = req.body;

    const user = await User.findOne({ email });

    if (!user) {
      // Ne pas révéler si l'utilisateur existe ou non
      return res.json({
        success: true,
        message: 'Si cet email existe, un lien de réinitialisation a été envoyé'
      });
    }

    // Générer un token de réinitialisation
    const resetToken = crypto.randomBytes(32).toString('hex');
    user.resetPasswordToken = crypto
      .createHash('sha256')
      .update(resetToken)
      .digest('hex');
    user.resetPasswordExpires = Date.now() + 3600000; // 1 heure

    await user.save();

    // Envoyer l'email
    const transporter = createEmailTransporter();
    const resetUrl = `http://localhost:8504/reset-password?token=${resetToken}`;

    await transporter.sendMail({
      from: `"SETRAF-ERT" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: '🔐 Réinitialisation de votre mot de passe SETRAF-ERT',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #2e5c8a;">Réinitialisation de mot de passe</h2>
          <p>Vous avez demandé une réinitialisation de votre mot de passe.</p>
          <p>Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="${resetUrl}" 
               style="background-color: #2e5c8a; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
              Réinitialiser mon mot de passe
            </a>
          </div>
          <p style="color: #666; font-size: 12px;">
            Ce lien expire dans 1 heure.
          </p>
          <p style="color: #666; font-size: 12px;">
            Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
          </p>
        </div>
      `
    });

    res.json({
      success: true,
      message: 'Si cet email existe, un lien de réinitialisation a été envoyé'
    });
  } catch (error) {
    console.error('Erreur forgot password:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la demande de réinitialisation'
    });
  }
};

// @desc    Envoyer un code OTP par email
// @route   POST /api/auth/send-otp
// @access  Public
export const sendOTP = async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({
        success: false,
        message: 'Email requis'
      });
    }

    // Vérifier si l'utilisateur existe
    const user = await User.findOne({ email });

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Aucun compte associé à cet email'
      });
    }

    // Générer un code OTP à 6 chiffres
    const otpCode = Math.floor(100000 + Math.random() * 900000).toString();
    const otpExpires = Date.now() + 10 * 60 * 1000; // 10 minutes

    // Stocker l'OTP dans l'utilisateur
    user.otpCode = otpCode;
    user.otpExpires = otpExpires;
    await user.save();

    // Envoyer l'email
    try {
      const transporter = createEmailTransporter();
      
      await transporter.sendMail({
        from: `"SETRAF-ERT" <${process.env.EMAIL_USER}>`,
        to: email,
        subject: '🔐 Votre code OTP SETRAF-ERT',
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; border-radius: 15px;">
            <div style="background: white; padding: 30px; border-radius: 10px;">
              <h2 style="color: #667eea; text-align: center; margin-bottom: 30px;">
                🔐 Code d'authentification SETRAF-ERT
              </h2>
              <p style="font-size: 16px; color: #333;">Bonjour ${user.firstName || user.username},</p>
              <p style="font-size: 16px; color: #333;">
                Voici votre code d'authentification à usage unique (OTP) :
              </p>
              <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; text-align: center; margin: 30px 0;">
                <div style="font-size: 48px; font-weight: bold; color: white; letter-spacing: 8px; font-family: monospace;">
                  ${otpCode}
                </div>
              </div>
              <p style="font-size: 14px; color: #666; text-align: center;">
                ⏰ Ce code expire dans <strong>10 minutes</strong>
              </p>
              <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <p style="margin: 0; color: #856404; font-size: 13px;">
                  <strong>⚠️ Sécurité :</strong> Ne partagez jamais ce code. 
                  Si vous n'avez pas demandé ce code, ignorez cet email.
                </p>
              </div>
              <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
              <p style="color: #999; font-size: 11px; text-align: center; margin: 0;">
                © 2025 SETRAF-ERT - Analyse géophysique avancée<br>
                Tous droits réservés
              </p>
            </div>
          </div>
        `
      });

      res.json({
        success: true,
        message: 'Code OTP envoyé à votre email'
      });

    } catch (emailError) {
      console.error('Erreur d\'envoi d\'email OTP:', emailError);
      res.status(500).json({
        success: false,
        message: 'Erreur lors de l\'envoi du code OTP'
      });
    }

  } catch (error) {
    console.error('Erreur send OTP:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de l\'envoi du code OTP'
    });
  }
};

// @desc    Vérifier le code OTP
// @route   POST /api/auth/verify-otp
// @access  Public
export const verifyOTP = async (req, res) => {
  try {
    const { email, otp } = req.body;

    if (!email || !otp) {
      return res.status(400).json({
        success: false,
        message: 'Email et code OTP requis'
      });
    }

    // Trouver l'utilisateur
    const user = await User.findOne({ email });

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Utilisateur non trouvé'
      });
    }

    // Vérifier si l'OTP est valide
    if (!user.otpCode || !user.otpExpires) {
      return res.status(400).json({
        success: false,
        message: 'Aucun code OTP actif. Veuillez en demander un nouveau.'
      });
    }

    // Vérifier si l'OTP est expiré
    if (Date.now() > user.otpExpires) {
      user.otpCode = undefined;
      user.otpExpires = undefined;
      await user.save();

      return res.status(400).json({
        success: false,
        message: 'Code OTP expiré. Veuillez en demander un nouveau.'
      });
    }

    // Vérifier le code
    if (user.otpCode !== otp) {
      return res.status(401).json({
        success: false,
        message: 'Code OTP invalide'
      });
    }

    // Code valide - effacer l'OTP et connecter l'utilisateur
    user.otpCode = undefined;
    user.otpExpires = undefined;
    user.lastLogin = new Date();
    user.loginCount = (user.loginCount || 0) + 1;
    user.emailVerified = true; // Vérifier automatiquement l'email via OTP
    await user.save();

    // Générer les tokens
    const { accessToken, refreshToken } = generateTokens(user._id);

    // Créer une session
    const ipAddress = req.ip || req.connection.remoteAddress;
    const userAgent = req.headers['user-agent'];

    await Session.create({
      userId: user._id,
      refreshToken,
      ipAddress,
      userAgent,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    });

    res.json({
      success: true,
      message: 'Authentification réussie',
      accessToken,
      refreshToken,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        fullName: user.firstName && user.lastName ? `${user.firstName} ${user.lastName}` : user.username,
        role: user.role,
        emailVerified: user.emailVerified,
        organization: user.organization,
        country: user.country
      }
    });

  } catch (error) {
    console.error('Erreur verify OTP:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la vérification du code OTP'
    });
  }
};

export default {
  register,
  login,
  refreshToken,
  logout,
  verifyEmail,
  getProfile,
  forgotPassword,
  sendOTP,
  verifyOTP
};
