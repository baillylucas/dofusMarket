import json
import os
from pathlib import Path

# Chemin du fichier de sauvegarde
DATA_DIR = Path("data")
SCRAPPER_FILE = DATA_DIR / "items_scrap.json"

def ensure_data_dir():
    """Crée le répertoire data s'il n'existe pas"""
    DATA_DIR.mkdir(exist_ok=True)

def load_scrapper_items():
    """Charge la liste des items du scrapper depuis le fichier JSON"""
    ensure_data_dir()
    if SCRAPPER_FILE.exists():
        try:
            with open(SCRAPPER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('items', [])
        except Exception as e:
            print(f"Erreur lors du chargement du fichier scrapper: {e}")
            return []
    return []

def save_scrapper_items(items_list):
    """Sauvegarde la liste des items du scrapper dans le fichier JSON"""
    ensure_data_dir()
    try:
        data = {
            'items': items_list
        }
        with open(SCRAPPER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier scrapper: {e}")
        return False

def add_items_to_scrapper(item_ids):
    """Ajoute des items à la liste du scrapper"""
    current_items = load_scrapper_items()
    
    # Convertir en ensemble pour éviter les doublons, puis en liste
    current_set = set(current_items)
    new_items = set(item_ids)
    updated_set = current_set.union(new_items)
    
    updated_list = sorted(list(updated_set))
    save_scrapper_items(updated_list)
    
    return len(updated_list) - len(current_items)

def remove_items_from_scrapper(item_ids):
    """Supprime des items de la liste du scrapper"""
    current_items = load_scrapper_items()
    
    # Convertir en ensemble pour l'opération de suppression
    current_set = set(current_items)
    items_to_remove = set(item_ids)
    updated_set = current_set - items_to_remove
    
    updated_list = sorted(list(updated_set))
    save_scrapper_items(updated_list)
    
    return len(current_items) - len(updated_list)