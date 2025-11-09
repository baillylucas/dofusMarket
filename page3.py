import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON

# Configuration pour occuper toute la largeur
st.set_page_config(layout="wide")

# Initialisation de l'état de session pour les checkboxes
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = set()
if 'select_all' not in st.session_state:
    st.session_state.select_all = False

st.markdown("# Page 3")
st.sidebar.markdown("# Page 3")

# CSS personnalisé pour styler les éléments <details>
st.markdown("""
<style>
    /* Style des details/summary (expanders natifs HTML) */
    details {
        border: 1px solid #555;
        border-top: none;
        border-radius: 0;
        margin: 0;
        background-color: rgba(40, 50, 60, 0.6);
    }
    
    details:first-of-type {
        border-top: 1px solid #555;
    }
    
    summary {
        display: grid;
        grid-template-columns: 3% 7% 21% 8% 12% 12% 8% 13% 13%;
        gap: 8px;
        padding: 16px 12px;
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
    
    summary::-webkit-details-marker {
        display: none;
    }
    
    summary::marker {
        display: none;
    }
    
    summary:hover {
        background-color: rgba(70, 120, 180, 0.4);
    }
    
    details[open] summary {
        border-bottom: 1px solid #555;
    }
    
    /* Gestion de la flèche et de l'ID */
    .arrow-cell {
        color: #6db3ff;
        font-weight: bold;
        text-align: center;
    }
    
    .id-cell {
        color: #6db3ff;
        font-weight: bold;
    }
    
    .details-content {
        padding: 20px;
        background-color: rgba(30, 40, 50, 0.8);
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .info-item {
        color: #fff;
    }
    
    .info-label {
        font-size: 0.85em;
        color: #888;
        margin-bottom: 5px;
    }
    
    .info-value {
        font-size: 1.5em;
        font-weight: bold;
        color: #fff;
    }
    
    .recipe-table, .history-table {
        width: 100%;
        margin-top: 10px;
        border-collapse: collapse;
    }
    
    .recipe-table th, .history-table th {
        background-color: rgba(100, 180, 255, 0.3);
        padding: 8px;
        border: 1px solid #666;
        color: #fff;
        text-align: left;
    }
    
    .recipe-table td, .history-table td {
        background-color: rgba(50, 50, 60, 0.5);
        padding: 8px;
        border: 1px solid #666;
        color: #ddd;
    }
    
    .section-title {
        color: #fff;
        font-weight: bold;
        margin: 15px 0 10px 0;
    }
    
    .price-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    
    hr {
        border: none;
        border-top: 1px solid #666;
        margin: 20px 0;
    }
    
    .arrow-cell {
        color: #6db3ff;
        font-weight: bold;
    }
    
    .item-name {
        color: #fff;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .item-info {
        color: #ddd;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .craft-yes {
        color: #5eff5e;
    }
    
    .craft-no {
        color: #ff5e5e;
    }
    
    .price-value {
        color: #ffd966;
    }
    
    /* Animation de la flèche avec CSS pur */
    details .arrow-cell::after {
        content: '▶';
        color: #6db3ff;
        font-weight: bold;
    }
    
    details[open] .arrow-cell::after {
        content: '▼';
    }
    
    .arrow-cell {
        color: #6db3ff;
        font-weight: bold;
        text-align: center;
    }
    
    /* Style pour les colonnes avec checkboxes */
    .stCheckbox {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div[data-testid="column"] {
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuration Google Drive
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

@st.cache_data(ttl=600)
def charger_donnees():
    """Charge les données depuis Google Drive"""
    try:
        drive = GoogleDriveJSON(FILE_ID)
        data = drive.read()
        # Garder uniquement les clés numériques
        data = {k: v for k, v in data.items() if str(k).isdigit()}
        return data
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return None

def get_latest_entry(dico):
    """Récupère l'entrée la plus récente d'un dictionnaire daté"""
    if not dico:
        return None
    try:
        return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
    except Exception:
        return None

def get_ingredient_name(data, ingredient_id):
    """Récupère le nom d'un ingrédient par son ID"""
    item_id = str(ingredient_id)
    if item_id in data:
        return data[item_id].get('name', f"Item #{ingredient_id}")
    return f"Item #{ingredient_id}"

def get_recipe_html(data, item):
    """Génère le HTML de la recette"""
    if not item.get('ingredients'):
        return "<p style='color: #aaa;'><em>Cet item n'a pas de recette</em></p>"
    
    html = "<div class='section-title'>🧪 Recette de fabrication</div>"
    html += "<table class='recipe-table'>"
    html += "<tr><th>Ingrédient</th><th>ID</th><th>Quantité</th></tr>"
    
    for ing in item['ingredients']:
        ing_name = get_ingredient_name(data, ing['id'])
        html += f"<tr><td>{ing_name}</td><td>{ing['id']}</td><td>{ing['quantity']}</td></tr>"
    
    html += "</table>"
    return html

def get_price_history_html(prix_dict, quantity, title):
    """Génère le HTML de l'historique des prix"""
    if not prix_dict:
        return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucun historique disponible</em></p></div>"
    
    html = f"<div><div class='section-title'>{title}</div>"
    html += "<table class='history-table'>"
    html += "<tr><th>Date</th><th>Prix</th></tr>"
    
    try:
        sorted_dates = sorted(prix_dict.keys(), key=lambda k: datetime.fromisoformat(k), reverse=True)[:5]
    except:
        sorted_dates = sorted(prix_dict.keys(), reverse=True)[:5]
    
    has_data = False
    for date in sorted_dates:
        price = prix_dict[date].get(str(quantity))
        if price is not None:
            has_data = True
            try:
                date_formatted = datetime.fromisoformat(date).strftime('%d/%m/%Y %H:%M')
            except:
                date_formatted = date
            html += f"<tr><td>{date_formatted}</td><td>{price} K</td></tr>"
    
    html += "</table></div>"
    
    if not has_data:
        return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucune donnée pour la quantité x{quantity}</em></p></div>"
    
    return html

def create_item_html(item, data, quantity):
    """Crée le HTML complet d'un item avec <details>"""
    
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft = get_latest_entry(item.get("cout_craft", {})) or {}
    
    prix_val = prix.get(str(quantity), '-')
    craft_val = craft.get(str(quantity), '-')
    craft_icon = '✓' if item.get('is_craft') else '✗'
    craft_class = 'craft-yes' if item.get('is_craft') else 'craft-no'
    
    last_maj = item.get('last_maj', 'N/A')
    if last_maj != 'N/A':
        try:
            last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
        except:
            pass
    
    # Contenu du summary (header)
    html = "<details>"
    html += f"""
    <summary>
        <div class="arrow-cell"></div>
        <div class="id-cell">{item.get('id')}</div>
        <div class="item-name">{item.get('name')}</div>
        <div class="item-info">{item.get('level')}</div>
        <div class="item-info">{item.get('supertype', 'N/A')}</div>
        <div class="item-info">{item.get('type', 'N/A')}</div>
        <div class="{craft_class}">{craft_icon}</div>
        <div class="price-value">{prix_val}</div>
        <div class="price-value">{craft_val}</div>
    </summary>
    """
    
    # Contenu détaillé
    html += "<div class='details-content'>"
    
    # Informations générales
    html += "<div class='info-grid'>"
    html += f"""
        <div class='info-item'>
            <div class='info-label'>ID</div>
            <div class='info-value'>{item['id']}</div>
            <div class='info-label' style='margin-top: 10px;'>Niveau</div>
            <div class='info-value'>{item['level']}</div>
        </div>
        <div class='info-item'>
            <div class='info-label'>Supertype</div>
            <div class='info-value'>{item.get('supertype', 'N/A')}</div>
            <div class='info-label' style='margin-top: 10px;'>Type</div>
            <div class='info-value'>{item.get('type', 'N/A')}</div>
        </div>
        <div class='info-item'>
            <div class='info-label'>Craftable</div>
            <div class='info-value'>{"Oui ✓" if item.get('is_craft') else "Non ✗"}</div>
            <div class='info-label' style='margin-top: 10px;'>Dernière MAJ</div>
            <div class='info-value'>{last_maj}</div>
        </div>
    """
    html += "</div>"
    
    html += "<hr>"
    
    # Recette si craftable
    if item.get('is_craft') and item.get('ingredients'):
        html += get_recipe_html(data, item)
        html += "<hr>"
    
    # Historiques de prix
    html += "<div class='price-grid'>"
    html += get_price_history_html(item.get('prix_hdv', {}), quantity, f"📊 Prix HDV (x{quantity})")
    html += get_price_history_html(item.get('cout_craft', {}), quantity, f"📊 Coût Craft (x{quantity})")
    html += "</div>"
    
    html += "</div>"
    html += "</details>"
    
    return html

# --- CHARGEMENT DES DONNÉES ---
st.title("🎮 Encyclopédie des Items")

with st.spinner("Chargement des données depuis Google Drive..."):
    data = charger_donnees()

if data is None or len(data) == 0:
    st.error("❌ Impossible de charger les données")
    st.stop()

st.success(f"✅ {len(data)} items chargés avec succès")

# Bouton de rafraîchissement
col_refresh, col_empty = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Rafraîchir"):
        st.cache_data.clear()
        st.rerun()

# --- SIDEBAR : PARAMÈTRES ET FILTRES ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    # Sélecteur de quantité
    quantity = st.selectbox(
        "Quantité pour les prix",
        options=[1, 10, 100, 1000],
        index=1
    )
    
    st.markdown("---")
    st.markdown("### 📋 Filtres")
    
    # Recherche
    search_term = st.text_input("🔍 Rechercher par nom ou ID", "")
    
    # Filtres par supertype et type
    all_supertypes = sorted(set(item.get('supertype', 'N/A') for item in data.values()))
    supertype_filter = st.multiselect(
        "Supertype",
        options=all_supertypes,
        default=[]
    )
    
    all_types = sorted(set(item.get('type', 'N/A') for item in data.values()))
    type_filter = st.multiselect(
        "Type",
        options=all_types,
        default=[]
    )
    
    # Filtre craftable
    craft_filter = st.radio(
        "Type d'item",
        options=["Tous", "Craftables uniquement", "Non craftables"],
        index=0
    )
    
    # Filtre par niveau
    max_level = max((item.get('level', 0) for item in data.values()), default=200)
    level_range = st.slider(
        "Niveau",
        min_value=1,
        max_value=max_level,
        value=(1, max_level)
    )

# --- TRANSFORMATION EN DATAFRAME POUR FILTRAGE ---
rows = []
for item_id, item in data.items():
    rows.append({
        "id": item.get("id"),
        "name": item.get("name"),
        "level": item.get("level"),
        "supertype": item.get("supertype"),
        "type": item.get("type"),
        "is_craft": item.get("is_craft"),
        "_item_id": item_id
    })

df = pd.DataFrame(rows)

# --- APPLICATION DES FILTRES ---
if search_term:
    df = df[
        df["name"].str.contains(search_term, case=False, na=False) |
        df["id"].astype(str).str.contains(search_term, na=False)
    ]

if supertype_filter:
    df = df[df["supertype"].isin(supertype_filter)]

if type_filter:
    df = df[df["type"].isin(type_filter)]

if craft_filter == "Craftables uniquement":
    df = df[df["is_craft"] == True]
elif craft_filter == "Non craftables":
    df = df[df["is_craft"] == False]

df = df[(df["level"] >= level_range[0]) & (df["level"] <= level_range[1])]

# --- TRI ---
st.markdown(f"### 📦 Items ({len(df)} résultats)")

col_sort1, col_sort2 = st.columns(2)
with col_sort1:
    sort_column = st.selectbox(
        "Trier par",
        options=['id', 'name', 'level', 'supertype', 'type'],
        index=1
    )

with col_sort2:
    sort_order = st.radio(
        "Ordre",
        options=['Croissant', 'Décroissant'],
        horizontal=True,
        index=0
    )

ascending = (sort_order == 'Croissant')
df_display = df.sort_values(by=sort_column, ascending=ascending).reset_index(drop=True)

# --- PAGINATION ---
items_per_page = st.selectbox("Items par page", [10, 20, 50, 100], index=1)
total_pages = max((len(df_display) - 1) // items_per_page + 1, 1)

col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
with col_page2:
    current_page = st.number_input(
        f"Page (1-{total_pages})",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

start_idx = (current_page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, len(df_display))

df_page = df_display.iloc[start_idx:end_idx]

# --- EN-TÊTE DU TABLEAU AVEC CHECKBOX ---
col_header_check, col_header_content = st.columns([0.04, 0.96])

with col_header_check:
    # Checkbox "Sélectionner tout"
    items_on_page = [row['_item_id'] for _, row in df_page.iterrows()]
    all_selected = all(item_id in st.session_state.selected_items for item_id in items_on_page) if items_on_page else False
    
    select_all = st.checkbox("", value=all_selected, key=f"select_all_{current_page}", label_visibility="collapsed")
    
    if select_all:
        st.session_state.selected_items.update(items_on_page)
    else:
        # Si on décoche, retirer uniquement les items de la page courante
        if not all_selected:  # Si on vient de décocher
            st.session_state.selected_items.difference_update(items_on_page)

with col_header_content:
    st.markdown("""
    <div style="display: grid; grid-template-columns: 3% 7% 21% 8% 12% 12% 8% 13% 13%; gap: 8px; padding: 16px 12px; background-color: rgba(70, 120, 180, 0.5); font-weight: bold; border: 1px solid #555; border-radius: 0; font-family: monospace; color: #fff; margin-bottom: 0;">
        <div></div>
        <div>ID</div>
        <div>Nom</div>
        <div>Niveau</div>
        <div>Supertype</div>
        <div>Type</div>
        <div>Craft</div>
        <div>Prix HDV</div>
        <div>Coût Craft</div>
    </div>
    """, unsafe_allow_html=True)

# --- AFFICHAGE DES ITEMS AVEC <DETAILS> ET CHECKBOXES ---
if len(df_page) > 0:
    for idx, row in df_page.iterrows():
        item_id = row['_item_id']
        item = data[item_id]
        
        col_check, col_item = st.columns([0.04, 0.96])
        
        with col_check:
            is_selected = item_id in st.session_state.selected_items
            checked = st.checkbox("", value=is_selected, key=f"check_{item_id}_{current_page}", label_visibility="collapsed")
            
            if checked:
                st.session_state.selected_items.add(item_id)
            else:
                st.session_state.selected_items.discard(item_id)
        
        with col_item:
            st.markdown(create_item_html(item, data, quantity), unsafe_allow_html=True)
else:
    st.info("Aucun résultat ne correspond à vos critères de recherche.")

# --- AFFICHAGE DE LA SÉLECTION ---
if st.session_state.selected_items:
    st.markdown("---")
    col_selected1, col_selected2 = st.columns([4, 1])
    with col_selected1:
        st.info(f"🎯 {len(st.session_state.selected_items)} item(s) sélectionné(s)")
    with col_selected2:
        if st.button("🗑️ Effacer la sélection"):
            st.session_state.selected_items.clear()
            st.rerun()

# --- STATISTIQUES ---
st.markdown("---")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric("Total items", len(data))

with col_stat2:
    craftable_count = sum(1 for item in data.values() if item.get('is_craft'))
    st.metric("Items craftables", craftable_count)

with col_stat3:
    with_hdv = sum(1 for item in data.values() if item.get('prix_hdv'))
    st.metric("Prix HDV disponibles", with_hdv)

with col_stat4:
    with_craft = sum(1 for item in data.values() if item.get('cout_craft'))
    st.metric("Coûts craft disponibles", with_craft)