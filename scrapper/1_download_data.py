import requests
from datetime import datetime
from constants import *
from pathlib import Path
import os
import sys

# Ajouter le répertoire parent au path pour importer googleDriveJSON
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from googleDriveJSON import GoogleDriveJSON

def determine_hdv(item_type: str) -> str:
    """
    Détermine l'HDV (Hôtel de Vente) d'un item en fonction de son type.

    Args:
        item_type: Le type de l'item (ex: "Épée", "Bois de Frêne", etc.)

    Returns:
        str: Le nom de l'HDV ("Ressources", "Equipements", etc.) ou None si non trouvé
    """
    if item_type in L_TYPES_RESSOURCES:
        return "Ressources"
    elif item_type in L_TYPES_EQUIPEMENTS:
        return "Equipements"
    elif item_type in L_TYPES_CREATURES:
        return "Creatures"
    elif item_type in L_TYPES_FORGEMAGIE:
        return "Forgemagie"
    elif item_type in L_TYPES_CONSOMMABLES:
        return "Consommables"
    elif item_type in L_TYPES_COSMETIQUES:
        return "Cosmetiques"
    elif item_type in L_TYPES_AMES:
        return "Ames"
    else:
        return None

def get_all_jobs():
    """
    Récupère tous les métiers du jeu à partir de dofusdb

    Returns:
        dict : dictionnaire contenant tous les métiers du jeu (clé: id du métier, valeur: nom en français)

    """
    url = "https://api.dofusdb.fr/jobs"
    jobs_data = {}
    skip = 0

    while True:
        params = {
           '$limit': 50,
           '$skip': skip
        }

        jobs = requests.get(url, params=params).json()

        if not jobs['data']:
            break

        for job in jobs['data']:
            jobs_data[job['id']] = job['name']['fr']

        skip += 50

    return jobs_data

def get_all_recipes():
    """
    Récupère toutes les recettes du jeu à partir de dofusdb

    Returns:
        dict : dictionnaire contenant toutes les recettes du jeu

    """
    url = "https://api.dofusdb.fr/recipes/"
    recipes_data = {}
    skip = 0

    while True:
        params = {
           '$limit': 50,
           '$skip': skip
        }

        recipes = requests.get(url, params=params).json()

        if not recipes['data']:
            break

        for recipe in recipes['data']:
            ingredients = [
                {'id': ing_id, 'quantity': qty}
                for ing_id, qty in zip(recipe['ingredientIds'], recipe['quantities'])
            ]

            item_type = recipe['result']['type']['name']['fr']
            hdv = determine_hdv(item_type)

            recipe_data = {
                'id': recipe['resultId'],
                'name': recipe['resultName']['fr'],
                'type': item_type,
                'level': recipe['resultLevel'],
                'iconId': recipe['result']['iconId'],
                'is_craft': True,
                'ingredients': ingredients
            }

            # Ajouter le jobId si présent
            if 'jobId' in recipe:
                recipe_data['jobId'] = recipe['jobId']

            # Ajouter l'HDV seulement si trouvé
            if hdv is not None:
                recipe_data['hdv'] = hdv

            recipes_data[recipe['resultId']] = recipe_data

        skip += 50

    return recipes_data

def get_all_items():
    """
    Récupère tous les items du jeu à partir de dofusdb
    
    Returns:
        dict : dictionnaire contenant toutes les recettes du jeu
    
    """
    url = "https://api.dofusdb.fr/items?isSaleable=true"
    items_data = {}
    skip = 0
    
    while True:
        params = {
            '$limit': 50,
            '$skip': skip
        }
        
        items = requests.get(url, params=params).json()
        
        if not items['data']:
            break
        
        for item in items['data']:
            item_type = item['type']['name']['fr']
            hdv = determine_hdv(item_type)

            item_data = {
                'id': item['id'],
                'name': item['name']['fr'],
                'level': item['level'],
                'iconId': item['iconId'],
                'supertype': item['type']['superType']['name']['fr'],
                'type': item_type,
                'is_craft': False,
            }

            # Ajouter l'HDV seulement si trouvé
            if hdv is not None:
                item_data['hdv'] = hdv

            items_data[item['id']] = item_data
        
        skip += 50
    
    return items_data

