"""
Script pour initialiser le fichier JSON des groupes sur Google Drive
"""
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON
from config import GROUPS_DRIVE_FILE_ID, SERVICE_ACCOUNT_FILE

def init_groups_file():
    """Initialise le fichier JSON sur Google Drive avec les utilisateurs de base"""

    initial_data = {
        "users": [
            "Akisatsu",
            "KeTaBi"
        ],
        "groups": {
            "favoris_Akisatsu": {
                "name": "favoris",
                "owner": "Akisatsu",
                "shared_with": [],
                "items": [],
                "is_default": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            "favoris_KeTaBi": {
                "name": "favoris",
                "owner": "KeTaBi",
                "shared_with": [],
                "items": [],
                "is_default": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }
    }

    try:
        drive = GoogleDriveJSON(GROUPS_DRIVE_FILE_ID, SERVICE_ACCOUNT_FILE)
        drive.write(initial_data)
        print("✓ Fichier JSON initialisé avec succès sur Google Drive")
        print(f"  - {len(initial_data['users'])} utilisateurs créés")
        print(f"  - {len(initial_data['groups'])} groupes créés")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'initialisation: {e}")
        return False

if __name__ == "__main__":
    print("Initialisation du fichier JSON des groupes...")
    init_groups_file()
