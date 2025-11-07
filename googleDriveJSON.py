import requests
import json

class GoogleDriveJSON:
    def __init__(self, file_id: str, api_key: str = None):
        """
        Initialise la classe avec l'ID du fichier Google Drive.
        Si une clé API est fournie, elle permettra l'écriture.
        """
        self.file_id = file_id
        self.api_key = api_key
        self.base_download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
        self.base_api_url = f'https://www.googleapis.com/drive/v3/files/{file_id}'

    def read(self):
        """
        Lit le contenu JSON d’un fichier public sur Google Drive.
        Retourne un dictionnaire Python.
        """
        response = requests.get(self.base_download_url)
        response.raise_for_status()  # Lève une exception si erreur HTTP

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ValueError("Le contenu du fichier n'est pas un JSON valide.")
        return data

    def write(self, data: dict):
        """
        Écrit (met à jour) le contenu JSON du fichier sur Google Drive.
        ⚠️ Nécessite une clé API ou un token d'accès OAuth.
        """
        if not self.api_key:
            raise PermissionError("Écriture impossible sans clé API ou token d'accès.")

        url = f'https://www.googleapis.com/upload/drive/v3/files/{self.file_id}?uploadType=media&key={self.api_key}'
        headers = {'Content-Type': 'application/json'}
        response = requests.patch(url, headers=headers, data=json.dumps(data))

        if response.status_code not in (200, 204):
            raise RuntimeError(f"Erreur lors de l'écriture : {response.status_code} - {response.text}")

        print("✅ Données mises à jour avec succès sur Google Drive.")

# --- Exemple d’utilisation ---

if __name__ == "__main__":
    API_KEY = 'AIzaSyCH-_57w2vrxLEycNV-wI4_2G8AXGrLubI'
    FILE_ID = '1qO5ZaWX6xJLH70Kih3oO73NKTdUHuRcO'  # Remplace par ton ID
    drive_json = GoogleDriveJSON(FILE_ID, API_KEY)

    # Lire le fichier
    data = drive_json.read()
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Exemple : modifier et écrire (si clé API disponible)
    # drive_json.api_key = "TA_CLE_API"
    # data['utilisateur']['nom'] = "Jean Dupont"
    # drive_json.write(data)
