#!/bin/bash
# =====================================================================
# Script d'envoi automatique vers GitHub pour Miaou 🐱🚀
# À exécuter dans ton terminal (sur Mac, ou Windows si Git est installé) !
# =====================================================================

echo "🐱 Préparation de l'envoi vers GitHub..."

# 1. Vérifier si Git est disponible
if ! command -v git &> /dev/null; then
    echo "❌ Erreur : Git n'est pas détecté."
    echo "Sur Mac, lance 'xcode-select --install' dans ton terminal pour l'activer."
    echo "Sur Windows, télécharge Git depuis : https://git-scm.com/"
    exit 1
fi

# 2. Demander l'URL du dépôt GitHub
echo "🔗 Colle l'URL de ton dépôt GitHub (ex: https://github.com/ton-pseudo/nom-du-repo.git) :"
read -r repo_url

if [ -z "$repo_url" ]; then
    echo "❌ Erreur : L'URL du dépôt est requise !"
    exit 1
fi

# 3. Initialiser le dépôt s'il ne l'est pas
if [ ! -d ".git" ]; then
    echo "📁 Initialisation du dépôt Git local..."
    git init
fi

# 4. Ajouter les fichiers (en ignorant les gros fichiers temporaires ou inutiles)
echo "➕ Ajout des fichiers au suivi Git..."
# Créer un fichier .gitignore basique s'il n'existe pas
if [ ! -f ".gitignore" ]; then
    cat <<EOF > .gitignore
__pycache__/
*.pyc
.DS_Store
Caisse.app/
Caisse.dmg
tickets/
caisse.db
EOF
fi

git add .

# 5. Création du commit
echo "💾 Création du commit local..."
git commit -m "Initial commit - Caisse Enregistreuse avec Firebase et version macOS 🐾"

# 6. Configurer la branche par défaut
git branch -M main

# 7. Ajouter le dépôt distant
git remote remove origin 2>/dev/null
git remote add origin "$repo_url"

# 8. Pousser vers GitHub
echo "🚀 Envoi du code vers GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "🎉 Félicitations Miaou 🐱 ! Ton code est maintenant en ligne sur GitHub !"
    echo "Tu peux maintenant le télécharger sur ton Mac avec : git clone $repo_url"
else
    echo "❌ Échec de l'envoi. Vérifie ton URL, ta connexion et tes accès GitHub."
fi
