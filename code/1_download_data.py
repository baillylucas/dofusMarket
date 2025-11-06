import requests 
import json
from datetime import datetime
from constants import *
from pathlib import Path
import os

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
            
            recipe_data = {
                'id': recipe['resultId'],
                'name': recipe['resultName']['fr'],
                'type': recipe['result']['type']['name']['fr'],
                'level': recipe['resultLevel'],
                'is_craft': True,
                'ingredients': ingredients
            }
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
            items_data[item['id']] = {
                'id': item['id'],
                'name': item['name']['fr'],
                'level': item['level'],
                'supertype': item['type']['superType']['name']['fr'],
                'type': item['type']['name']['fr'],
                'is_craft': False,
            }
        
        skip += 50
    
    return items_data

def merge_recipes_and_items():
    """
    Met à jour les recettes du fichiers "dofus_items.json"
    Ne modifie pas les prix.
    
    Returns:
        dict : dictionnaire contenant toutes les recettes du jeu
        écris ce dictionnaire dans dofus_items.json
    
    """
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M")  # Format simplifié
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)
    
    # Vérifier si le fichier existe et le charger si c'est le cas
    existing_data = {}
    if os.path.exists('data/dofus_items.json'):
        with open('data/dofus_items.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    
    # Récupérer les nouvelles données
    recipes_data = get_all_recipes()
    items_data = get_all_items()
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
                new_item.update({
                    'is_craft': True,
                    'ingredients': recipes_data[item_id]['ingredients']
                })
            
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
    
    # Sauvegarder
    with open('data/dofus_items.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    return final_data

if __name__ == "__main__":
    # Récupère les recettes et items via l'api dofusdb, et les écrit dans 
    # le fichier 'dofus_items.json' du dossier 'data'
    print('Téléchargement des données ...')
    merge_recipes_and_items()
    print('Téléchargement réussi !')