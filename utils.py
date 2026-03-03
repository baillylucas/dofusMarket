import json
import os
from pathlib import Path
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON
from config import CURRENT_USER, GROUPS_DRIVE_FILE_ID, SERVICE_ACCOUNT_FILE

# Chemin des fichiers de sauvegarde
DATA_DIR = Path("data")
SCRAPPER_FILE = DATA_DIR / "items_scrap.json"
FAVORITES_FILE = DATA_DIR / "items_fav.json"

def ensure_data_dir():
    """Crée le répertoire data s'il n'existe pas"""
    DATA_DIR.mkdir(exist_ok=True)

# --- SCRAPPER ---

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

def load_scrapper_ingredients():
    """Charge la liste des ingrédients automatiques du scrapper depuis le fichier JSON"""
    ensure_data_dir()
    if SCRAPPER_FILE.exists():
        try:
            with open(SCRAPPER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ingredients', [])
        except Exception as e:
            print(f"Erreur lors du chargement des ingrédients du scrapper: {e}")
            return []
    return []

def save_scrapper_items(items_list):
    """Sauvegarde la liste des items du scrapper dans le fichier JSON"""
    ensure_data_dir()
    try:
        # Charger les ingrédients existants pour ne pas les écraser
        current_ingredients = load_scrapper_ingredients()
        data = {
            'items': items_list,
            'ingredients': current_ingredients
        }
        with open(SCRAPPER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier scrapper: {e}")
        return False

def save_scrapper_data(items_list, ingredients_list):
    """Sauvegarde la liste des items et des ingrédients du scrapper dans le fichier JSON"""
    ensure_data_dir()
    try:
        data = {
            'items': items_list,
            'ingredients': ingredients_list
        }
        with open(SCRAPPER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier scrapper: {e}")
        return False

def get_all_ingredients_recursive(data, item_ids):
    """
    Récupère tous les ingrédients nécessaires pour crafter les items spécifiés.
    Retourne une liste unique d'IDs d'ingrédients (sans les items de départ).

    Args:
        data: Dictionnaire complet des items depuis Google Drive
        item_ids: Liste des IDs d'items pour lesquels extraire les ingrédients

    Returns:
        Liste unique d'IDs d'ingrédients
    """
    all_ingredients = set()
    items_to_process = set(item_ids)

    def extract_ingredients(item_id):
        """Fonction récursive pour extraire les ingrédients"""
        item_id_str = str(item_id)

        if item_id_str not in data:
            return

        item = data[item_id_str]

        # Si l'item est craftable et a des ingrédients
        if item.get('is_craft') and item.get('ingredients'):
            for ingredient in item['ingredients']:
                ing_id = ingredient['id']
                all_ingredients.add(ing_id)
                # Récursion pour les sous-ingrédients
                extract_ingredients(ing_id)

    # Extraire les ingrédients pour chaque item
    for item_id in items_to_process:
        extract_ingredients(item_id)

    return sorted(list(all_ingredients))

def add_items_to_scrapper(item_ids, data=None):
    """
    Ajoute des items à la liste du scrapper et met à jour automatiquement
    la liste des ingrédients nécessaires.

    Args:
        item_ids: Liste des IDs d'items à ajouter
        data: Dictionnaire complet des items (optionnel, sera chargé si None)

    Returns:
        Nombre d'items ajoutés
    """
    current_items = load_scrapper_items()
    current_ingredients = load_scrapper_ingredients()

    # Convertir en ensemble pour éviter les doublons
    current_items_set = set(current_items)
    new_items_set = set(item_ids)
    updated_items_set = current_items_set.union(new_items_set)

    # Si data est fourni, mettre à jour les ingrédients automatiquement
    if data is not None:
        # Extraire tous les ingrédients pour tous les items (anciens + nouveaux)
        all_items = list(updated_items_set)
        all_extracted_ingredients = set(get_all_ingredients_recursive(data, all_items))

        # Retirer les items qui sont aussi dans la liste des items choisis
        ingredients_only = all_extracted_ingredients - updated_items_set

        # Sauvegarder les deux listes
        updated_items_list = sorted(list(updated_items_set))
        updated_ingredients_list = sorted(list(ingredients_only))
        save_scrapper_data(updated_items_list, updated_ingredients_list)
    else:
        # Sans data, juste sauvegarder les items
        updated_items_list = sorted(list(updated_items_set))
        save_scrapper_items(updated_items_list)

    return len(updated_items_set) - len(current_items_set)

def remove_items_from_scrapper(item_ids, data=None):
    """
    Supprime des items de la liste du scrapper et recalcule les ingrédients.

    Args:
        item_ids: Liste des IDs d'items à supprimer
        data: Dictionnaire complet des items (optionnel, pour recalculer les ingrédients)

    Returns:
        Nombre d'items supprimés
    """
    current_items = load_scrapper_items()

    # Convertir en ensemble pour l'opération de suppression
    current_set = set(current_items)
    items_to_remove = set(item_ids)
    updated_set = current_set - items_to_remove

    # Si data est fourni, recalculer les ingrédients
    if data is not None and updated_set:
        all_extracted_ingredients = set(get_all_ingredients_recursive(data, list(updated_set)))
        ingredients_only = all_extracted_ingredients - updated_set

        updated_items_list = sorted(list(updated_set))
        updated_ingredients_list = sorted(list(ingredients_only))
        save_scrapper_data(updated_items_list, updated_ingredients_list)
    elif data is not None and not updated_set:
        # Si plus d'items, vider aussi les ingrédients
        save_scrapper_data([], [])
    else:
        # Sans data, juste sauvegarder les items
        updated_list = sorted(list(updated_set))
        save_scrapper_items(updated_list)

    return len(current_items) - len(updated_set)

def remove_ingredients_from_scrapper(ingredient_ids):
    """
    Supprime des ingrédients de la liste du scrapper sans toucher aux items.

    Args:
        ingredient_ids: Liste des IDs d'ingrédients à supprimer

    Returns:
        Nombre d'ingrédients supprimés
    """
    current_items = load_scrapper_items()
    current_ingredients = load_scrapper_ingredients()

    # Convertir en ensemble pour l'opération de suppression
    current_ing_set = set(current_ingredients)
    ing_to_remove = set(ingredient_ids)
    updated_ing_set = current_ing_set - ing_to_remove

    # Sauvegarder sans modifier les items
    updated_ingredients_list = sorted(list(updated_ing_set))
    save_scrapper_data(current_items, updated_ingredients_list)

    return len(current_ingredients) - len(updated_ing_set)

# --- FAVORIS ---

def load_favorite_items():
    """Charge la liste des items favoris depuis le fichier JSON"""
    ensure_data_dir()
    if FAVORITES_FILE.exists():
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('items', [])
        except Exception as e:
            print(f"Erreur lors du chargement du fichier favoris: {e}")
            return []
    return []

def save_favorite_items(items_list):
    """Sauvegarde la liste des items favoris dans le fichier JSON"""
    ensure_data_dir()
    try:
        data = {
            'items': items_list
        }
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier favoris: {e}")
        return False

def add_items_to_favorites(item_ids):
    """Ajoute des items à la liste des favoris"""
    current_items = load_favorite_items()
    
    # Convertir en ensemble pour éviter les doublons, puis en liste
    current_set = set(current_items)
    new_items = set(item_ids)
    updated_set = current_set.union(new_items)
    
    updated_list = sorted(list(updated_set))
    save_favorite_items(updated_list)
    
    return len(updated_list) - len(current_items)

def remove_items_from_favorites(item_ids):
    """Supprime des items de la liste des favoris"""
    current_items = load_favorite_items()
    
    # Convertir en ensemble pour l'opération de suppression
    current_set = set(current_items)
    items_to_remove = set(item_ids)
    updated_set = current_set - items_to_remove
    
    updated_list = sorted(list(updated_set))
    save_favorite_items(updated_list)
    
    return len(current_items) - len(updated_list)

def is_favorite(item_id, favorite_list):
    """Vérifie si un item est dans la liste des favoris"""
    return item_id in favorite_list

# --- GROUPES (Google Drive) ---

def load_groups_data():
    """Charge les données de groupes depuis Google Drive"""
    try:
        drive = GoogleDriveJSON(GROUPS_DRIVE_FILE_ID, SERVICE_ACCOUNT_FILE)
        data = drive.read()
        return data
    except Exception as e:
        print(f"Erreur lors du chargement des groupes: {e}")
        # Structure par défaut si erreur
        return {
            "users": [CURRENT_USER],
            "groups": {}
        }

def load_groups_data_cached():
    """Version cachée du chargement des groupes (utilise streamlit cache)"""
    import streamlit as st

    # Utiliser le cache de streamlit avec un TTL de 60 secondes
    @st.cache_data(ttl=60, show_spinner=False)
    def _load_cached():
        return load_groups_data()

    return _load_cached()

def save_groups_data(data):
    """Sauvegarde les données de groupes sur Google Drive"""
    try:
        drive = GoogleDriveJSON(GROUPS_DRIVE_FILE_ID, SERVICE_ACCOUNT_FILE)
        drive.write(data)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des groupes: {e}")
        return False

def get_user_groups(user=None, force_refresh=False):
    """Récupère tous les groupes accessibles par l'utilisateur (créés ou partagés avec lui)"""
    if user is None:
        user = CURRENT_USER

    # Utiliser streamlit cache si disponible
    try:
        import streamlit as st

        # Si force_refresh, invalider le cache
        if force_refresh and hasattr(st, 'cache_data'):
            st.cache_data.clear()

        @st.cache_data(ttl=60, show_spinner=False)
        def _get_user_groups_cached(user_key):
            data = load_groups_data()
            groups = data.get('groups', {})

            user_groups = {}
            for group_id, group_data in groups.items():
                if group_data['owner'] == user_key or user_key in group_data.get('shared_with', []):
                    user_groups[group_id] = group_data

            return user_groups

        return _get_user_groups_cached(user)
    except ImportError:
        # Fallback si streamlit n'est pas disponible
        data = load_groups_data()
        groups = data.get('groups', {})

        user_groups = {}
        for group_id, group_data in groups.items():
            if group_data['owner'] == user or user in group_data.get('shared_with', []):
                user_groups[group_id] = group_data

        return user_groups

def create_group(name, shared_with=None, user=None):
    """Crée un nouveau groupe pour l'utilisateur"""
    if user is None:
        user = CURRENT_USER

    if shared_with is None:
        shared_with = []

    data = load_groups_data()

    # Générer un ID unique pour le groupe
    group_id = f"{user}_{name}"

    # Vérifier si un groupe avec cet ID existe déjà
    if group_id in data['groups']:
        return None  # Le groupe existe déjà

    # Créer le groupe
    new_group = {
        "name": name,
        "owner": user,
        "shared_with": shared_with,
        "items": [],
        "is_default": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    data['groups'][group_id] = new_group

    if save_groups_data(data):
        return group_id
    return None

def delete_group(group_id, user=None):
    """Supprime un groupe (uniquement si l'utilisateur est le propriétaire)"""
    if user is None:
        user = CURRENT_USER

    data = load_groups_data()
    groups = data.get('groups', {})

    if group_id not in groups:
        return False

    group = groups[group_id]

    # Vérifier que l'utilisateur est le propriétaire
    if group['owner'] != user:
        return False

    del data['groups'][group_id]
    return save_groups_data(data)

def add_items_to_group(group_id, item_ids, user=None):
    """Ajoute des items à un groupe"""
    if user is None:
        user = CURRENT_USER

    data = load_groups_data()
    groups = data.get('groups', {})

    if group_id not in groups:
        return 0

    group = groups[group_id]

    # Vérifier que l'utilisateur a accès au groupe
    if group['owner'] != user and user not in group.get('shared_with', []):
        return 0

    # Ajouter les items
    current_items = set(group['items'])
    new_items = set(item_ids)
    updated_items = current_items.union(new_items)

    group['items'] = sorted(list(updated_items))
    group['updated_at'] = datetime.now().isoformat()

    if save_groups_data(data):
        return len(updated_items) - len(current_items)
    return 0

def remove_items_from_group(group_id, item_ids, user=None):
    """Supprime des items d'un groupe"""
    if user is None:
        user = CURRENT_USER

    data = load_groups_data()
    groups = data.get('groups', {})

    if group_id not in groups:
        return 0

    group = groups[group_id]

    # Vérifier que l'utilisateur a accès au groupe
    if group['owner'] != user and user not in group.get('shared_with', []):
        return 0

    # Supprimer les items
    current_items = set(group['items'])
    items_to_remove = set(item_ids)
    updated_items = current_items - items_to_remove

    removed_count = len(current_items) - len(updated_items)

    group['items'] = sorted(list(updated_items))
    group['updated_at'] = datetime.now().isoformat()

    if save_groups_data(data):
        return removed_count
    return 0

def get_group_items(group_id, user=None):
    """Récupère la liste des items d'un groupe"""
    if user is None:
        user = CURRENT_USER

    data = load_groups_data()
    groups = data.get('groups', {})

    if group_id not in groups:
        return []

    group = groups[group_id]

    # Vérifier que l'utilisateur a accès au groupe
    if group['owner'] != user and user not in group.get('shared_with', []):
        return []

    return group['items']

def get_items_in_groups(group_ids, user=None):
    """Récupère tous les items appartenant à au moins un des groupes spécifiés"""
    if user is None:
        user = CURRENT_USER

    all_items = set()
    for group_id in group_ids:
        items = get_group_items(group_id, user)
        all_items.update(items)

    return list(all_items)

def ensure_default_group(user=None):
    """S'assure que l'utilisateur a un groupe 'favoris' par défaut"""
    if user is None:
        user = CURRENT_USER

    data = load_groups_data()

    # Vérifier si l'utilisateur existe dans la liste
    if user not in data.get('users', []):
        data['users'].append(user)

    # Chercher un groupe favoris pour cet utilisateur
    favoris_group_id = f"favoris_{user}"

    if favoris_group_id not in data.get('groups', {}):
        # Créer le groupe favoris par défaut
        data['groups'][favoris_group_id] = {
            "name": "favoris",
            "owner": user,
            "shared_with": [],
            "items": [],
            "is_default": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        save_groups_data(data)

    return favoris_group_id

# --- SCRAPPER - ORGANISATION PAR HDV ---

def get_scrapper_items_by_hdv(data):
    """
    Récupère les items et ingrédients du scrapper et les organise par HDV.

    Args:
        data: Dictionnaire complet des items depuis Google Drive

    Returns:
        Dict[str, List[str]]: Dictionnaire {nom_hdv: [liste de noms d'items]}

    Exemple:
        {
            "ressources": ["Bois de Frêne", "Cuivre"],
            "equipements": ["Amulette du Bouftou"],
            ...
        }
    """
    # Charger les items et ingrédients du scrapper
    scrapper_items = load_scrapper_items()
    scrapper_ingredients = load_scrapper_ingredients()

    # Combiner les deux listes (liste unique)
    all_item_ids = list(set(scrapper_items + scrapper_ingredients))

    # Mapper les noms HDV de la BDD vers les noms utilisés dans le scrapper
    # Support pour les deux formats (avec et sans "Hôtel de vente")
    hdv_mapping = {
        "Hôtel de vente de ressources": "ressources",
        "Hôtel de vente d'équipements": "equipements",
        "Hôtel de vente de consommables": "consommables",
        "Hôtel de vente des forgemagies": "forgemagies",
        "Hôtel de vente de créatures": "creatures",
        "Hôtel de vente des cosmétiques": "cosmetiques",
        "Hôtel de vente des âmes": "ames",
        # Formats courts (sans "Hôtel de vente")
        "Ressources": "ressources",
        "Equipements": "equipements",
        "Consommables": "consommables",
        "Forgemagie": "forgemagies",  # Sans "s" (retourné par determine_hdv)
        "Forgemagies": "forgemagies",  # Avec "s" (au cas où)
        "Creatures": "creatures",
        "Cosmetiques": "cosmetiques",
        "Âmes": "ames"
    }

    # Organiser par HDV
    items_by_hdv = {
        "ressources": [],
        "equipements": [],
        "consommables": [],
        "forgemagies": [],
        "creatures": [],
        "cosmetiques": [],
        "ames": []
    }

    for item_id in all_item_ids:
        item_id_str = str(item_id)
        if item_id_str in data:
            item = data[item_id_str]
            item_name = item.get('name')
            item_hdv = item.get('hdv', 'N/A')

            # Mapper le nom du HDV
            if item_hdv in hdv_mapping:
                hdv_key = hdv_mapping[item_hdv]
                if item_name and item_name not in items_by_hdv[hdv_key]:
                    items_by_hdv[hdv_key].append(item_name)

    # Retirer les HDV vides
    items_by_hdv = {hdv: items for hdv, items in items_by_hdv.items() if items}

    return items_by_hdv

def _launch_script(batch_file: str, script_path: str, debug: bool, label: str):
    """
    Lance un script de scraping en tant que processus séparé (nouvelle console Windows).

    Args:
        batch_file: Chemin absolu vers le fichier .bat à utiliser sous Windows.
        script_path: Chemin absolu vers le script Python (utilisé sous Linux/Mac).
        debug: Si True, passe le flag --debug au script.
        label: Nom court du scraper pour les messages utilisateur.

    Returns:
        tuple: (success: bool, message: str, process: subprocess.Popen | None)
    """
    import subprocess

    project_root = os.path.dirname(__file__)

    if not os.path.exists(script_path):
        return False, f"Script non trouvé : {script_path}", None

    if not os.path.exists(batch_file):
        return False, f"Fichier batch non trouvé : {batch_file}", None

    extra_args = ["--debug"] if debug else []

    try:
        if os.name == 'nt':  # Windows
            cmd = ["cmd.exe", "/c", "start", "cmd.exe", "/k", batch_file] + extra_args
            process = subprocess.Popen(cmd, cwd=project_root, shell=False)
        else:  # Linux/Mac
            cmd = ["uv", "run", "python", script_path] + extra_args
            process = subprocess.Popen(cmd, cwd=project_root)

        debug_msg = " (mode DEBUG activé)" if debug else ""
        return True, f"{label} lancé avec succès{debug_msg} ! Une nouvelle console s'est ouverte.", process

    except Exception as e:
        return False, f"Erreur lors du lancement : {e}", None


def launch_scrapper(debug: bool = False):
    """
    Lance le scraper de prix HDV (5_dofus_scrapper.py) dans un processus séparé.

    Args:
        debug: Si True, active le mode debug avec screenshots élargis.

    Returns:
        tuple: (success: bool, message: str, process: subprocess.Popen | None)
    """
    project_root = os.path.dirname(__file__)
    return _launch_script(
        batch_file=os.path.join(project_root, "launch_scrapper.bat"),
        script_path=os.path.join(project_root, "scrapper", "5_dofus_scrapper.py"),
        debug=debug,
        label="Scraper de prix HDV",
    )


def launch_familier_scrapper(debug: bool = False):
    """
    Lance le scraper XP familier (8_familier_xp_scrapper.py) dans un processus séparé.

    Args:
        debug: Si True, active le mode debug avec screenshots élargis.

    Returns:
        tuple: (success: bool, message: str, process: subprocess.Popen | None)
    """
    project_root = os.path.dirname(__file__)
    return _launch_script(
        batch_file=os.path.join(project_root, "launch_familier_scrapper.bat"),
        script_path=os.path.join(project_root, "scrapper", "8_familier_xp_scrapper.py"),
        debug=debug,
        label="Scraper XP familier",
    )