# 🌊 SETRAF - Système Complet Opérationnel

## ✅ État du Système

### 🔐 Serveur d'Authentification (Node.js)
- **Status**: ✅ Opérationnel
- **MongoDB**: ✅ Connecté (MongoDB Atlas - myDatabase10)
- **IP WiFi**: http://192.168.1.66:5000
- **Localhost**: http://localhost:5000
- **WebSocket**: ws://192.168.1.66:5000
- **Plateforme**: Windows (via WSL)

### 💧 Application SETRAF (Streamlit)
- **Status**: ✅ Opérationnel
- **URL Locale**: http://localhost:8504
- **URL Réseau**: http://172.20.31.35:8504
- **Environnement**: gestmodo (Python 3.10)
- **Authentification**: ✅ Intégrée

## 🚀 Démarrage Rapide

```bash
# Démarrer tout le système
cd /home/belikan/KIbalione8/SETRAF
./start-setraf.sh

# Arrêter le système
./stop-setraf.sh

# Voir le statut
./setraf-kernel.sh status

# Voir les logs
./setraf-kernel.sh logs node      # Logs Node.js
./setraf-kernel.sh logs streamlit # Logs Streamlit
```

## 🔧 Configuration

### Auto-détection IP
Le système détecte automatiquement:
- **IP WiFi** pour Node.js: 192.168.1.66
- **IP WSL** pour Streamlit: 172.20.31.35
- **Fallback**: localhost

### MongoDB Atlas
- **URI**: mongodb+srv://SETRAF:***@cluster0.5tjz9v0.mongodb.net/myDatabase10
- **Base**: myDatabase10
- **Collections**: users, sessions

### Environnement Python
- **Environnement**: gestmodo
- **Python**: 3.10
- **Dépendances**: streamlit, pandas, numpy, matplotlib, pygimli, etc.

## 🔐 Authentification

### Modes de connexion

1. **Email + Mot de passe**
   - Connexion classique
   - Sessions JWT (15 min + refresh 7 jours)

2. **OTP (One-Time Password)** ⭐ Recommandé
   - Code à 6 chiffres envoyé par email
   - Valide 10 minutes
   - Email vérifié automatiquement

3. **Inscription**
   - Création de nouveau compte
   - Email de vérification
   - Validation des données

### Fonctionnalités Auth

- ✅ JWT Access Token (15 minutes)
- ✅ JWT Refresh Token (7 jours)
- ✅ OTP par email
- ✅ Réinitialisation mot de passe
- ✅ Vérification email
- ✅ Rate limiting (100 req/15min)
- ✅ WebSocket pour temps réel
- ✅ Sessions persistantes MongoDB
- ✅ Protection compte (5 tentatives max)

## 🌐 URLs d'Accès

### Depuis la machine locale
```
Auth API:  http://localhost:5000
App:       http://localhost:8504
```

### Depuis le réseau WiFi
```
Auth API:  http://192.168.1.66:5000
App:       http://192.168.1.66:8504  (ou 172.20.31.35:8504)
```

### API Endpoints
```
GET  /                    - Info serveur
GET  /api/health          - Santé du système
POST /api/auth/register   - Inscription
POST /api/auth/login      - Connexion
POST /api/auth/send-otp   - Envoyer OTP
POST /api/auth/verify-otp - Vérifier OTP
POST /api/auth/refresh    - Rafraîchir token
POST /api/auth/logout     - Déconnexion
GET  /api/auth/me         - Profil utilisateur
GET  /api/users/profile   - Détails profil
GET  /api/users/stats     - Statistiques
```

## 📊 Architecture

