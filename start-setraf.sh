#!/bin/bash

###############################################################################
# SETRAF Quick Launch - Lancement rapide et simple
###############################################################################

cd "$(dirname "$0")"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          🌊 SETRAF - Lancement Rapide                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Utiliser le kernel pour démarrer
./setraf-kernel.sh start

echo ""
echo -e "${GREEN}Pour arrêter les services, utilisez:${NC}"
echo -e "  ./setraf-kernel.sh stop"
echo ""
echo -e "${GREEN}Pour voir le statut:${NC}"
echo -e "  ./setraf-kernel.sh status"
echo ""
echo -e "${GREEN}Pour voir les logs:${NC}"
echo -e "  ./setraf-kernel.sh logs [node|streamlit|kernel]"
