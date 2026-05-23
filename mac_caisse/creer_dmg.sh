#!/bin/bash
# =====================================================================
# Script de compilation et packaging DMG pour Miaou 🐱🍏
# À exécuter sur ton Mac pour générer le fichier Caisse.dmg !
# =====================================================================

echo "🍏 Démarrage de la création de l'application macOS..."

# 1. Nettoyage des anciennes builds
rm -rf Caisse.app
rm -f Caisse.dmg

# 2. Création de la structure du bundle .app macOS
echo "📁 Création du dossier d'application..."
mkdir -p Caisse.app/Contents/MacOS
mkdir -p Caisse.app/Contents/Resources

# 3. Création du fichier de configuration Info.plist
echo "📝 Génération du fichier de configuration Info.plist..."
cat <<EOF > Caisse.app/Contents/Info.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Caisse</string>
    <key>CFBundleIdentifier</key>
    <string>com.miaou.Caisse</string>
    <key>CFBundleName</key>
    <string>Caisse</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# 4. Compilation des fichiers Swift avec le compilateur natif swiftc de macOS
echo "🔨 Compilation des sources Swift..."
SDK_PATH=$(xcrun --show-sdk-path --sdk macosx 2>/dev/null)

if [ -z "$SDK_PATH" ]; then
    echo "❌ Erreur : Xcode Command Line Tools non installés sur ton Mac !"
    echo "Lance la commande 'xcode-select --install' dans ton terminal Mac pour les installer."
    exit 1
fi

swiftc -sdk "$SDK_PATH" CaisseApp.swift ContentView.swift FirebaseManager.swift Models.swift Theme.swift -o Caisse.app/Contents/MacOS/Caisse

if [ $? -eq 0 ]; then
    echo "✅ Compilation Swift réussie !"
else
    echo "❌ Échec de la compilation Swift."
    exit 1
fi

# 5. Création du fichier DMG via l'utilitaire natif hdiutil de macOS
echo "📦 Packaging en Caisse.dmg..."
hdiutil create -volname "Caisse Enregistreuse 🐾" -srcfolder Caisse.app -ov -format UDZO Caisse.dmg

if [ $? -eq 0 ]; then
    echo "🎉 Félicitations Miaou 🐱 ! Caisse.dmg a été créé avec succès !"
    echo "Double-clique sur Caisse.dmg dans le dossier pour installer l'application sur ton Mac."
    # Nettoyage
    rm -rf Caisse.app
else
    echo "❌ Échec du packaging DMG."
    exit 1
fi
EOF
