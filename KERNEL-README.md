# 🌊 SETRAF - Mini Kernel OS

## Description

Le **SETRAF Mini Kernel OS** est un système de gestion de services qui lance et supervise automatiquement:

1. 🔐 **Serveur Node.js** - Authentification avec OTP (Port 5000)
2. 💧 **Application Streamlit** - Interface d'analyse ERT (Port 8504)

## 🚀 Utilisation Rapide

### Démarrer SETRAF

```bash
./start-setraf.sh
```

ou

```bash
./setraf-kernel.sh start
```

### Arrêter SETRAF

```bash
./stop-setraf.sh
```

ou

```bash
./setraf-kernel.sh stop
```

### Vérifier le statut

```bash
./setraf-kernel.sh status
```

### Redémarrer les services

```bash
./setraf-kernel.sh restart
```

### Voir les logs en temps réel

```bash
# Logs du serveur Node.js
./setraf-kernel.sh logs node

# Logs de l'application Streamlit
./setraf-kernel.sh logs streamlit

# Logs du kernel système
./setraf-kernel.sh logs kernel
```

## 📊 Services

### Serveur d'Authentification (Node.js)
- **URL**: http://172.20.31.35:5000
- **API**: `/api/auth/*` - Authentification, OTP, inscription
- **WebSocket**: Socket.IO pour connexions temps réel
- **Base de données**: MongoDB Atlas

### Application SETRAF (Streamlit)
- **URL**: http://172.20.31.35:8504
- **Fonctionnalités**:
  - 🌡️ Calculateur température Ts
  - 📊 Analyse fichiers .dat
  - 🌍 Pseudo-sections ERT 2D/3D
  - 🪨 Stratigraphie complète
  - 🔬 Inversion pyGIMLi

## 🔐 Authentification

L'application SETRAF nécessite une authentification. Trois modes sont disponibles:

1. **Connexion classique** - Email + mot de passe
2. **Inscription** - Créer un nouveau compte
3. **Connexion OTP** - Code à 6 chiffres envoyé par email (⭐ Recommandé)

### Connexion OTP

1. Entrer votre email
2. Recevoir le code OTP par email (valide 10 minutes)
3. Entrer le code à 6 chiffres
4. Accéder à l'application

## 📁 Structure des fichiers

```
SETRAF/
├── setraf-kernel.sh         # Kernel OS principal
├── start-setraf.sh          # Lancement rapide
├── stop-setraf.sh           # Arrêt rapide
├── launch_setraf.sh         # Ancien script (streamlit seul)
├── ERTest.py                # Application Streamlit
├── auth_module.py           # Module d'authentification Python
├── node-auth/               # Serveur Node.js
│   ├── server.js            # Serveur Express + Socket.IO
│   ├── routes/              # Routes API
│   ├── controllers/         # Contrôleurs (auth, OTP)
│   ├── models/              # Modèles MongoDB
│   ├── middleware/          # Middleware JWT
│   └── config/              # Configuration réseau
├── logs/                    # Logs des services
│   ├── node-auth.log
│   ├── streamlit.log
│   └── kernel.log
└── .env                     # Variables d'environnement
```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# MongoDB
MONGO_URI=mongodb+srv://...

# JWT
JWT_SECRET=...
JWT_REFRESH_SECRET=...

# Email (Gmail)
EMAIL_USER=...
EMAIL_PASS=...

# Port
PORT=5000
```

### Logs

Les logs sont stockés dans `SETRAF/logs/`:
- `node-auth.log` - Logs du serveur Node.js
- `streamlit.log` - Logs de l'application Streamlit
- `kernel.log` - Logs du kernel système

Les anciens logs sont automatiquement archivés (gardés 5 derniers).

## 🛠️ Dépannage

### Le serveur Node.js ne démarre pas

```bash
# Vérifier les logs
./setraf-kernel.sh logs node

# Vérifier que Node.js est installé
ls /mnt/c/Program\ Files/nodejs/node.exe
```

### L'application Streamlit ne démarre pas

```bash
# Vérifier les logs
./setraf-kernel.sh logs streamlit

# Vérifier Miniconda
ls ~/miniconda3
```

### Les services sont déjà lancés

```bash
# Arrêter proprement
./setraf-kernel.sh stop

# Redémarrer
./setraf-kernel.sh restart
```

### Processus zombie

```bash
# Tuer manuellement
pkill -f "node.exe server.js"
pkill -f "streamlit run"

# Supprimer les fichiers PID
rm /tmp/setraf_*.pid
```

## 📡 Accès réseau

### Depuis la machine locale
- Auth: http://localhost:5000
- App: http://localhost:8504

### Depuis le réseau local
- Auth: http://172.20.31.35:5000
- App: http://172.20.31.35:8504

### Depuis un autre appareil

Assurez-vous que:
1. Le pare-feu autorise les ports 5000 et 8504
2. L'appareil est sur le même réseau local
3. Vous utilisez l'adresse IP correcte (voir `./setraf-kernel.sh status`)

## 🎯 Fonctionnalités du Kernel

- ✅ Démarrage automatique des deux services
- ✅ Vérification des dépendances
- ✅ Gestion des processus (PID)
- ✅ Logs séparés par service
- ✅ Archivage automatique des logs
- ✅ Arrêt propre des services
- ✅ Statut en temps réel
- ✅ Supervision des processus
- ✅ Interface colorée et claire

## 📝 Notes

- Le kernel nécessite **Bash** (WSL, Linux, macOS)
- Node.js Windows est utilisé via `/mnt/c/Program Files/nodejs/node.exe` (WSL)
- Miniconda doit être installé dans `~/miniconda3`
- MongoDB Atlas est utilisé (connexion internet requise)

## 🔄 Mise à jour

```bash
# Arrêter les services
./stop-setraf.sh

# Mettre à jour le code
git pull

# Installer les nouvelles dépendances
cd node-auth && npm install

# Redémarrer
./start-setraf.sh
```

## 📜 Licence

SETRAF - © 2025 BelikanM
Apache License 2.0

---

**Auteur**: BelikanM  
**Date**: 08 Novembre 2025  
**Version**: 1.0
