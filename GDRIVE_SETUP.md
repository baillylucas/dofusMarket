# Configuration de l'accès Google Drive

Ce projet utilise Google Drive pour stocker et synchroniser le fichier `dofus_items.json`.

## Prérequis

1. Installer les dépendances Python :
```bash
pip install -r requirements.txt
```

## Configuration de l'authentification Google Drive

### Option 1 : Lecture seule (via gdown)

Si vous souhaitez uniquement lire les données, aucune configuration n'est nécessaire. Le module utilisera automatiquement `gdown` pour télécharger le fichier.

### Option 2 : Lecture/Écriture (via PyDrive2)

Pour pouvoir uploader des modifications sur Google Drive, vous devez configurer l'authentification OAuth :

1. **Créer un projet Google Cloud** (première fois seulement) :
   - Allez sur https://console.cloud.google.com/
   - Créez un nouveau projet
   - Activez l'API Google Drive
   - Créez des identifiants OAuth 2.0 (type "Application de bureau")
   - Téléchargez le fichier JSON des credentials

2. **Configurer PyDrive2** :
   - Renommez le fichier téléchargé en `client_secrets.json`
   - Placez-le à la racine du projet
   - Créez un fichier `settings.yaml` avec le contenu suivant :

```yaml
client_config_backend: settings
client_config:
  client_id: YOUR_CLIENT_ID
  client_secret: YOUR_CLIENT_SECRET

save_credentials: True
save_credentials_backend: file
save_credentials_file: credentials.json

get_refresh_token: True

oauth_scope:
  - https://www.googleapis.com/auth/drive.file
  - https://www.googleapis.com/auth/drive
```

3. **Première authentification** :
   - Lancez n'importe quel script Python du projet
   - Un navigateur s'ouvrira pour vous demander d'autoriser l'accès
   - Acceptez les permissions
   - Les credentials seront sauvegardés dans `credentials.json`

## ID du fichier Google Drive

Le fichier actuel est : `1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu`

Pour changer le fichier, modifiez la constante `GDRIVE_FILE_ID` dans `code/gdrive_helper.py`.

## Fonctionnement

- **Lecture** : Le module essaie d'abord PyDrive2, puis gdown, puis le cache local
- **Écriture** : Nécessite PyDrive2 configuré, sinon sauvegarde uniquement en local
- **Cache local** : Un cache est maintenu dans `data/dofus_items.json` pour un accès hors ligne

## Dépannage

### "PyDrive2 not available"
```bash
pip install PyDrive2
```

### "gdown not available"
```bash
pip install gdown
```

### Erreurs d'authentification
- Vérifiez que `client_secrets.json` et `settings.yaml` sont correctement configurés
- Supprimez `credentials.json` et réauthentifiez-vous
- Vérifiez que l'API Google Drive est activée dans votre projet Google Cloud

### Impossible de télécharger le fichier
- Vérifiez votre connexion Internet
- Vérifiez que l'ID du fichier est correct
- En dernier recours, le cache local sera utilisé
