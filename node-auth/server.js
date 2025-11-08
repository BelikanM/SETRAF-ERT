import express from 'express';
import mongoose from 'mongoose';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server } from 'socket.io';
import rateLimit from 'express-rate-limit';
import { getLocalIP, generateURIs, getSystemInfo } from './config/networkUtils.js';
import authRoutes from './routes/auth.js';
import userRoutes from './routes/users.js';
import { authenticate } from './middleware/auth.js';

// Charger les variables d'environnement
dotenv.config({ path: '../.env' });

const app = express();
const httpServer = createServer(app);

// Configuration WebSocket avec Socket.IO
const io = new Server(httpServer, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"],
        credentials: true
    },
    transports: ['websocket', 'polling']
});

// Détection automatique de l'IP et du port
const PORT = process.env.AUTH_PORT || 5000;
const uris = generateURIs(PORT);
const systemInfo = getSystemInfo();

// Middleware de sécurité
app.use(helmet({
    crossOriginResourcePolicy: { policy: "cross-origin" }
}));

// Configuration CORS dynamique pour toutes les IPs
app.use(cors({
    origin: function (origin, callback) {
        // Autoriser toutes les origines en développement
        callback(null, true);
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limite de 100 requêtes par IP
    message: 'Trop de requêtes depuis cette IP, veuillez réessayer plus tard.'
});

app.use('/api/auth/', limiter);

// Middleware pour parser le JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Middleware pour logger les requêtes
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${req.method} ${req.url} - IP: ${req.ip}`);
    next();
});

// Connexion à MongoDB avec URI depuis .env
const MONGODB_URI = process.env.MONGO_URI || process.env.MONGODB_URI || 'mongodb://localhost:27017/setraf_auth';

console.log('🔗 Tentative de connexion à MongoDB...');
console.log(`📊 URI: ${MONGODB_URI.replace(/\/\/([^:]+):([^@]+)@/, '//$1:****@')}`); // Masquer le mot de passe dans les logs

mongoose.connect(MONGODB_URI)
.then(() => {
    console.log('✅ Connecté à MongoDB avec succès');
    console.log(`📊 Base de données: ${mongoose.connection.name}`);
})
.catch((error) => {
    console.error('❌ Erreur de connexion MongoDB:', error.message);
    console.error('⚠️  Le serveur continuera sans MongoDB (fonctionnalités limitées)');
    // Ne pas arrêter le serveur, continuer sans MongoDB
});

// Routes
app.get('/', (req, res) => {
    res.json({
        message: '🔒 SETRAF Authentication Server',
        version: '1.0.0',
        status: 'active',
        endpoints: {
            auth: '/api/auth',
            users: '/api/users',
            health: '/api/health'
        },
        network: uris,
        system: systemInfo,
        documentation: '/api/docs'
    });
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        mongodb: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected',
        network: uris,
        system: systemInfo
    });
});

// Routes d'authentification
// Routes
app.use('/api/auth', authRoutes);
app.use('/api/users', authenticate, userRoutes);

// WebSocket - Gestion des connexions
const activeConnections = new Map();

io.on('connection', (socket) => {
    console.log(`🔌 Nouvelle connexion WebSocket: ${socket.id}`);
    
    activeConnections.set(socket.id, {
        connectedAt: new Date(),
        lastActivity: new Date(),
        ip: socket.handshake.address
    });

    // Envoi des informations réseau au client
    socket.emit('server-info', {
        uris: uris,
        system: systemInfo,
        timestamp: new Date().toISOString()
    });

    // Authentification via WebSocket
    socket.on('authenticate', async (data) => {
        try {
            const { token } = data;
            // Vérifier le token JWT ici
            socket.emit('auth-response', {
                success: true,
                message: 'Authentification réussie via WebSocket'
            });
        } catch (error) {
            socket.emit('auth-response', {
                success: false,
                message: 'Authentification échouée'
            });
        }
    });

    // Heartbeat pour maintenir la connexion
    socket.on('ping', () => {
        socket.emit('pong', {
            timestamp: new Date().toISOString(),
            serverTime: Date.now()
        });
        
        if (activeConnections.has(socket.id)) {
            activeConnections.get(socket.id).lastActivity = new Date();
        }
    });

    // Broadcast du statut d'analyse
    socket.on('analysis-update', (data) => {
        socket.broadcast.emit('analysis-status', {
            ...data,
            timestamp: new Date().toISOString()
        });
    });

    // Déconnexion
    socket.on('disconnect', (reason) => {
        console.log(`🔴 Déconnexion WebSocket: ${socket.id} - Raison: ${reason}`);
        activeConnections.delete(socket.id);
    });

    socket.on('error', (error) => {
        console.error(`❌ Erreur WebSocket: ${socket.id}`, error);
    });
});

// Route pour obtenir les statistiques WebSocket
app.get('/api/websocket/stats', authenticate, (req, res) => {
    const stats = {
        totalConnections: activeConnections.size,
        connections: Array.from(activeConnections.entries()).map(([id, info]) => ({
            id,
            ...info
        }))
    };
    res.json(stats);
});

// Gestion des erreurs 404
app.use((req, res) => {
    res.status(404).json({
        error: 'Route non trouvée',
        path: req.url,
        method: req.method
    });
});

// Gestion globale des erreurs
app.use((err, req, res, next) => {
    console.error('❌ Erreur serveur:', err);
    res.status(err.status || 500).json({
        error: err.message || 'Erreur interne du serveur',
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    });
});

// Démarrage du serveur
httpServer.listen(PORT, '0.0.0.0', () => {
    console.log('\n════════════════════════════════════════════════════════');
    console.log('🚀 SETRAF Authentication Server - DÉMARRÉ');
    console.log('════════════════════════════════════════════════════════');
    console.log(`\n📡 SERVEUR ACCESSIBLE SUR :`);
    console.log(`   - Local:   ${uris.local.http}`);
    console.log(`   - Réseau:  ${uris.network.http}`);
    console.log(`\n🔌 WEBSOCKET ACCESSIBLE SUR :`);
    console.log(`   - Local:   ${uris.local.ws}`);
    console.log(`   - Réseau:  ${uris.network.ws}`);
    console.log(`\n💻 INFORMATIONS SYSTÈME :`);
    console.log(`   - Hostname: ${systemInfo.hostname}`);
    console.log(`   - Plateforme: ${systemInfo.platform}`);
    console.log(`   - Architecture: ${systemInfo.arch}`);
    console.log(`   - CPUs: ${systemInfo.cpus}`);
    console.log(`   - Mémoire: ${systemInfo.freeMemory} / ${systemInfo.totalMemory}`);
    console.log(`\n🌐 TOUTES LES ADRESSES IP :`);
    uris.allIPs.forEach(iface => {
        const type = iface.internal ? '(interne)' : '(externe)';
        console.log(`   - ${iface.name}: ${iface.address} ${type}`);
    });
    console.log('\n════════════════════════════════════════════════════════\n');
});

// Gestion de l'arrêt propre
process.on('SIGTERM', () => {
    console.log('📴 Arrêt du serveur...');
    httpServer.close(() => {
        console.log('✅ Serveur arrêté');
        mongoose.connection.close(false, () => {
            console.log('✅ Connexion MongoDB fermée');
            process.exit(0);
        });
    });
});

export { io, activeConnections };
