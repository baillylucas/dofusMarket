import requests 
import json
from datetime import datetime
from constants import *
from pathlib import Path
import os


def get_all_required_ingredients(data, item_id, visited=None):
   """
   Récupère la liste des ingrédients d'un item.
   
   Args:
        data (json) : structure contenant les items de dofus_items.json
        item_id (int) : id de l'item auquel il faut récupérer les ingrédients
        visited (boolean) : liste des items déjà visités

    Returns:
        list : Liste des ids des ingrédients de l'item
   
   """
   if visited is None:
       visited = set()
   
   if item_id in visited:
       return set()
   
   visited.add(item_id)
   required_ingredients = {item_id}
   
   item = data.get(str(item_id))
   if item and item.get('is_craft') and item.get('ingredients'):
       for ingredient in item['ingredients']:
           required_ingredients.update(
               get_all_required_ingredients(data, ingredient['id'], visited)
           )
   
   return required_ingredients


def create_type_files(json_filename="data/dofus_items.json", levels=None, l_types=None, l_supertypes=None, l_names=None, only_craft=True):
    """
    Trie les items trouvés dans "dofus_items.json" en 7 fichiers :
        - consommables.txt
        - equipements.txt
        - forgemagies.txt
        - ressources.txt
        - creatures.txt
        - cosmetiques.txt
        - ames.txt
    
    Args:
        json_filename (string) : chemin du fichier contenant les items dofus
        levels ([int, int]) : niveaux minimum et maximum des items à récupérer
        l_types (list[string]) : liste des types d'items à récupérer
        l_supertypes (list[string]) : liste des supertypes d'items à récupérer
        l_names (list[string]) : liste des noms d'items à récupérer
        only_craft (boolean) : paramètre permettant de récupérer uniquement les items craftable

    Returns:
        files : créer les fichiers consommables, equipements, forgemagies, ressources, creatures, cosmetiques et ames
    
    """
    # Charger les données JSON
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if only_craft:
        # 1. Filtrer d'abord les crafts selon les critères
        target_crafts = {
            item_id: item for item_id, item in data.items()
            if item.get('is_craft') and
               (not levels or levels[0] <= item['level'] <= levels[1]) and
               (not l_types or item['type'] in l_types) and
               (not l_supertypes or item['supertype'] in l_supertypes) and
               (not l_names or item['name'] in l_names)
        }

        # 2. Récupérer tous les ingrédients nécessaires pour ces crafts
        all_required_items = set()
        for item_id in target_crafts:

            all_required_items.update(
                get_all_required_ingredients(data, item_id)
            )
        
        # 3. Créer le dictionnaire final avec les crafts ciblés et leurs ingrédients
        filtered_data = {
            item_id: data[item_id] for item_id in map(str, all_required_items)
        }
    else:
        # Appliquer directement les filtres si only_craft est False
        filtered_data = {
            item_id: item for item_id, item in data.items()
            if (not levels or levels[0] <= item['level'] <= levels[1]) and
               (not l_types or item['type'] in l_types) and
               (not l_supertypes or item['supertype'] in l_supertypes) and
               (not l_names or item['name'] in l_names)
        }

    # Préparer les dictionnaires pour chaque catégorie
    ressources = []
    consommables = []
    forgemagies = []
    equipements = []
    creatures = []
    cosmetiques = []
    ames = []

    # Trier les items dans les bonnes catégories
    for item in filtered_data.values():
        
        name = item['name']
        item_type = item['type']
        # print(f"Item: {name}, Type: {item_type}")

        if item_type in L_TYPES_RESSOURCES:
            ressources.append(name)
        if item_type in L_TYPES_CONSOMMABLES:
            consommables.append(name)
        if item_type in L_TYPES_FORGEMAGIE:
            forgemagies.append(name)
        if item_type in L_TYPES_EQUIPEMENTS:
            equipements.append(name)
        if item_type in L_TYPES_CREATURES:
            creatures.append(name)
        if item_type in L_TYPES_COSMETIQUES:
            cosmetiques.append(name)
        if item_type in L_TYPES_AMES:
            ames.append(name)


    # Trier les listes par ordre alphabétique
    ressources.sort()
    consommables.sort()
    forgemagies.sort()
    equipements.sort()
    creatures.sort()
    cosmetiques.sort()
    ames.sort()

    # Créer le dossier data s'il n'existe pas
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)

    # Supprimer les anciens fichiers .txt
    for file in data_dir.glob("*.txt"):
        file.unlink()

    # Écrire uniquement les fichiers non vides
    files_to_write = {
        'ressources.txt': ressources,
        'consommables.txt': consommables,
        'forgemagies.txt': forgemagies,
        'equipements.txt': equipements,
        'creatures.txt': creatures,
        'cosmetiques.txt': cosmetiques,
        'ames.txt': ames
    }

    for filename, items in files_to_write.items():
        if items:  # Écrire uniquement si la liste n'est pas vide
            with open(data_dir / filename, 'w', encoding='utf-8') as f:
                for item in items:
                    f.write(f"{item}\n")
            print(f"{filename} créé avec {len(items)} items")




if __name__ == "__main__":
    # Exemple 1: Filtrer par noms d'items spécifiques
    # create_type_files(
    #     l_names=["Épée du Destiny", "Arc Céleste", "Marteau Titanesque"],
    #     only_craft=True
    # )
    
    # Exemple 2: Combiner filtre par noms et autres critères
    create_type_files(
        l_names = [
            "Anneau du Père Fwetar", 
            "Ceinture du Père Fwetar",
            "Bottes du Père Fwetar",
            "Bottes du Nowel Cauchemardesque",
            "Cape du Nowel Cauchemardesque",
            "Masque du Nowel Cauchemardesque",
            "Porte-Malheur du Nowel Cauchemardesque"
            ]
    )
    
    # # Exemple original
    # create_type_files(
    #     levels=[75, 100],
    #     l_supertypes=["Arme"],
    #     l_types=L_TYPES_FORGERON,
    #     only_craft=True
    # )