```
SETRAF/
├── setraf-kernel.sh           # Kernel OS - Gestionnaire principal
├── start-setraf.sh            # Démarrage rapide
├── stop-setraf.sh             # Arrêt rapide
├── ERTest.py                  # Application Streamlit principale
├── auth_module.py             # Module d'auth Python
├── .env                       # Variables d'environnement
│
├── node-auth/                 # Backend Node.js
│   ├── server.js              # Serveur Express + Socket.IO
│   ├── routes/                # Routes API
│   │   ├── auth.js            # Auth routes
│   │   └── users.js           # User routes
│   ├── controllers/           # Contrôleurs
│   │   └── authController.js  # Login, OTP, Register
│   ├── models/                # Modèles MongoDB
│   │   ├── User.js            # Modèle utilisateur
│   │   └── Session.js         # Modèle session
│   ├── middleware/            # Middleware
│   │   └── auth.js            # JWT verification
│   ├── config/                # Configuration
│   │   ├── networkUtils.js    # Auto-détection IP
│   │   └── database.js        # Config MongoDB
│   ├── .env                   # Config locale
│   └── package.json           # Dépendances npm
│
└── logs/                      # Logs système
    ├── kernel.log             # Logs kernel
    ├── node-auth.log          # Logs Node.js
    └── streamlit.log          # Logs Streamlit
```

## 🔍 Vérifications

### Tester le serveur Node.js
```bash
curl http://192.168.1.66:5000/api/health
```

### Tester l'inscription
```bash
curl -X POST http://192.168.1.66:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234",
    "fullName": "Test User"
  }'
```

### Tester l'OTP
```bash
# Envoyer OTP
curl -X POST http://192.168.1.66:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Vérifier OTP
curl -X POST http://192.168.1.66:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'
```

## 🛠️ Dépannage

### MongoDB non connecté
```bash
# Vérifier l'URI dans .env
cat /home/belikan/KIbalione8/SETRAF/.env | grep MONGO_URI

# Voir les logs
./setraf-kernel.sh logs node | grep -i mongo
```

### Serveur Node.js ne répond pas
```bash
# Vérifier les processus
ps aux | grep node.exe

# Tuer les processus
pkill -f "node.exe server.js"

# Redémarrer
./setraf-kernel.sh restart
```

### Streamlit erreur import
```bash
# Vérifier l'environnement
~/miniconda3/envs/gestmodo/bin/python --version

# Voir les logs
./setraf-kernel.sh logs streamlit | tail -50
```

### IP incorrecte
```bash
# Détecter l'IP
hostname -I
ip route get 1.1.1.1 | grep -oP 'src \K\S+'

# Le kernel détecte automatiquement au démarrage
```

## 📝 Logs

Les logs sont automatiquement gérés:
- Rotation automatique (garde les 5 derniers)
- Timestamps sur chaque entrée
- Séparation par service

```bash
# Voir tous les logs
tail -f logs/kernel.log
tail -f logs/node-auth.log
tail -f logs/streamlit.log

# Ou via le kernel
./setraf-kernel.sh logs kernel
./setraf-kernel.sh logs node
./setraf-kernel.sh logs streamlit
```

## 🔐 Sécurité

- ✅ JWT avec secrets séparés (access + refresh)
- ✅ Rate limiting (100 requêtes/15min)
- ✅ Helmet.js (headers sécurisés)
- ✅ CORS configuré
- ✅ Mots de passe hashés (bcrypt)
- ✅ OTP à usage unique (10 min)
- ✅ Protection compte (5 tentatives)
- ✅ Email vérifié requis
- ✅ Sessions MongoDB persistantes
- ✅ Tokens expirables

## 📈 Performances

- **Node.js**: 24 CPUs, 31 GB RAM disponible
- **MongoDB**: Atlas (Cloud, auto-scaling)
- **Streamlit**: Python 3.10, gestmodo optimisé
- **WebSocket**: Socket.IO avec polling fallback

## 🎯 Prochaines étapes

1. ✅ Système opérationnel
2. ✅ Auth complète avec OTP
3. ✅ MongoDB connecté
4. ✅ Auto-détection IP
5. ⏳ Interface utilisateur auth dans Streamlit
6. ⏳ Tests end-to-end
7. ⏳ Documentation utilisateur

---

**Dernière mise à jour**: 08 Novembre 2025  
**Version**: 1.0.0  
**Auteur**: BelikanM  
**Statut**: ✅ Production Ready
