"""
Module pour gérer l'accès au fichier dofus_items.json sur Google Drive.
File ID: 1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
import io

try:
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive
    PYDRIVE_AVAILABLE = True
except ImportError:
    PYDRIVE_AVAILABLE = False
    print("PyDrive2 not available. Install it with: pip install PyDrive2")

try:
    import gdown
    GDOWN_AVAILABLE = True
except ImportError:
    GDOWN_AVAILABLE = False
    print("gdown not available. Install it with: pip install gdown")


# ID du fichier Google Drive
GDRIVE_FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

# Chemin du fichier de credentials local (cache)
LOCAL_CACHE_PATH = "data/dofus_items.json"


class GDriveHelper:
    """Classe pour gérer l'accès au fichier JSON sur Google Drive."""

    def __init__(self, file_id: str = GDRIVE_FILE_ID):
        self.file_id = file_id
        self.drive = None
        self._authenticate()

    def _authenticate(self):
        """Authentifie avec Google Drive."""
        if not PYDRIVE_AVAILABLE:
            print("⚠️ PyDrive2 non disponible. Utilisation du mode lecture seule via gdown.")
            return

        try:
            gauth = GoogleAuth()

            # Essayer de charger les credentials sauvegardés
            credentials_file = "credentials.json"
            if os.path.exists(credentials_file):
                gauth.LoadCredentialsFile(credentials_file)

            # Si pas de credentials valides, authentifier
            if gauth.credentials is None:
                # Authentification locale (ouvre un navigateur)
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                # Rafraîchir les credentials
                gauth.Refresh()
            else:
                # Autoriser avec les credentials existants
                gauth.Authorize()

            # Sauvegarder les credentials pour la prochaine fois
            gauth.SaveCredentialsFile(credentials_file)

            self.drive = GoogleDrive(gauth)
            print("✅ Authentification Google Drive réussie")

        except Exception as e:
            print(f"⚠️ Erreur d'authentification Google Drive: {e}")
            print("Mode lecture seule via gdown activé")
            self.drive = None

    def download_json(self) -> Dict[str, Any]:
        """
        Télécharge et charge le fichier JSON depuis Google Drive.

        Returns:
            Dict contenant les données du fichier JSON
        """
        # Méthode 1: Utiliser PyDrive2 si disponible
        if self.drive is not None:
            try:
                file = self.drive.CreateFile({'id': self.file_id})
                content = file.GetContentString()
                data = json.loads(content)
                print(f"✅ Fichier téléchargé depuis Google Drive (PyDrive2)")

                # Sauvegarder localement comme cache
                self._save_local_cache(data)
                return data

            except Exception as e:
                print(f"⚠️ Erreur lors du téléchargement via PyDrive2: {e}")
                print("Tentative avec gdown...")

        # Méthode 2: Utiliser gdown
        if GDOWN_AVAILABLE:
            try:
                url = f"https://drive.google.com/uc?id={self.file_id}"
                output = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
                output_path = output.name
                output.close()

                gdown.download(url, output_path, quiet=False)

                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                os.remove(output_path)
                print(f"✅ Fichier téléchargé depuis Google Drive (gdown)")

                # Sauvegarder localement comme cache
                self._save_local_cache(data)
                return data

            except Exception as e:
                print(f"⚠️ Erreur lors du téléchargement via gdown: {e}")

        # Méthode 3: Utiliser le cache local
        if os.path.exists(LOCAL_CACHE_PATH):
            print(f"⚠️ Utilisation du cache local: {LOCAL_CACHE_PATH}")
            with open(LOCAL_CACHE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)

        raise Exception("Impossible de télécharger le fichier depuis Google Drive et aucun cache local disponible")

    def upload_json(self, data: Dict[str, Any]) -> bool:
        """
        Upload le fichier JSON sur Google Drive.

        Args:
            data: Dictionnaire à sauvegarder

        Returns:
            True si le upload a réussi, False sinon
        """
        if self.drive is None:
            print("⚠️ Pas d'authentification Google Drive. Sauvegarde locale uniquement.")
            self._save_local_cache(data)
            return False

        try:
            # Convertir le dictionnaire en JSON
            json_content = json.dumps(data, ensure_ascii=False, indent=2)

            # Créer un objet fichier et uploader
            file = self.drive.CreateFile({'id': self.file_id})
            file.SetContentString(json_content)
            file.Upload()

            print(f"✅ Fichier uploadé sur Google Drive")

            # Sauvegarder également localement
            self._save_local_cache(data)
            return True

        except Exception as e:
            print(f"❌ Erreur lors de l'upload sur Google Drive: {e}")
            print("Sauvegarde locale uniquement")
            self._save_local_cache(data)
            return False

    def _save_local_cache(self, data: Dict[str, Any]):
        """Sauvegarde les données localement comme cache."""
        try:
            os.makedirs(os.path.dirname(LOCAL_CACHE_PATH), exist_ok=True)
            with open(LOCAL_CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Cache local sauvegardé: {LOCAL_CACHE_PATH}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde du cache local: {e}")


# Fonctions helpers pour faciliter l'utilisation
def load_dofus_items() -> Dict[str, Any]:
    """
    Charge le fichier dofus_items.json depuis Google Drive.

    Returns:
        Dict contenant les données des items Dofus
    """
    helper = GDriveHelper()
    return helper.download_json()


def save_dofus_items(data: Dict[str, Any]) -> bool:
    """
    Sauvegarde le fichier dofus_items.json sur Google Drive.

    Args:
        data: Dictionnaire contenant les données à sauvegarder

    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    helper = GDriveHelper()
    return helper.upload_json(data)


if __name__ == "__main__":
    # Test du module
    print("Test de téléchargement...")
    data = load_dofus_items()
    print(f"Nombre d'items chargés: {len(data)}")

    print("\nTest d'upload...")
    success = save_dofus_items(data)
    if success:
        print("Test réussi !")
    else:
        print("Test échoué (mais cache local sauvegardé)")
