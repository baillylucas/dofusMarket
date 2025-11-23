import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

class GoogleDriveJSON:
    def __init__(self, file_id: str, service_account_file: str):
        """
        Initialise la classe avec l'ID du fichier Google Drive et le fichier Service Account.

        Args:
            file_id: L'ID du fichier Google Drive
            service_account_file: Chemin vers le fichier JSON du Service Account
        """
        self.file_id = file_id
        self.service_account_file = service_account_file

        # Configuration des scopes nécessaires
        # drive.file : fichiers créés par l'app uniquement
        # drive : accès complet aux fichiers partagés avec le Service Account
        self.scopes = ['https://www.googleapis.com/auth/drive']

        # Initialiser les credentials
        self.credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=self.scopes
        )

        # Créer le service Google Drive
        self.service = build('drive', 'v3', credentials=self.credentials)

    def read(self):
        """
        Lit le contenu JSON d'un fichier sur Google Drive via le Service Account.
        Retourne un dictionnaire Python.
        """
        try:
            # Télécharger le contenu du fichier
            request = self.service.files().get_media(fileId=self.file_id)
            content = request.execute()

            # Convertir en JSON
            data = json.loads(content.decode('utf-8'))
            return data

        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier : {e}")

    def write(self, data: dict):
        """
        Écrit (met à jour) le contenu JSON du fichier sur Google Drive via le Service Account.

        Args:
            data: Dictionnaire Python à écrire dans le fichier
        """
        try:
            # Convertir le dictionnaire en JSON
            json_content = json.dumps(data, ensure_ascii=False, indent=2)

            # Créer un objet de type fichier en mémoire
            media = MediaIoBaseUpload(
                BytesIO(json_content.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )

            # Mettre à jour le fichier sur Google Drive
            self.service.files().update(
                fileId=self.file_id,
                media_body=media,
                fields='id'
            ).execute()

            print("OK - Donnees mises a jour avec succes sur Google Drive.")

        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'écriture : {e}")

# --- Exemple d'utilisation ---

if __name__ == "__main__":
    SERVICE_ACCOUNT_FILE = 'credentials/service_account.json'  # Chemin vers votre fichier Service Account
    FILE_ID = '1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu'

    drive_json = GoogleDriveJSON(FILE_ID, SERVICE_ACCOUNT_FILE)

    # Lire le fichier
    print("Lecture du fichier...")
    data = drive_json.read()
    print(f"OK - Fichier lu : {len(data)} elements")

    # Afficher quelques exemples avec HDV
    print("\nExemples d'items avec HDV:")
    count = 0
    for item_id, item_data in data.items():
        if 'hdv' in item_data and count < 5:
            print(f"  - {item_data['name']} ({item_data['type']}) -> HDV: {item_data['hdv']}")
            count += 1
        if count >= 5:
            break

    # Compter les items par HDV
    hdv_counts = {}
    items_sans_hdv = 0
    for item_data in data.values():
        if 'hdv' in item_data:
            hdv = item_data['hdv']
            hdv_counts[hdv] = hdv_counts.get(hdv, 0) + 1
        else:
            items_sans_hdv += 1

    print("\nRepartition par HDV:")
    for hdv, count in sorted(hdv_counts.items()):
        print(f"  {hdv}: {count} items")
    print(f"  Sans HDV: {items_sans_hdv} items")
