import os from 'os';
import ip from 'ip';

/**
 * Détecte automatiquement l'adresse IP de l'appareil
 * Compatible avec toutes les plateformes (Windows, Linux, macOS)
 */
export function getLocalIP() {
    try {
        // Méthode 1: Utiliser le module 'ip'
        const localIP = ip.address();
        if (localIP && localIP !== '127.0.0.1') {
            return localIP;
        }

        // Méthode 2: Parcourir les interfaces réseau
        const interfaces = os.networkInterfaces();
        
        for (const name of Object.keys(interfaces)) {
            for (const iface of interfaces[name]) {
                // Ignorer les interfaces internes et IPv6
                if (iface.family === 'IPv4' && !iface.internal) {
                    return iface.address;
                }
            }
        }

        // Fallback: localhost
        return '127.0.0.1';
    } catch (error) {
        console.error('Erreur détection IP:', error);
        return '127.0.0.1';
    }
}

/**
 * Obtient toutes les adresses IP disponibles
 */
export function getAllIPs() {
    const ips = [];
    const interfaces = os.networkInterfaces();
    
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (iface.family === 'IPv4') {
                ips.push({
                    name: name,
                    address: iface.address,
                    internal: iface.internal,
                    mac: iface.mac
                });
            }
        }
    }
    
    return ips;
}

/**
 * Obtient les informations système
 */
export function getSystemInfo() {
    return {
        hostname: os.hostname(),
        platform: os.platform(),
        arch: os.arch(),
        cpus: os.cpus().length,
        totalMemory: Math.round(os.totalmem() / (1024 ** 3)) + ' GB',
        freeMemory: Math.round(os.freemem() / (1024 ** 3)) + ' GB',
        uptime: Math.round(os.uptime() / 3600) + ' heures'
    };
}

/**
 * Génère les URIs pour HTTP et WebSocket
 */
export function generateURIs(port = 5000) {
    const localIP = getLocalIP();
    
    return {
        local: {
            http: `http://localhost:${port}`,
            ws: `ws://localhost:${port}`
        },
        network: {
            http: `http://${localIP}:${port}`,
            ws: `ws://${localIP}:${port}`
        },
        ip: localIP,
        allIPs: getAllIPs()
    };
}

export default {
    getLocalIP,
    getAllIPs,
    getSystemInfo,
    generateURIs
};
