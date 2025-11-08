import express from 'express';
import { authenticate } from '../middleware/auth.js';
import User from '../models/User.js';

const router = express.Router();

// @desc    Obtenir le profil utilisateur
// @route   GET /api/users/profile
// @access  Private
router.get('/profile', authenticate, async (req, res) => {
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
});

// @desc    Mettre à jour le profil utilisateur
// @route   PUT /api/users/profile
// @access  Private
router.put('/profile', authenticate, async (req, res) => {
  try {
    const { firstName, lastName, organization, country } = req.body;

    const user = await User.findById(req.userId);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Utilisateur non trouvé'
      });
    }

    // Mettre à jour les champs
    if (firstName !== undefined) user.firstName = firstName;
    if (lastName !== undefined) user.lastName = lastName;
    if (organization !== undefined) user.organization = organization;
    if (country !== undefined) user.country = country;

    await user.save();

    res.json({
      success: true,
      message: 'Profil mis à jour avec succès',
      user
    });

  } catch (error) {
    console.error('Erreur mise à jour profil:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la mise à jour du profil'
    });
  }
});

// @desc    Supprimer le compte utilisateur
// @route   DELETE /api/users/profile
// @access  Private
router.delete('/profile', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.userId);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Utilisateur non trouvé'
      });
    }

    // Désactiver le compte au lieu de le supprimer
    user.isActive = false;
    await user.save();

    res.json({
      success: true,
      message: 'Compte désactivé avec succès'
    });

  } catch (error) {
    console.error('Erreur suppression compte:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la suppression du compte'
    });
  }
});

// @desc    Obtenir les statistiques utilisateur
// @route   GET /api/users/stats
// @access  Private
router.get('/stats', authenticate, async (req, res) => {
  try {
    const user = await User.findById(req.userId);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'Utilisateur non trouvé'
      });
    }

    res.json({
      success: true,
      stats: {
        loginCount: user.loginCount || 0,
        lastLogin: user.lastLogin,
        accessCount: user.accessCount || 0,
        accountCreated: user.createdAt,
        emailVerified: user.emailVerified
      }
    });

  } catch (error) {
    console.error('Erreur statistiques:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération des statistiques'
    });
  }
});

export default router;