def merge_recipes_and_items():
    """
    Met à jour les recettes du fichiers "dofus_items.json" sur Google Drive
    Ne modifie pas les prix.

    Returns:
        dict : dictionnaire contenant toutes les recettes du jeu
        écris ce dictionnaire dans dofus_items.json sur Google Drive

    """
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")  # Format simplifié

    # Initialiser GoogleDriveJSON avec les constantes
    drive_json = GoogleDriveJSON(GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE)

    # Lire les données existantes depuis Google Drive
    existing_data = {}
    try:
        print("Lecture des donnees existantes depuis Google Drive...")
        existing_data = drive_json.read()
        print(f"OK - {len(existing_data)} items charges depuis Google Drive")
    except Exception as e:
        print(f"ATTENTION - Aucune donnee existante trouvee sur Google Drive: {e}")
        print("Creation d'un nouveau fichier...")

    # Récupérer les nouvelles données
    print("Recuperation des metiers...")
    jobs_data = get_all_jobs()
    print(f"OK - {len(jobs_data)} metiers charges")

    print("Recuperation des recettes...")
    recipes_data = get_all_recipes()
    print(f"OK - {len(recipes_data)} recettes chargees")

    print("Recuperation des items...")
    items_data = get_all_items()
    print(f"OK - {len(items_data)} items charges")

    final_data = {}
    
    # 1. Identifier tous les IDs à garder
    ids_to_keep = set()
    ids_to_keep.update(recipes_data.keys())
    for recipe_data in recipes_data.values():
        for ingredient in recipe_data['ingredients']:
            ids_to_keep.add(ingredient['id'])
    
    # 2. Construire la structure finale
    for item_id in ids_to_keep:
        if item_id in items_data:
            # Créer le nouvel item
            new_item = items_data[item_id].copy()
            new_item['last_maj'] = current_time

            # Si c'est un craft, ajouter les infos de recette
            if item_id in recipes_data:
                recipe = recipes_data[item_id]
                new_item.update({
                    'is_craft': True,
                    'ingredients': recipe['ingredients']
                })

                # Ajouter le nom du métier si disponible
                if 'jobId' in recipe and recipe['jobId'] in jobs_data:
                    new_item['job'] = jobs_data[recipe['jobId']]

            # Si l'item existait déjà, préserver ses prix
            if str(item_id) in existing_data:
                old_item = existing_data[str(item_id)]
                new_item['prix_hdv'] = old_item.get('prix_hdv', {})  # Valeur par défaut
                new_item['cout_craft'] = old_item.get('cout_craft', {})
            else:
                # Initialiser les prix pour les nouveaux items
                new_item['prix_hdv'] = {}
                new_item['cout_craft'] = {}

            final_data[str(item_id)] = new_item  # Convertir en string pour cohérence
    
    # 3. Vérifier les ingrédients invalides
    items_to_remove = set()
    for item_id, item_data in final_data.items():
        if item_data.get('is_craft'):
            for ingredient in item_data['ingredients']:
                if str(ingredient['id']) not in final_data:
                    items_to_remove.add(item_id)
                    break
    
    # Retirer les items avec des ingrédients invalides
    for item_id in items_to_remove:
        del final_data[item_id]

    # Sauvegarder sur Google Drive
    print(f"Ecriture de {len(final_data)} items sur Google Drive...")
    drive_json.write(final_data)

    return final_data

if __name__ == "__main__":
    # Récupère les recettes et items via l'api dofusdb, et les écrit sur Google Drive
    print('Telechargement des donnees ...')
    merge_recipes_and_items()
    print('Telechargement et synchronisation reussis !')