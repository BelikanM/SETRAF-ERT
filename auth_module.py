"""
Module d'authentification pour SETRAF ERTest.py
Intégration avec le backend Node.js et système OTP
"""

import streamlit as st
import requests
import json
import socket
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('/home/belikan/KIbalione8/SETRAF/.env')

def get_local_ip():
    """Détecte automatiquement l'adresse IP locale"""
    try:
        # Méthode 1: Créer une socket pour obtenir l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Méthode 2: Utiliser hostname
            return socket.gethostbyname(socket.gethostname())
        except:
            # Fallback
            return "172.20.31.35"

# Détection automatique de l'IP
LOCAL_IP = get_local_ip()

# Configuration de l'API backend avec IP auto-détectée
BACKEND_URL = f"http://{LOCAL_IP}:{os.getenv('PORT', '5000')}/api"
LOCAL_BACKEND = f"http://localhost:{os.getenv('PORT', '5000')}/api"

class AuthManager:
    """Gestionnaire d'authentification avec OTP"""
    
    def __init__(self):
        # Initialiser les states de session
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        if 'refresh_token' not in st.session_state:
            st.session_state.refresh_token = None
        if 'otp_sent' not in st.session_state:
            st.session_state.otp_sent = False
        if 'otp_email' not in st.session_state:
            st.session_state.otp_email = None
        if 'otp_expiry' not in st.session_state:
            st.session_state.otp_expiry = None
    
    def _get_backend_url(self):
        """Détermine l'URL backend appropriée avec fallback sur plusieurs IPs"""
        # Liste des IPs à tester
        ips_to_try = [
            "192.168.1.66",  # IP WiFi détectée
            LOCAL_IP,         # IP auto-détectée
            "172.20.31.35",   # IP WSL
            "localhost"       # Fallback final
        ]
        
        port = os.getenv('PORT', '5000')
        
        for ip in ips_to_try:
            try:
                url = f"http://{ip}:{port}/api"
                response = requests.get(f"{url.replace('/api', '')}/api/health", timeout=1)
                if response.status_code == 200:
                    return url
            except:
                continue
        
        # Fallback par défaut
        return f"http://localhost:{port}/api"
    
    def register(self, username, email, password, full_name, organization=""):
        """Inscription d'un nouvel utilisateur"""
        try:
            backend = self._get_backend_url()
            response = requests.post(
                f"{backend}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "fullName": full_name,
                    "organization": organization
                },
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                return True, data.get('message', 'Inscription réussie')
            else:
                error = response.json()
                return False, error.get('message', 'Erreur d\'inscription')
                
        except requests.exceptions.RequestException as e:
            return False, f"Erreur de connexion au serveur: {str(e)}"
    
    def login(self, email, password):
        """Connexion avec email et mot de passe"""
        try:
            backend = self._get_backend_url()
            response = requests.post(
                f"{backend}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.authenticated = True
                st.session_state.user = data['user']
                st.session_state.access_token = data['accessToken']
                st.session_state.refresh_token = data['refreshToken']
                return True, "Connexion réussie!"
            else:
                error = response.json()
                return False, error.get('message', 'Identifiants invalides')
                
        except requests.exceptions.RequestException as e:
            return False, f"Erreur de connexion au serveur: {str(e)}"
    
    def send_otp(self, email):
        """Envoyer un code OTP par email"""
        try:
            backend = self._get_backend_url()
            response = requests.post(
                f"{backend}/auth/send-otp",
                json={"email": email},
                timeout=10
            )
            
            if response.status_code == 200:
                st.session_state.otp_sent = True
                st.session_state.otp_email = email
                st.session_state.otp_expiry = datetime.now() + timedelta(minutes=10)
                return True, "Code OTP envoyé à votre email"
            else:
                error = response.json()
                return False, error.get('message', 'Erreur lors de l\'envoi du OTP')
                
        except requests.exceptions.RequestException as e:
            return False, f"Erreur de connexion au serveur: {str(e)}"
    
    def verify_otp(self, email, otp_code):
        """Vérifier le code OTP"""
        try:
            backend = self._get_backend_url()
            response = requests.post(
                f"{backend}/auth/verify-otp",
                json={
                    "email": email,
                    "otp": otp_code
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.authenticated = True
                st.session_state.user = data['user']
                st.session_state.access_token = data['accessToken']
                st.session_state.refresh_token = data['refreshToken']
                st.session_state.otp_sent = False
                st.session_state.otp_email = None
                return True, "Authentification réussie!"
            else:
                error = response.json()
                return False, error.get('message', 'Code OTP invalide')
                
        except requests.exceptions.RequestException as e:
            return False, f"Erreur de connexion au serveur: {str(e)}"
    
    def logout(self):
        """Déconnexion"""
        try:
            if st.session_state.refresh_token:
                backend = self._get_backend_url()
                requests.post(
                    f"{backend}/auth/logout",
                    headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    json={"refreshToken": st.session_state.refresh_token},
                    timeout=5
                )
        except:
            pass
        
        # Réinitialiser les états
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.otp_sent = False
        st.session_state.otp_email = None
        st.session_state.otp_expiry = None
    
    def refresh_access_token(self):
        """Rafraîchir le token d'accès"""
        try:
            if not st.session_state.refresh_token:
                return False
                
            backend = self._get_backend_url()
            response = requests.post(
                f"{backend}/auth/refresh",
                json={"refreshToken": st.session_state.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data['accessToken']
                return True
            else:
                self.logout()
                return False
                
        except:
            self.logout()
            return False
    
    def is_authenticated(self):
        """Vérifier si l'utilisateur est authentifié"""
        return st.session_state.authenticated

def show_auth_ui():
    """Affiche l'interface d'authentification"""
    auth = AuthManager()
    
    # Style CSS
    st.markdown("""
    <style>
    .auth-container {
        max-width: 500px;
        margin: 50px auto;
        padding: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .auth-title {
        color: white;
        text-align: center;
        font-size: 32px;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stButton>button {
        width: 100%;
        background: white;
        color: #667eea;
        font-weight: bold;
        border: none;
        padding: 12px;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .otp-info {
        background: rgba(255,255,255,0.2);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🔐 SETRAF - Authentification</div>', unsafe_allow_html=True)
    
    # Tabs pour Login / Register / OTP
    auth_tab = st.radio(
        "Mode d'authentification",
        ["🔑 Connexion", "📝 Inscription", "📱 Connexion OTP"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if auth_tab == "🔑 Connexion":
        st.markdown("### Connexion")
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="votre.email@example.com")
            password = st.text_input("🔒 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                if email and password:
                    with st.spinner("Connexion en cours..."):
                        success, message = auth.login(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Veuillez remplir tous les champs")
    
    elif auth_tab == "📝 Inscription":
        st.markdown("### Créer un compte")
        with st.form("register_form"):
            username = st.text_input("👤 Nom d'utilisateur", placeholder="username")
            email = st.text_input("📧 Email", placeholder="votre.email@example.com")
            full_name = st.text_input("📛 Nom complet", placeholder="Prénom Nom")
            organization = st.text_input("🏢 Organisation (optionnel)", placeholder="Université, Entreprise...")
            password = st.text_input("🔒 Mot de passe", type="password", 
                                    help="Min 6 caractères, 1 majuscule, 1 minuscule, 1 chiffre")
            password_confirm = st.text_input("🔒 Confirmer le mot de passe", type="password")
            submit = st.form_submit_button("S'inscrire")
            
            if submit:
                if not all([username, email, full_name, password, password_confirm]):
                    st.warning("Veuillez remplir tous les champs obligatoires")
                elif password != password_confirm:
                    st.error("Les mots de passe ne correspondent pas")
                elif len(password) < 6:
                    st.error("Le mot de passe doit contenir au moins 6 caractères")
                else:
                    with st.spinner("Inscription en cours..."):
                        success, message = auth.register(username, email, password, full_name, organization)
                        if success:
                            st.success(message)
                            st.info("Vérifiez votre email pour activer votre compte")
                        else:
                            st.error(message)
    
    elif auth_tab == "📱 Connexion OTP":
        st.markdown("### Authentification par OTP")
        
        if not st.session_state.otp_sent:
            # Formulaire pour demander l'OTP
            with st.form("otp_request_form"):
                email = st.text_input("📧 Email", placeholder="votre.email@example.com")
                submit = st.form_submit_button("Envoyer le code OTP")
                
                if submit:
                    if email:
                        with st.spinner("Envoi du code OTP..."):
                            success, message = auth.send_otp(email)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Veuillez entrer votre email")
        else:
            # Formulaire pour vérifier l'OTP
            st.markdown(f"""
            <div class="otp-info">
                ✉️ Code envoyé à: <strong>{st.session_state.otp_email}</strong><br>
                ⏰ Expire dans: <strong>10 minutes</strong>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("otp_verify_form"):
                otp_code = st.text_input("🔢 Code OTP (6 chiffres)", max_chars=6, placeholder="123456")
                col1, col2 = st.columns(2)
                with col1:
                    verify = st.form_submit_button("Vérifier")
                with col2:
                    resend = st.form_submit_button("Renvoyer")
                
                if verify:
                    if otp_code and len(otp_code) == 6:
                        with st.spinner("Vérification..."):
                            success, message = auth.verify_otp(st.session_state.otp_email, otp_code)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.warning("Veuillez entrer un code à 6 chiffres")
                
                if resend:
                    st.session_state.otp_sent = False
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def require_auth(func):
    """Décorateur pour protéger les fonctions nécessitant une authentification"""
    def wrapper(*args, **kwargs):
        auth = AuthManager()
        if not auth.is_authenticated():
            show_auth_ui()
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def show_user_info():
    """Affiche les informations de l'utilisateur connecté"""
    if st.session_state.authenticated and st.session_state.user:
        user = st.session_state.user
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Utilisateur connecté")
            st.markdown(f"**Nom:** {user.get('fullName', user.get('username'))}")
            st.markdown(f"**Email:** {user.get('email')}")
            if user.get('organization'):
                st.markdown(f"**Organisation:** {user.get('organization')}")
            st.markdown(f"**Rôle:** {user.get('role', 'user').upper()}")
            
            if st.button("🚪 Se déconnecter", use_container_width=True):
                AuthManager().logout()
                st.success("Déconnexion réussie")
                st.rerun()
