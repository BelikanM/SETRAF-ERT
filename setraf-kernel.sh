#!/bin/bash

###############################################################################
# SETRAF Mini Kernel OS - Gestionnaire de services
# Lance et supervise le serveur Node.js (authentification) et Streamlit
###############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NODE_AUTH_DIR="$SCRIPT_DIR/node-auth"
STREAMLIT_APP="$SCRIPT_DIR/ERTest.py"
NODE_EXEC="/mnt/c/Program Files/nodejs/node.exe"
CONDA_BASE="/home/belikan/miniconda3"
CONDA_ENV="gestmodo"  # Environnement avec toutes les dépendances installées

# Fichiers PID
NODE_PID_FILE="/tmp/setraf_node.pid"
STREAMLIT_PID_FILE="/tmp/setraf_streamlit.pid"

# Logs
LOG_DIR="$SCRIPT_DIR/logs"
NODE_LOG="$LOG_DIR/node-auth.log"
STREAMLIT_LOG="$LOG_DIR/streamlit.log"
KERNEL_LOG="$LOG_DIR/kernel.log"

###############################################################################
# Fonctions utilitaires
###############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$KERNEL_LOG"
}

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║          🌊 SETRAF Mini Kernel OS v1.0                       ║"
    echo "║          Subaquifère ERT Analysis Platform                    ║"
    echo "║                                                               ║"
    echo "║          Services: Node.js Auth + Streamlit App              ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    log "INFO" "Vérification des dépendances..."
    
    # Vérifier Node.js
    if [ ! -f "$NODE_EXEC" ]; then
        log "ERROR" "Node.js non trouvé: $NODE_EXEC"
        echo -e "${RED}❌ Node.js non installé${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js trouvé${NC}"
    
    # Vérifier Python/Conda
    if [ ! -d "$CONDA_BASE" ]; then
        log "ERROR" "Miniconda non trouvé: $CONDA_BASE"
        echo -e "${RED}❌ Miniconda non installé${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Miniconda trouvé${NC}"
    
    # Vérifier l'environnement gestmodo
    if [ ! -d "$CONDA_BASE/envs/$CONDA_ENV" ]; then
        log "ERROR" "Environnement conda '$CONDA_ENV' non trouvé"
        echo -e "${RED}❌ Environnement '$CONDA_ENV' non trouvé${NC}"
        echo -e "${YELLOW}Créez-le avec: conda create -n $CONDA_ENV python=3.10${NC}"
        echo -e "${YELLOW}Puis installez: conda activate $CONDA_ENV && pip install -r requirements.txt${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Environnement conda '$CONDA_ENV' trouvé${NC}"
    
    # Vérifier les fichiers
    if [ ! -f "$STREAMLIT_APP" ]; then
        log "ERROR" "Application Streamlit non trouvée: $STREAMLIT_APP"
        echo -e "${RED}❌ ERTest.py non trouvé${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Application Streamlit trouvée${NC}"
    
    if [ ! -d "$NODE_AUTH_DIR" ]; then
        log "ERROR" "Dossier Node.js Auth non trouvé: $NODE_AUTH_DIR"
        echo -e "${RED}❌ node-auth/ non trouvé${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Serveur d'authentification trouvé${NC}"
}

setup_environment() {
    log "INFO" "Configuration de l'environnement..."
    
    # Créer le dossier de logs
    mkdir -p "$LOG_DIR"
    echo -e "${GREEN}✓ Dossier de logs créé${NC}"
    
    # Nettoyer les anciens logs (garder les 5 derniers)
    cd "$LOG_DIR"
    ls -t kernel.log.* 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    
    # Archiver le log actuel s'il existe
    if [ -f "$KERNEL_LOG" ]; then
        mv "$KERNEL_LOG" "$KERNEL_LOG.$(date +%Y%m%d_%H%M%S)"
    fi
}

