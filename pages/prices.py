import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON
from functools import lru_cache
from utils import (
    add_items_to_scrapper,
    get_user_groups, add_items_to_group, remove_items_from_group,
    get_group_items, get_items_in_groups
)
from config import CURRENT_USER


# Configuration
st.set_page_config(layout="wide")

st.markdown("# 📊 Prix des items")

st.sidebar.markdown("# ⚙️ Filtres")

# --- CSS ---
st.markdown("""
<style>
    details { border: 1px solid #555; border-top: none; border-radius: 0; margin: 0; background-color: rgba(40, 50, 60, 0.6); }
    details:first-of-type { border-top: 1px solid #555; }
    summary {
        display: grid;
        grid-template-columns: 2% 3% 3% 13% 4% 10% 11% 8% 8% 8% 8% 8% 8% 2%;
        column-gap: 6px;
        padding: 16px 8px;
        cursor: pointer;
        background-color: rgba(40, 50, 60, 0.6);
        border-radius: 0;
        font-family: monospace;
        align-items: center;
        transition: background-color 0.2s;
        color: #ddd;
        min-height: 20px;
        list-style: none;
    }
    summary::-webkit-details-marker { display: none; }
    summary::marker { display: none; }
    summary:hover { background-color: rgba(70, 120, 180, 0.4); }
    details[open] summary { border-bottom: 1px solid #555; }
    .arrow-cell { color: #6db3ff; font-weight: bold; text-align: center; }
    .id-cell { color: #6db3ff; font-weight: bold; }
    .details-content { padding: 20px; background-color: rgba(30, 40, 50, 0.8); }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .info-item { color: #fff; }
    .info-label { font-size: 0.85em; color: #888; margin-bottom: 5px; }
    .info-value { font-size: 1.5em; font-weight: bold; color: #fff; }
    .recipe-table, .history-table { width: 100%; margin-top: 10px; border-collapse: collapse; }
    .recipe-table th, .history-table th { background-color: rgba(100, 180, 255, 0.3); padding: 8px; border: 1px solid #666; color: #fff; text-align: left; }
    .recipe-table td, .history-table td { background-color: rgba(50, 50, 60, 0.5); padding: 8px; border: 1px solid #666; color: #ddd; }
    .section-title { color: #fff; font-weight: bold; margin: 15px 0 10px 0; }
    .price-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
    .price-grid-single { display: grid; grid-template-columns: 1fr; gap: 20px; }
    hr { border: none; border-top: 1px solid #666; margin: 20px 0; }
    .craft-yes { color: #5eff5e; }
    .craft-no { color: #ff5e5e; }
    .price-value { color: #ffd966; }
    .not-craftable { color: #888; font-style: italic; }
    .profit-positive { color: #5eff5e; font-weight: bold; }
    .profit-negative { color: #ff5e5e; font-weight: bold; }
    .profit-neutral { color: #888; }
    .method-hdv { color: #64b5f6; font-weight: bold; }
    .method-craft { color: #81c784; font-weight: bold; }
    details .arrow-cell::after { content: '▶'; color: #6db3ff; font-weight: bold; }
    details[open] .arrow-cell::after { content: '▼'; }
    .checkbox-cell input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; accent-color: #6db3ff; }
    
    /* Style pour les boutons de header */
    .stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: #fff !important;
        font-weight: bold !important;
        padding: 0 !important;
        font-family: monospace !important;
        box-shadow: none !important;
        cursor: pointer !important;
        height: auto !important;
        width: auto !important;
    }
    .stButton > button:hover {
        background-color: transparent !important;
        color: #6db3ff !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stButton > button:active,
    .stButton > button:focus {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Container pour le header */
    .header-container {
        display: grid;
        grid-template-columns: 2% 3% 3% 13% 4% 10% 11% 8% 8% 8% 8% 8% 8% 2%;
        column-gap: 6px;
        padding: 16px 8px;
        background-color: rgba(70, 120, 180, 0.5);
        font-weight: bold;
        border: 1px solid #555;
        color: #fff;
        font-family: monospace;
        align-items: center;
    }

    /* Style pour les images */
    .item-image {
        width: 40px;
        height: 40px;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

# --- Google Drive ---
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"
SERVICE_ACCOUNT_FILE = "credentials/service_account.json"

# --- Chargement des XP ---
@st.cache_data
def load_xp_data():
    """Charge les données XP depuis le fichier CSV"""
    try:
        df_xp = pd.read_csv('data/items_xp.csv', delimiter=';')
        # Créer un dictionnaire id -> (xp_1, xp_2)
        xp_dict = {}
        for _, row in df_xp.iterrows():
            item_id = int(row['id'])
            xp_1 = row['xp_1'] if pd.notna(row['xp_1']) else None
            xp_2 = row['xp_2'] if pd.notna(row['xp_2']) else None
            xp_dict[item_id] = (xp_1, xp_2)
        return xp_dict
    except Exception as e:
        st.error(f"Erreur lors du chargement des XP : {e}")
        return {}

# --- Session State defaults ---
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = set()
if 'select_all_checkbox' not in st.session_state:
    st.session_state.select_all_checkbox = False
if 'child_toggled' not in st.session_state:
    st.session_state.child_toggled = False
if 'sort_column' not in st.session_state:
    st.session_state.sort_column = 'id'
if 'sort_ascending' not in st.session_state:
    st.session_state.sort_ascending = True
if 'quantity' not in st.session_state:
    st.session_state.quantity = 1
if 'craft_cache' not in st.session_state:
    st.session_state.craft_cache = {}
if 'scrapper_items' not in st.session_state:
    st.session_state.scrapper_items = []
if 'notification_shown' not in st.session_state:
    st.session_state.notification_shown = False
if 'user_groups' not in st.session_state:
    st.session_state.user_groups = {}
if 'selected_group_action' not in st.session_state:
    st.session_state.selected_group_action = None
if 'selected_group_filters' not in st.session_state:
    st.session_state.selected_group_filters = []

# --- Chargement des données ---
@st.cache_data(ttl=600)
def charger_donnees():
    try:
        drive = GoogleDriveJSON(FILE_ID, SERVICE_ACCOUNT_FILE)
        data = drive.read()
        data = {k: v for k, v in data.items() if str(k).isdigit()}
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None

def get_latest_entry(dico):
    if not dico:
        return None
    try:
        return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
    except Exception:
        return None

@lru_cache(maxsize=10000)
def calculate_optimal_price_cached(prices_tuple, target_quantity):
    """
    Version cachée de calculate_optimal_price.
    prices_tuple est un tuple de tuples ((qty, price), ...) pour être hashable.
    """
    if not prices_tuple:
        return None
    
    available_quantities = dict(prices_tuple)
    
    if not available_quantities:
        return None
    
    # Si la quantité exacte existe
    if target_quantity in available_quantities:
        return int(round(available_quantities[target_quantity]))
    
    # Trier les quantités disponibles
    sorted_quantities = sorted(available_quantities.keys())
    
    # Programmation dynamique pour trouver le prix optimal
    dp = [float('inf')] * (target_quantity + 1)
    dp[0] = 0
    
    for i in range(1, target_quantity + 1):
        # Option 1: Utiliser les quantités inférieures ou égales à i
        for qty, price in available_quantities.items():
            if qty <= i:
                dp[i] = min(dp[i], dp[i - qty] + price)
        
        # Option 2: Acheter directement une quantité supérieure à i
        for qty, price in available_quantities.items():
            if qty > i:
                dp[i] = min(dp[i], price)
    
    if dp[target_quantity] == float('inf'):
        return None
    
    return int(round(dp[target_quantity]))

def calculate_optimal_price(prices_dict, target_quantity):
    """
    Wrapper qui convertit le dict en tuple pour le cache.
    """
    if not prices_dict:
        return None
    
    # Filtrer et convertir en tuple hashable
    valid_prices = []
    for qty_str, price in prices_dict.items():
        if price is not None and price != -1:
            try:
                qty_int = int(qty_str)
                price_float = float(price)
                if price_float > 0:
                    valid_prices.append((qty_int, price_float))
            except (ValueError, TypeError):
                continue
    
    if not valid_prices:
        return None
    
    prices_tuple = tuple(sorted(valid_prices))
    return calculate_optimal_price_cached(prices_tuple, target_quantity)

def calculate_craft_cost_recursive(data, item_id, quantity, memo=None, is_root=True):
    """
    Calcule récursivement le coût de craft d'un item pour une quantité donnée.
    Version optimisée avec cache global.
    
    Args:
        data: Dictionnaire complet des items
        item_id: ID de l'item (int ou str)
        quantity: Quantité désirée (int)
        memo: Dictionnaire de mémoïsation
        is_root: True si c'est l'item principal, False si c'est un ingrédient
    
    Returns:
        (coût_total, méthode) ou (None, None) si impossible
    """
    if memo is None:
        memo = st.session_state.craft_cache
    
    # Vérifier le cache - ajouter is_root à la clé de cache
    cache_key = (str(item_id), quantity, is_root)
    if cache_key in memo:
        return memo[cache_key]
    
    item_id_str = str(item_id)
    if item_id_str not in data:
        memo[cache_key] = (None, None)
        return (None, None)
    
    item = data[item_id_str]
    
    # Calculer le prix HDV
    prix_hdv_dict = get_latest_entry(item.get("prix_hdv", {})) or {}
    prix_hdv = calculate_optimal_price(prix_hdv_dict, quantity)
    
    # Si l'item n'est pas craftable, on retourne le prix HDV
    if not item.get('is_craft') or not item.get('ingredients'):
        result = (prix_hdv, 'HDV') if prix_hdv is not None else (None, None)
        memo[cache_key] = result
        return result
    
    # Calculer le coût de craft en fonction des ingrédients
    craft_cost = 0
    for ingredient in item['ingredients']:
        ing_id = ingredient['id']
        ing_qty_per_craft = ingredient['quantity']
        
        # Quantité totale d'ingrédient nécessaire
        total_ing_qty = ing_qty_per_craft * quantity
        
        # Calculer récursivement le meilleur prix pour cet ingrédient (is_root=False)
        ing_cost, _ = calculate_craft_cost_recursive(data, ing_id, total_ing_qty, memo, is_root=False)
        
        if ing_cost is None:
            craft_cost = None
            break
        
        craft_cost += ing_cost
    
    # Déterminer la meilleure méthode
    if craft_cost is None:
        result = (prix_hdv, 'HDV') if prix_hdv is not None else (None, None)
    elif prix_hdv is None:
        result = (craft_cost, 'Craft')
    else:
        # Si c'est l'item principal (root), on retourne toujours le craft_cost
        if is_root:
            result = (craft_cost, 'Craft')
        else:
            # Pour les ingrédients, on compare et on prend le minimum
            if craft_cost <= prix_hdv:
                result = (craft_cost, 'Craft')
            else:
                result = (prix_hdv, 'HDV')
    
    memo[cache_key] = result
    return result

def precalculate_all_crafts(data, quantity):
    """
    Pré-calcule tous les coûts de craft pour une quantité donnée.
    Cela remplit le cache en une seule passe.
    """
    memo = st.session_state.craft_cache
    
    # Parcourir tous les items
    for item_id in data.keys():
        # Calculer avec is_root=True pour l'item principal
        calculate_craft_cost_recursive(data, item_id, quantity, memo, is_root=True)
        # Calculer aussi avec is_root=False pour quand il sera utilisé comme ingrédient
        calculate_craft_cost_recursive(data, item_id, quantity, memo, is_root=False)

def get_ingredient_details(data, item_id, quantity, memo=None):
    """
    Retourne les détails d'un ingrédient avec son coût optimal.
    """
    if memo is None:
        memo = st.session_state.craft_cache
    
    item_id_str = str(item_id)
    if item_id_str not in data:
        return {
            'id': item_id,
            'name': f"Item #{item_id}",
            'quantity': quantity,
            'cost': None,
            'method': None
        }
    
    item = data[item_id_str]
    # Pour les ingrédients, is_root=False
    cost, method = calculate_craft_cost_recursive(data, item_id, quantity, memo, is_root=False)
    
    return {
        'id': item_id,
        'name': item.get('name', f"Item #{item_id}"),
        'quantity': quantity,
        'cost': cost,
        'method': method
    }

def get_recipe_html(data, item, quantity):
    """
    Génère le HTML de la recette avec les coûts optimaux pour chaque ingrédient.
    """
    if not item.get('ingredients'):
        return "<p style='color: #aaa;'><em>Cet item n'a pas de recette</em></p>"
    
    html = f"<div class='section-title'>🧪 Recette de fabrication (x{quantity})</div>"
    html += "<table class='recipe-table'><tr><th>Ingrédient</th><th>ID</th><th>Quantité</th><th>Coût unitaire</th><th>Coût total</th><th>Méthode</th></tr>"
    
    memo = st.session_state.craft_cache
    total_craft_cost = 0
    
    for ing in item['ingredients']:
        ing_qty_per_craft = ing['quantity']
        total_ing_qty = ing_qty_per_craft * quantity
        
        ing_details = get_ingredient_details(data, ing['id'], total_ing_qty, memo)
        
        # Coût unitaire
        if ing_details['cost'] is not None and total_ing_qty > 0:
            unit_cost = ing_details['cost'] / total_ing_qty
            cost_display = f"{ing_details['cost']} K"
            unit_cost_display = f"{int(round(unit_cost))} K"
            total_craft_cost += ing_details['cost']
        else:
            cost_display = "-"
            unit_cost_display = "-"
        
        method_class = f"method-{ing_details['method'].lower()}" if ing_details['method'] else ""
        method_display = ing_details['method'] if ing_details['method'] else "-"
        
        html += f"<tr><td>{ing_details['name']}</td><td>{ing_details['id']}</td><td>{total_ing_qty}</td><td>{unit_cost_display}</td><td>{cost_display}</td><td class='{method_class}'>{method_display}</td></tr>"
    
    html += f"<tr style='font-weight: bold; background-color: rgba(100, 180, 255, 0.2);'><td colspan='4'>TOTAL</td><td>{int(round(total_craft_cost))} K</td><td></td></tr>"
    html += "</table>"
    
    return html

def get_price_history_html(prix_dict, quantity, title):
    if not prix_dict:
        return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucun historique disponible</em></p></div>"

    # Créer l'en-tête avec les 5 colonnes de quantités
    html = f"<div><div class='section-title'>{title}</div><table class='history-table'>"
    html += f"<tr><th>Date</th><th>x1</th><th>x10</th><th>x100</th><th>x1000</th><th>x{quantity}</th></tr>"

    try:
        sorted_dates = sorted(prix_dict.keys(), key=lambda k: datetime.fromisoformat(k), reverse=True)[:5]
    except:
        sorted_dates = sorted(prix_dict.keys(), reverse=True)[:5]

    has_data = False
    for date in sorted_dates:
        # Récupérer les prix directs depuis le dictionnaire (pas de calcul optimal)
        prices_for_date = prix_dict[date]

        # Extraire les valeurs directes (ou None si absentes)
        price_x1 = prices_for_date.get("1", None) if prices_for_date.get("1", -1) not in [None, -1] else None
        price_x10 = prices_for_date.get("10", None) if prices_for_date.get("10", -1) not in [None, -1] else None
        price_x100 = prices_for_date.get("100", None) if prices_for_date.get("100", -1) not in [None, -1] else None
        price_x1000 = prices_for_date.get("1000", None) if prices_for_date.get("1000", -1) not in [None, -1] else None

        # Pour xQuantité, utiliser calculate_optimal_price
        price_quantity = calculate_optimal_price(prices_for_date, quantity)

        # Afficher la ligne si au moins un prix existe
        if any(p is not None for p in [price_x1, price_x10, price_x100, price_x1000, price_quantity]):
            has_data = True
            try:
                date_formatted = datetime.fromisoformat(date).strftime('%d/%m/%Y %H:%M')
            except:
                date_formatted = date

            # Formater les prix (- si None)
            p1 = f"{int(price_x1)} K" if price_x1 is not None else "-"
            p10 = f"{int(price_x10)} K" if price_x10 is not None else "-"
            p100 = f"{int(price_x100)} K" if price_x100 is not None else "-"
            p1000 = f"{int(price_x1000)} K" if price_x1000 is not None else "-"
            pq = f"{price_quantity} K" if price_quantity is not None else "-"

            html += f"<tr><td>{date_formatted}</td><td>{p1}</td><td>{p10}</td><td>{p100}</td><td>{p1000}</td><td>{pq}</td></tr>"

    html += "</table></div>"
    if not has_data:
        return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucune donnée disponible</em></p></div>"
    return html

def create_item_html(item, data, quantity, xp_data):
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    prix_val = calculate_optimal_price(prix, quantity)

    # Calculer le coût de craft dynamiquement (avec cache)
    is_craftable = item.get('is_craft') and item.get('ingredients')

    if is_craftable:
        # Pour l'item principal, is_root=True
        craft_val, craft_method = calculate_craft_cost_recursive(data, item.get('id'), quantity, is_root=True)
        craft_display = f"{craft_val}" if craft_val is not None else '-'
    else:
        craft_val = None
        craft_display = '<span class="not-craftable">Non Fabriquable</span>'

    prix_display = f"{prix_val}" if prix_val is not None else '-'

    # Calcul de la rentabilité
    if is_craftable and prix_val is not None and craft_val is not None:
        profit_flat = prix_val - craft_val
        profit_percent = (profit_flat / craft_val * 100) if craft_val > 0 else 0

        profit_class = 'profit-positive' if profit_flat > 0 else ('profit-negative' if profit_flat < 0 else 'profit-neutral')
        profit_flat_display = f'<span class="{profit_class}">{profit_flat:+d}</span>'
        profit_percent_display = f'<span class="{profit_class}">{profit_percent:+.1f}%</span>'
    else:
        profit_flat_display = '-'
        profit_percent_display = '-'

    # Calculer XP et XP/10kk
    item_int_id = item.get('id')
    xp_display = '-'
    xp_per_10kk_display = '-'

    if item_int_id in xp_data:
        xp_1, xp_2 = xp_data[item_int_id]
        xp_value = xp_1 if xp_1 is not None else xp_2

        if xp_value is not None:
            # Multiplier l'XP par la quantité
            total_xp = xp_value * quantity
            xp_display = f"{total_xp:.2f}"

            min_cost = None
            if prix_val is not None and craft_val is not None:
                min_cost = min(prix_val, craft_val)
            elif prix_val is not None:
                min_cost = prix_val
            elif craft_val is not None:
                min_cost = craft_val

            if min_cost is not None and min_cost > 0:
                xp_per_10kk = (total_xp / min_cost) * 10000
                xp_per_10kk_display = f"{xp_per_10kk:.1f}"

    last_maj = item.get('last_maj', 'N/A')
    if last_maj != 'N/A':
        try:
            last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
        except:
            pass

    html = f"""
    <details>
    <summary>
        <div class="arrow-cell"></div>
        <div class="id-cell">{item.get('id')}</div>
        <div><img src="https://api.dofusdb.fr/img/items/{item.get('iconId', item.get('id'))}.png" class="item-image" alt="{item.get('name')}"></div>
        <div class="item-name">{item.get('name')} </div>
        <div class="item-info">{item.get('level')}</div>
        <div class="item-info">{item.get('supertype', 'N/A')}</div>
        <div class="item-info">{item.get('type', 'N/A')}</div>
        <div class="price-value">{prix_display}</div>
        <div class="price-value">{craft_display}</div>
        <div class="price-value">{profit_flat_display}</div>
        <div class="price-value">{profit_percent_display}</div>
        <div class="price-value">{xp_display}</div>
        <div class="price-value">{xp_per_10kk_display}</div>
    </summary>
    <div class='details-content'>
        <div class='info-grid'>
            <div class='info-item'>
                <div class='info-label'>ID</div><div class='info-value'>{item['id']}</div>
                <div class='info-label' style='margin-top: 10px;'>Niveau</div><div class='info-value'>{item['level']}</div>
            </div>
            <div class='info-item'>
                <div class='info-label'>Supertype</div><div class='info-value'>{item.get('supertype', 'N/A')}</div>
                <div class='info-label' style='margin-top: 10px;'>Type</div><div class='info-value'>{item.get('type', 'N/A')}</div>
            </div>
            <div class='info-item'>
                <div class='info-label'>Craftable</div>
                <div class='info-value'>{"Oui ✓" if item.get('is_craft') else "Non ✗"}</div>
                <div class='info-label' style='margin-top: 10px;'>Dernière MAJ</div>
                <div class='info-value'>{last_maj}</div>
            </div>
        </div>
        <hr>
    """
    if item.get('is_craft') and item.get('ingredients'):
        html += get_recipe_html(data, item, quantity) + "<hr>"

    # Pour les objets non craftables, utiliser une seule colonne
    grid_class = 'price-grid' if item.get('is_craft') and item.get('ingredients') else 'price-grid-single'
    price_history = get_price_history_html(item.get('prix_hdv', {}), quantity, "📊 Prix HDV")
    html += f"""<div class='{grid_class}'>{price_history}</div></div></details>"""
    return html

# --- PAGE ---
with st.spinner("Chargement des données depuis Google Drive..."):
    data = charger_donnees()

if not data:
    st.error("❌ Impossible de charger les données")
    st.stop()

# Toujours charger les groupes de l'utilisateur (cache géré dans get_user_groups)
st.session_state.user_groups = get_user_groups()

# Charger les données XP
xp_data = load_xp_data()

if not st.session_state.notification_shown:
    st.toast(f"✅ {len(data)} items chargés avec succès", icon="✅")
    st.session_state.notification_shown = True

# --- Sidebar ---
with st.sidebar:

    # Contrôle de la quantité
    quantity = st.number_input(
        "Quantité",
        min_value=1,
        max_value=100000,
        value=st.session_state.quantity,
        step=1,
        key="quantity_input"
    )
    # Mettre à jour le session_state si la valeur change
    if quantity != st.session_state.quantity:
        st.session_state.quantity = quantity
        # Vider le cache si la quantité change
        st.session_state.craft_cache = {}

    # Filtre par groupes
    group_options = {group_id: f"{group_data['name']} ({group_data['owner']})"
                     for group_id, group_data in st.session_state.user_groups.items()}
    selected_group_filters = st.multiselect(
        "Filtrer par groupe(s)",
        options=list(group_options.keys()),
        format_func=lambda x: group_options[x],
        key="group_filter_multiselect"
    )

    search_term = st.text_input("🔍 Rechercher par nom ou ID", "")
    all_supertypes = sorted(set(item.get('supertype', 'N/A') for item in data.values()))
    supertype_filter = st.multiselect("Supertype", options=all_supertypes)
    all_types = sorted(set(item.get('type', 'N/A') for item in data.values()))
    type_filter = st.multiselect("Type", options=all_types)
    all_jobs = sorted(set(item.get('job') for item in data.values() if item.get('job')))
    job_filter = st.multiselect("Métier", options=all_jobs)
    craft_filter = st.radio("Type d'item", ["Tous", "Craftables uniquement", "Non craftables"])
    xp_filter = st.checkbox("📚 XP connu uniquement")
    max_level = max((item.get('level', 0) for item in data.values()), default=200)
    level_range = st.slider("Niveau", 1, max_level, (1, max_level))

# Pré-calculer tous les crafts pour cette quantité (uniquement si le cache est vide)
if not st.session_state.craft_cache:
    with st.spinner(f"Calcul des coûts de craft pour la quantité {quantity}..."):
        precalculate_all_crafts(data, quantity)

# --- Filtrage ---
rows = []
for item_id, item in data.items():
    # Extraire les prix pour la quantité sélectionnée
    prix_dict = get_latest_entry(item.get("prix_hdv", {})) or {}
    prix_val = calculate_optimal_price(prix_dict, quantity)
    
    # Calculer dynamiquement le coût de craft (depuis le cache)
    is_craftable = item.get('is_craft') and item.get('ingredients')
    if is_craftable:
        craft_val, _ = calculate_craft_cost_recursive(data, item.get('id'), quantity, is_root=True)
    else:
        craft_val = None
    
    # Calculer la rentabilité
    if is_craftable and prix_val is not None and craft_val is not None:
        profit_flat = prix_val - craft_val
        profit_percent = (profit_flat / craft_val * 100) if craft_val > 0 else 0
    else:
        profit_flat = None
        profit_percent = None
    
    # Calculer XP et XP/10kk
    item_int_id = item.get('id')
    xp_value = None
    xp_per_10kk = None

    if item_int_id in xp_data:
        xp_1, xp_2 = xp_data[item_int_id]
        xp_value_single = xp_1 if xp_1 is not None else xp_2

        if xp_value_single is not None:
            # Multiplier l'XP par la quantité
            xp_value = xp_value_single * quantity

            # Déterminer le coût minimum
            min_cost = None
            if prix_val is not None and craft_val is not None:
                min_cost = min(prix_val, craft_val)
            elif prix_val is not None:
                min_cost = prix_val
            elif craft_val is not None:
                min_cost = craft_val

            if min_cost is not None and min_cost > 0:
                xp_per_10kk = (xp_value / min_cost) * 10000

    # Convertir en float pour le tri (None devient inf)
    prix_numeric = float(prix_val) if prix_val is not None else float('inf')
    craft_numeric = float(craft_val) if craft_val is not None else float('inf')
    profit_flat_numeric = float(profit_flat) if profit_flat is not None else float('-inf')
    profit_percent_numeric = float(profit_percent) if profit_percent is not None else float('-inf')
    xp_numeric = float(xp_value) if xp_value is not None else float('-inf')
    xp_per_10kk_numeric = float(xp_per_10kk) if xp_per_10kk is not None else float('-inf')

    rows.append({
        "id": item.get("id"),
        "name": item.get("name"),
        "level": item.get("level"),
        "supertype": item.get("supertype"),
        "type": item.get("type"),
        "job": item.get("job"),
        "is_craft": item.get("is_craft"),
        "prix_hdv": prix_numeric,
        "cout_craft": craft_numeric,
        "profit_flat": profit_flat_numeric,
        "profit_percent": profit_percent_numeric,
        "xp": xp_numeric,
        "xp_per_10kk": xp_per_10kk_numeric,
        "_item_id": item_id
    })

df = pd.DataFrame(rows)

if search_term:
    df = df[df["name"].str.contains(search_term, case=False, na=False) | df["id"].astype(str).str.contains(search_term)]
if supertype_filter:
    df = df[df["supertype"].isin(supertype_filter)]
if type_filter:
    df = df[df["type"].isin(type_filter)]
if job_filter:
    df = df[df["job"].isin(job_filter)]
if craft_filter == "Craftables uniquement":
    df = df[df["is_craft"]]
elif craft_filter == "Non craftables":
    df = df[~df["is_craft"]]
if xp_filter:
    df = df[df["xp"] != float('-inf')]
# Filtre par groupe(s)
if selected_group_filters:
    group_items = get_items_in_groups(selected_group_filters)
    df = df[df["id"].isin(group_items)]
df = df[(df["level"] >= level_range[0]) & (df["level"] <= level_range[1])]

# Tri basé sur le session state
df_display = df.sort_values(by=st.session_state.sort_column, ascending=st.session_state.sort_ascending).reset_index(drop=True)

items_per_page = 20
total_pages = max((len(df_display) - 1) // items_per_page + 1, 1)

# Afficher les boutons, les compteurs et la pagination sur la même ligne
col_refresh, col_group_select, col_group_add, col_group_remove, col_scrapper, col_display, col_page = st.columns([0.5, 1.2, 0.6, 0.6, 0.8, 1.8, 0.6])

with col_refresh:
    if st.button("🔄", help="Rafraîchir"):
        st.cache_data.clear()
        st.session_state.craft_cache = {}
        calculate_optimal_price_cached.cache_clear()
        st.rerun()

with col_group_select:
    # Sélecteur de groupe pour les actions
    if st.session_state.user_groups:
        group_options_action = {gid: gdata['name'] for gid, gdata in st.session_state.user_groups.items()}

        # Initialiser la sélection si elle n'existe pas
        if 'selected_group_for_action' not in st.session_state:
            st.session_state.selected_group_for_action = list(group_options_action.keys())[0] if group_options_action else None

        selected_group_action = st.selectbox(
            "Groupe",
            options=list(group_options_action.keys()),
            format_func=lambda x: group_options_action[x],
            index=list(group_options_action.keys()).index(st.session_state.selected_group_for_action) if st.session_state.selected_group_for_action in group_options_action else 0,
            key="group_action_select_widget",
            label_visibility="collapsed",
            on_change=lambda: st.session_state.update({'selected_group_for_action': st.session_state.group_action_select_widget})
        )
    else:
        selected_group_action = None
        st.info("Aucun groupe")

with col_group_add:
    if st.button("➕ Groupe", help="Ajouter au groupe"):
        if st.session_state.selected_items and selected_group_action:
            added_count = add_items_to_group(selected_group_action, list(st.session_state.selected_items))

            if added_count > 0:
                st.toast(f"✓ {added_count} item(s) ajouté(s) au groupe", icon="✅")
            else:
                st.toast("⚠️ Item(s) déjà dans le groupe", icon="ℹ️")
        elif not st.session_state.selected_items:
            st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
        else:
            st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

with col_group_remove:
    if st.button("➖ Groupe", help="Retirer du groupe"):
        if st.session_state.selected_items and selected_group_action:
            removed_count = remove_items_from_group(selected_group_action, list(st.session_state.selected_items))

            if removed_count > 0:
                st.toast(f"✓ {removed_count} item(s) retiré(s) du groupe", icon="✅")
            else:
                st.toast("⚠️ Aucun item à retirer du groupe", icon="ℹ️")
        elif not st.session_state.selected_items:
            st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
        else:
            st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

with col_scrapper:
    if st.button("➕ Scrapper", help="Ajouter au scrapper"):
        if st.session_state.selected_items:
            # Ajouter les items au fichier JSON avec extraction automatique des ingrédients
            added_count = add_items_to_scrapper(list(st.session_state.selected_items), data=data)

            if added_count > 0:
                st.toast(f"✓ {added_count} item(s) ajouté(s) au scrapper (+ ingrédients)", icon="✅")
            else:
                st.toast("⚠️ Item(s) déjà présent dans le scrapper", icon="ℹ️")
        else:
            st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")

with col_display:
    st.markdown(f"<div style='padding-top: 10px;'><b>Affichage : {len(df_display)} / {len(data)} items</b></div>", unsafe_allow_html=True)

with col_page:
    current_page = st.number_input(f"Page (1-{total_pages})", 1, total_pages, 1)

start_idx, end_idx = (current_page - 1) * items_per_page, min(current_page * items_per_page, len(df_display))
df_page = df_display.iloc[start_idx:end_idx]
def make_child_changed(widget_key, item_real_id):
    def _child_changed():
        if st.session_state.get(widget_key):
            st.session_state.selected_items.add(item_real_id)
        else:
            st.session_state.selected_items.discard(item_real_id)
        st.session_state.child_toggled = True
    return _child_changed

def master_changed():
    checked = st.session_state.get("select_all_checkbox", False)
    # ✅ Tous les items filtrés
    all_filtered_ids = df_display['id'].tolist()
    if checked:
        st.session_state.selected_items.update(all_filtered_ids)
    else:
        st.session_state.selected_items.clear()
    # Synchroniser les cases visibles
    for _, row in df_page.iterrows():
        item_id = row['_item_id']
        widget_key = f"check_{item_id}_{current_page}"
        st.session_state[widget_key] = checked
    st.session_state.child_toggled = False

# --- Callbacks pour les boutons de header ---
def header_clicked(column_name):
    def _callback():
        if st.session_state.sort_column == column_name:
            # Toggle l'ordre si on clique sur la même colonne
            st.session_state.sort_ascending = not st.session_state.sort_ascending
        else:
            # Nouvelle colonne : commence par décroissant
            st.session_state.sort_column = column_name
            st.session_state.sort_ascending = False
    return _callback

def get_sort_arrow(column_name):
    if st.session_state.sort_column == column_name:
        return " ▼" if not st.session_state.sort_ascending else " ▲"
    return ""

# --- Header avec checkbox maître et boutons ---
col_header_check, col_header_content = st.columns([0.03, 9.97])

if st.session_state.get("child_toggled", False):
    visible_ids = set(df_page['id'].tolist())
    st.session_state.select_all_checkbox = visible_ids.issubset(st.session_state.selected_items)
    st.session_state.child_toggled = False

with col_header_check:
    st.checkbox("Tout", key="select_all_checkbox", on_change=master_changed, label_visibility="collapsed")

with col_header_content:
    # Création d'une grille pour les boutons de header - alignement parfait
    header_cols = st.columns([0.02, 0.03, 0.04, 0.13, 0.05, 0.10, 0.11, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.02])

    with header_cols[0]:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    with header_cols[1]:
        st.button(f"ID{get_sort_arrow('id')}", key="btn_header_id", on_click=header_clicked('id'))

    with header_cols[2]:
        st.markdown("<div style='text-align: center; padding-top: 10px;'><b>Image</b></div>", unsafe_allow_html=True)

    with header_cols[3]:
        st.button(f"Nom{get_sort_arrow('name')}", key="btn_header_nom", on_click=header_clicked('name'))

    with header_cols[4]:
        st.button(f"Niveau{get_sort_arrow('level')}", key="btn_header_niveau", on_click=header_clicked('level'))

    with header_cols[5]:
        st.button(f"Supertype{get_sort_arrow('supertype')}", key="btn_header_supertype", on_click=header_clicked('supertype'))

    with header_cols[6]:
        st.button(f"Type{get_sort_arrow('type')}", key="btn_header_type", on_click=header_clicked('type'))

    with header_cols[7]:
        st.button(f"Prix HDV{get_sort_arrow('prix_hdv')}", key="btn_header_prix_hdv", on_click=header_clicked('prix_hdv'))

    with header_cols[8]:
        st.button(f"Coût Craft{get_sort_arrow('cout_craft')}", key="btn_header_cout_craft", on_click=header_clicked('cout_craft'))

    with header_cols[9]:
        st.button(f"Rentab. K{get_sort_arrow('profit_flat')}", key="btn_header_profit_flat", on_click=header_clicked('profit_flat'))

    with header_cols[10]:
        st.button(f"Rentab. %{get_sort_arrow('profit_percent')}", key="btn_header_profit_percent", on_click=header_clicked('profit_percent'))

    with header_cols[11]:
        st.button(f"XP{get_sort_arrow('xp')}", key="btn_header_xp", on_click=header_clicked('xp'))

    with header_cols[12]:
        st.button(f"XP/10kk{get_sort_arrow('xp_per_10kk')}", key="btn_header_xp_per_10kk", on_click=header_clicked('xp_per_10kk'))

# --- Affichage des items ---
if len(df_page) > 0:
    for _, row in df_page.iterrows():
        item_id = row['_item_id']
        item = data[item_id]
        item_real_id = item.get('id')
        col_check, col_content = st.columns([0.03, 9.97])

        with col_check:
            widget_key = f"check_{item_real_id}_{current_page}"
            st.session_state[widget_key] = (item_real_id in st.session_state.selected_items)
            st.checkbox("option technique", key=widget_key, on_change=make_child_changed(widget_key, item_real_id), label_visibility="collapsed")

        with col_content:
            st.markdown(create_item_html(item, data, quantity, xp_data), unsafe_allow_html=True)
else:
    st.info("Aucun résultat ne correspond à vos critères de recherche.")

# --- Statistiques et actions ---
st.markdown("---")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric("Total items", len(data))
with col_stat2:
    st.metric("Items craftables", sum(1 for item in data.values() if item.get('is_craft')))
with col_stat3:
    st.metric("Prix HDV disponibles", sum(1 for item in data.values() if item.get('prix_hdv')))
with col_stat4:
    st.metric("Coûts craft disponibles", sum(1 for item in data.values() if item.get('cout_craft')))