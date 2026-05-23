# Caisse Enregistreuse Moderne pour macOS 🐾🍏

Salut Miaou 🐱 ! Voici tous les fichiers nécessaires pour faire tourner ta superbe caisse enregistreuse directement sur ton Mac, connectée en temps réel à ta base de données **Firebase Realtime Database** !

---

## 📂 Contenu du dossier

Ce dossier contient 5 fichiers Swift à importer dans Xcode :
1. **`CaisseApp.swift`** : Le point d'entrée de l'application macOS.
2. **`ContentView.swift`** : Tous les écrans de l'application (Login, Ventes, Admin, Historique).
3. **`FirebaseManager.swift`** : Le gestionnaire réseau pour parler en temps réel à Firebase.
4. **`Models.swift`** : Les modèles de données (utilisateurs, produits, ventes) partagés avec Firebase.
5. **`Theme.swift`** : Les définitions esthétiques (couleurs Dark Premium).

---

## 🚀 Comment lancer l'application sur ton Mac (en 2 minutes !)

Suis ces étapes simples avec Xcode sur ton Mac :

### Étape 1 : Créer le projet dans Xcode
1. Lance **Xcode** sur ton Mac.
2. Sélectionne **Create a new Xcode project**.
3. Choisis l'onglet **macOS** en haut, sélectionne **App** et clique sur **Next**.
4. Remplis les informations du projet :
   - **Product Name** : `Caisse`
   - **Interface** : `SwiftUI` (Très important !)
   - **Language** : `Swift`
5. Clique sur **Next**, choisis où sauvegarder le projet sur ton Mac, puis clique sur **Create**.

### Étape 2 : Importer les fichiers
1. Dans la barre de navigation gauche de Xcode, supprime les fichiers par défaut suivants (fais un clic droit > *Delete* > *Move to Trash*) :
   - `CaisseApp.swift`
   - `ContentView.swift`
2. Glisse et dépose les 5 fichiers de ce dossier (`CaisseApp.swift`, `ContentView.swift`, `FirebaseManager.swift`, `Models.swift`, `Theme.swift`) directement dans le dossier jaune de ton projet dans la barre latérale de Xcode.
3. Coche la case **Copy items if needed** si Xcode te le demande, puis clique sur **Finish**.

### Étape 3 : Lancer l'application !
1. Clique sur le bouton de **Lecture (Play)** tout en haut à gauche de Xcode, ou appuie sur le raccourci **Command ⌘ + R**.
2. **Et voilà !** L'application caisse enregistreuse s'ouvre sur ton Mac avec le magnifique thème Dark Premium ! ⚡🎨

---

## 📦 Créer un fichier `.dmg` d'installation en 1 clic !

Si tu veux créer un fichier d'installation `.dmg` pour double-cliquer dessus et installer l'application sur ton Mac, j'ai créé un script magique appelé `creer_dmg.sh` !

### Comment l'utiliser ?
1. Copie le dossier `mac_caisse` sur ton Mac.
2. Ouvre l'application **Terminal** sur ton Mac.
3. Rends-toi dans le dossier `mac_caisse` dans ton terminal (par exemple en tapant `cd ` puis en glissant-déposant le dossier `mac_caisse` dans la fenêtre du terminal, puis appuie sur **Entrée**).
4. Exécute cette commande pour rendre le script exécutable et le lancer :
   ```bash
   chmod +x creer_dmg.sh && ./creer_dmg.sh
   ```
5. **Hop !** Le script compile tout et génère un fichier **`Caisse.dmg`** tout propre dans le dossier ! Double-clique dessus pour installer ta caisse enregistreuse sur ton Mac ! 🐾🍏

---

## 🔒 Configuration Firebase requise
Assure-toi que les règles de ta Realtime Database Firebase sur ton URL `https://test2-mdr-default-rtdb.europe-west1.firebasedatabase.app/` autorisent la lecture et l'écriture publique pour le test. 

Dans l'onglet **Rules (Règles)** de ta console Firebase Realtime Database :
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

Une fois cette règle publiée, tout ce que tu feras sur ton application Python (Windows) ou SwiftUI (Mac) sera instantanément synchronisé ! 🐱🔥