start_node_server() {
    log "INFO" "Démarrage du serveur Node.js (Authentification)..."
    echo -e "${YELLOW}🚀 Lancement du serveur d'authentification...${NC}"
    
    cd "$NODE_AUTH_DIR"
    
    # Démarrer Node.js en arrière-plan
    nohup "$NODE_EXEC" server.js > "$NODE_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$NODE_PID_FILE"
    
    # Attendre que le serveur démarre
    sleep 3
    
    # Vérifier si le processus tourne
    if ps -p $pid > /dev/null 2>&1; then
        log "INFO" "Serveur Node.js démarré (PID: $pid)"
        echo -e "${GREEN}✓ Serveur Node.js démarré sur http://172.20.31.35:5000${NC}"
        return 0
    else
        log "ERROR" "Échec du démarrage du serveur Node.js"
        echo -e "${RED}❌ Échec du démarrage du serveur Node.js${NC}"
        cat "$NODE_LOG"
        return 1
    fi
}

start_streamlit_server() {
    log "INFO" "Démarrage du serveur Streamlit..."
    echo -e "${YELLOW}🚀 Lancement de l'application Streamlit...${NC}"
    
    cd "$SCRIPT_DIR"
    
    # Définir les chemins de l'environnement gestmodo
    local GESTMODO_PYTHON="$CONDA_BASE/envs/$CONDA_ENV/bin/python"
    local GESTMODO_STREAMLIT="$CONDA_BASE/envs/$CONDA_ENV/bin/streamlit"
    
    # Vérifier que Python existe dans gestmodo
    if [ ! -f "$GESTMODO_PYTHON" ]; then
        log "ERROR" "Python non trouvé dans l'environnement $CONDA_ENV: $GESTMODO_PYTHON"
        echo -e "${RED}❌ Python non trouvé dans gestmodo${NC}"
        return 1
    fi
    
    # Vérifier que streamlit est installé
    if ! $GESTMODO_PYTHON -m streamlit --version &>/dev/null; then
        log "WARN" "Streamlit non trouvé, installation..."
        echo -e "${YELLOW}⚠️  Installation de Streamlit dans gestmodo...${NC}"
        $GESTMODO_PYTHON -m pip install streamlit -q
    fi
    
    # Arrêter les instances Streamlit existantes
    pkill -9 -f "streamlit run" 2>/dev/null || true
    sleep 2
    
    # Démarrer Streamlit avec l'environnement gestmodo
    nohup $GESTMODO_PYTHON -m streamlit run "$STREAMLIT_APP" --server.port=8504 --server.address=0.0.0.0 > "$STREAMLIT_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$STREAMLIT_PID_FILE"
    
    # Attendre que le serveur démarre
    sleep 5
    
    # Vérifier si le processus tourne
    if ps -p $pid > /dev/null 2>&1; then
        log "INFO" "Serveur Streamlit démarré (PID: $pid)"
        echo -e "${GREEN}✓ Application Streamlit démarrée sur http://172.20.31.35:8504${NC}"
        return 0
    else
        log "ERROR" "Échec du démarrage de Streamlit"
        echo -e "${RED}❌ Échec du démarrage de Streamlit${NC}"
        tail -20 "$STREAMLIT_LOG"
        return 1
    fi
}

stop_services() {
    log "INFO" "Arrêt des services..."
    echo -e "${YELLOW}🛑 Arrêt des services SETRAF...${NC}"
    
    # Arrêter Node.js
    if [ -f "$NODE_PID_FILE" ]; then
        local node_pid=$(cat "$NODE_PID_FILE")
        if ps -p $node_pid > /dev/null 2>&1; then
            kill $node_pid 2>/dev/null || true
            log "INFO" "Serveur Node.js arrêté (PID: $node_pid)"
            echo -e "${GREEN}✓ Serveur Node.js arrêté${NC}"
        fi
        rm -f "$NODE_PID_FILE"
    fi
    
    # Arrêter Streamlit
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        local streamlit_pid=$(cat "$STREAMLIT_PID_FILE")
        if ps -p $streamlit_pid > /dev/null 2>&1; then
            kill $streamlit_pid 2>/dev/null || true
            log "INFO" "Serveur Streamlit arrêté (PID: $streamlit_pid)"
            echo -e "${GREEN}✓ Application Streamlit arrêtée${NC}"
        fi
        rm -f "$STREAMLIT_PID_FILE"
    fi
    
    # Tuer tous les processus restants
    pkill -f "node.exe server.js" 2>/dev/null || true
    pkill -f "streamlit run" 2>/dev/null || true
}

