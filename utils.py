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
    group_id = f"{name}_{user}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

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
    """Supprime un groupe (uniquement si l'utilisateur est le propriétaire et que ce n'est pas un groupe par défaut)"""
    if user is None:
        user = CURRENT_USER

    data = load_groups_data()
    groups = data.get('groups', {})

    if group_id not in groups:
        return False

    group = groups[group_id]

    # Vérifier que l'utilisateur est le propriétaire et que ce n'est pas un groupe par défaut
    if group['owner'] != user or group.get('is_default', False):
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