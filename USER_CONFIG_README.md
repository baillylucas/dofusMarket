# Configuration Utilisateur

## 📋 Vue d'ensemble

Le fichier `user_config.py` contient toutes les configurations spécifiques à chaque utilisateur/joueur. Ce fichier est ignoré par git pour éviter les conflits entre différents utilisateurs.

## 🚀 Installation

### 1. Créer votre fichier de configuration

```bash
# Copiez le template
cp user_config.example.py user_config.py
```

Ou sur Windows :
```cmd
copy user_config.example.py user_config.py
```

### 2. Modifier vos paramètres

Ouvrez `user_config.py` et modifiez les valeurs selon votre configuration :

#### **CURRENT_USER**
Votre pseudo Dofus. Exemple : `"KeTaBi"`

#### **TESSERAT_PATH**
Chemin vers l'exécutable Tesseract-OCR :
- Windows : `r"C:\Program Files\Tesseract-OCR\tesseract.exe"`
- Mac : `"/usr/local/bin/tesseract"` ou `"/opt/homebrew/bin/tesseract"`
- Linux : `"/usr/bin/tesseract"`

#### **COORDINATES_***
Coordonnées spécifiques à votre écran pour le scraping automatique.

## 🎯 Calibration des coordonnées

Les coordonnées dépendent de :
- La résolution de votre écran
- La position de la fenêtre Dofus
- Votre interface in-game

### Comment calibrer :

1. **Ouvrez Dofus en plein écran** (ou en fenêtre fixe)
2. **Ouvrez un HDV** dans le jeu
3. **Utilisez un outil de capture** pour noter les coordonnées :
   - Windows : Outil Capture d'écran (Win + Shift + S) affiche les coordonnées
   - Mac : Cmd + Shift + 4 affiche les coordonnées
   - Ou utilisez un script Python simple :

   ```python
   import pyautogui
   import time

   print("Placez votre souris sur l'élément dans 3 secondes...")
   time.sleep(3)
   x, y = pyautogui.position()
   print(f"Position : ({x}, {y})")
   ```

4. **Modifiez les valeurs** dans `user_config.py`

## 📝 Fichiers de configuration

| Fichier | Description | Commité ? |
|---------|-------------|-----------|
| `user_config.py` | Votre configuration personnelle | ❌ Non (ignoré par git) |
| `user_config.example.py` | Template de configuration | ✅ Oui |
| `config.py` | Configuration partagée du projet | ✅ Oui |
| `scrapper/constants.py` | Constantes du scrapper | ✅ Oui |

## ⚠️ Important

- **Ne commitez JAMAIS** `user_config.py` (il est dans `.gitignore`)
- Si vous mettez à jour `user_config.example.py`, commitez-le pour partager avec l'équipe
- Chaque utilisateur doit créer son propre `user_config.py`

## 🔧 Structure du projet

```
dofusMarket/
├── user_config.py              # Votre config (non commité)
├── user_config.example.py      # Template (commité)
├── config.py                   # Config partagée (importe depuis user_config)
└── scrapper/
    └── constants.py            # Constantes (importe depuis user_config)
```

## 🐛 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'user_config'`

➜ Vous n'avez pas créé `user_config.py`. Copiez le template :
```bash
cp user_config.example.py user_config.py
```

### Les coordonnées ne fonctionnent pas

➜ Recalibrez vos coordonnées selon votre résolution d'écran.

### Je veux partager mes coordonnées avec l'équipe

➜ Mettez à jour `user_config.example.py` avec vos valeurs et commitez ce fichier.