status_services() {
    echo -e "${CYAN}📊 Statut des services SETRAF${NC}"
    echo ""
    
    # Statut Node.js
    if [ -f "$NODE_PID_FILE" ]; then
        local node_pid=$(cat "$NODE_PID_FILE")
        if ps -p $node_pid > /dev/null 2>&1; then
            echo -e "${GREEN}● Node.js Auth Server${NC}"
            echo -e "  Status: ${GREEN}Running${NC} (PID: $node_pid)"
            echo -e "  URL: http://172.20.31.35:5000"
            echo -e "  Log: $NODE_LOG"
        else
            echo -e "${RED}● Node.js Auth Server${NC}"
            echo -e "  Status: ${RED}Stopped${NC}"
        fi
    else
        echo -e "${RED}● Node.js Auth Server${NC}"
        echo -e "  Status: ${RED}Not started${NC}"
    fi
    
    echo ""
    
    # Statut Streamlit
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        local streamlit_pid=$(cat "$STREAMLIT_PID_FILE")
        if ps -p $streamlit_pid > /dev/null 2>&1; then
            echo -e "${GREEN}● Streamlit App${NC}"
            echo -e "  Status: ${GREEN}Running${NC} (PID: $streamlit_pid)"
            echo -e "  URL: http://172.20.31.35:8504"
            echo -e "  Log: $STREAMLIT_LOG"
        else
            echo -e "${RED}● Streamlit App${NC}"
            echo -e "  Status: ${RED}Stopped${NC}"
        fi
    else
        echo -e "${RED}● Streamlit App${NC}"
        echo -e "  Status: ${RED}Not started${NC}"
    fi
}

restart_services() {
    log "INFO" "Redémarrage des services..."
    stop_services
    sleep 2
    start_services
}

start_services() {
    print_banner
    check_dependencies
    setup_environment
    
    echo ""
    log "INFO" "Démarrage du système SETRAF..."
    
    # Détecter l'adresse IP automatiquement
    log "INFO" "Détection de l'adresse IP..."
    local LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "127.0.0.1")
    if [ -z "$LOCAL_IP" ] || [ "$LOCAL_IP" = "127.0.0.1" ]; then
        # Fallback pour WSL/Windows
        LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' || echo "172.20.31.35")
    fi
    echo -e "${GREEN}✓ Adresse IP détectée: $LOCAL_IP${NC}"
    log "INFO" "IP détectée: $LOCAL_IP"
    
    # Démarrer Node.js
    if ! start_node_server; then
        log "ERROR" "Impossible de démarrer le serveur Node.js"
        exit 1
    fi
    
    echo ""
    
    # Démarrer Streamlit
    if ! start_streamlit_server; then
        log "ERROR" "Impossible de démarrer Streamlit"
        stop_services
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║  ✅ Système SETRAF démarré avec succès !                     ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║  🔐 Authentification: http://$LOCAL_IP:5000              ║${NC}"
    echo -e "${GREEN}║  💧 Application SETRAF: http://$LOCAL_IP:8504            ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║  📝 Logs: $LOG_DIR                        ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}💡 Accès depuis le réseau local:${NC}"
    echo -e "   - Auth: http://$LOCAL_IP:5000"
    echo -e "   - App:  http://$LOCAL_IP:8504"
    echo -e "   - Localhost: http://localhost:8504"
    echo ""
    log "INFO" "Système SETRAF opérationnel sur $LOCAL_IP"
}

show_logs() {
    local service=$1
    case $service in
        node|auth)
            echo -e "${CYAN}📄 Logs Node.js Auth Server:${NC}"
            tail -f "$NODE_LOG"
            ;;
        streamlit|app)
            echo -e "${CYAN}📄 Logs Streamlit App:${NC}"
            tail -f "$STREAMLIT_LOG"
            ;;
        kernel|system)
            echo -e "${CYAN}📄 Logs Kernel:${NC}"
            tail -f "$KERNEL_LOG"
            ;;
        *)
            echo -e "${RED}Service inconnu. Utilisez: node, streamlit, ou kernel${NC}"
            ;;
    esac
}

###############################################################################
# Menu principal
###############################################################################

case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        status_services
        ;;
    logs)
        show_logs "${2:-kernel}"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [node|streamlit|kernel]}"
        exit 1
        ;;
esac
