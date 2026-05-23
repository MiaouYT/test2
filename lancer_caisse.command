#!/bin/bash
# =====================================================================
# Lanceur de Caisse Enregistreuse pour macOS 🐾🍏
# Double-clique sur ce fichier sur ton Mac pour lancer la caisse !
# =====================================================================

# Se déplacer dans le dossier où se trouve ce script
cd "$(dirname "$0")"

echo "🐱 Démarrage de Miaou POS (Version Python)..."

# Lancer avec python3 (la commande standard sur Mac)
python3 caisse.py
