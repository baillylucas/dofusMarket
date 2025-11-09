import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON

st.markdown("# Page 4")
st.sidebar.markdown("# Page 4")

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

def display_item_row(item, item_id, data, quantity):
    """Affiche une ligne d'item avec plusieurs dropdowns"""
    
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft = get_latest_entry(item.get("cout_craft", {})) or {}
    
    prix_val = prix.get(str(quantity), '-')
    craft_val = craft.get(str(quantity), '-')
    craft_icon = '✓' if item.get('is_craft') else '✗'
    
    # Container pour la ligne complète
    with st.container():
        # Ligne principale avec les infos de base
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.6, 2.5, 0.6, 1.2, 1.2, 0.6, 1.2, 1.2])
        
        with col1:
            st.markdown(f"**{item.get('id')}**")
        with col2:
            st.markdown(f"**{item.get('name')}**")
        with col3:
            st.markdown(f"{item.get('level')}")
        with col4:
            st.markdown(f"{item.get('supertype', 'N/A')}")
        with col5:
            st.markdown(f"{item.get('type', 'N/A')}")
        with col6:
            st.markdown(f"{craft_icon}")
        with col7:
            st.markdown(f"{prix_val}")
        with col8:
            st.markdown(f"{craft_val}")
        
        # Ligne de dropdowns (3 expanders côte à côte)
        col_drop1, col_drop2, col_drop3 = st.columns(3)
        
        # Dropdown 1: Ingrédients (recette)
        with col_drop1:
            if item.get('is_craft') and item.get('ingredients'):
                with st.expander("🧪 Recette", expanded=False):
                    recipe_data = []
                    for ing in item['ingredients']:
                        ing_name = get_ingredient_name(data, ing['id'])
                        recipe_data.append({
                            'Ingrédient': ing_name,
                            'ID': ing['id'],
                            'Qté': ing['quantity']
                        })
                    
                    df_recipe = pd.DataFrame(recipe_data)
                    st.dataframe(
                        df_recipe,
                        width='stretch',
                        hide_index=True,
                        height=min(len(recipe_data) * 35 + 38, 250),
                        column_config={
                            "Ingrédient": st.column_config.TextColumn("Ingrédient"),
                            "ID": st.column_config.NumberColumn("ID", width="small"),
                            "Qté": st.column_config.NumberColumn("Qté", width="small")
                        }
                    )
            else:
                with st.expander("🧪 Recette", expanded=False):
                    st.info("Non craftable")
        
        # Dropdown 2: Historique Prix HDV
        with col_drop2:
            if item.get('prix_hdv'):
                with st.expander(f"💰 HDV (x{quantity})", expanded=False):
                    try:
                        sorted_dates = sorted(
                            item['prix_hdv'].keys(), 
                            key=lambda k: datetime.fromisoformat(k), 
                            reverse=True
                        )[:5]
                    except:
                        sorted_dates = sorted(item['prix_hdv'].keys(), reverse=True)[:5]
                    
                    history_data = []
                    for date in sorted_dates:
                        price = item['prix_hdv'][date].get(str(quantity))
                        if price is not None:
                            try:
                                date_formatted = datetime.fromisoformat(date).strftime('%d/%m %H:%M')
                            except:
                                date_formatted = date
                            history_data.append({
                                'Date': date_formatted,
                                'Prix': price
                            })
                    
                    if history_data:
                        df_history = pd.DataFrame(history_data)
                        st.dataframe(
                            df_history,
                            width='stretch',
                            hide_index=True,
                            height=min(len(history_data) * 35 + 38, 250),
                            column_config={
                                "Date": st.column_config.TextColumn("Date", width="medium"),
                                "Prix": st.column_config.NumberColumn("Prix", format="%d K")
                            }
                        )
                        
                        # Mini graphique
                        if len(history_data) > 1:
                            st.line_chart(
                                df_history.set_index('Date')['Prix'],
                                height=150
                            )
                    else:
                        st.info(f"Pas de données x{quantity}")
            else:
                with st.expander(f"💰 HDV (x{quantity})", expanded=False):
                    st.info("Aucun historique")
        
        # Dropdown 3: Historique Coût Craft
        with col_drop3:
            if item.get('cout_craft'):
                with st.expander(f"⚒️ Craft (x{quantity})", expanded=False):
                    try:
                        sorted_dates = sorted(
                            item['cout_craft'].keys(), 
                            key=lambda k: datetime.fromisoformat(k), 
                            reverse=True
                        )[:5]
                    except:
                        sorted_dates = sorted(item['cout_craft'].keys(), reverse=True)[:5]
                    
                    history_data = []
                    for date in sorted_dates:
                        price = item['cout_craft'][date].get(str(quantity))
                        if price is not None:
                            try:
                                date_formatted = datetime.fromisoformat(date).strftime('%d/%m %H:%M')
                            except:
                                date_formatted = date
                            history_data.append({
                                'Date': date_formatted,
                                'Coût': price
                            })
                    
                    if history_data:
                        df_history = pd.DataFrame(history_data)
                        st.dataframe(
                            df_history,
                            width='stretch',
                            hide_index=True,
                            height=min(len(history_data) * 35 + 38, 250),
                            column_config={
                                "Date": st.column_config.TextColumn("Date", width="medium"),
                                "Coût": st.column_config.NumberColumn("Coût", format="%d K")
                            }
                        )
                        
                        # Mini graphique
                        if len(history_data) > 1:
                            st.line_chart(
                                df_history.set_index('Date')['Coût'],
                                height=150
                            )
                    else:
                        st.info(f"Pas de données x{quantity}")
            else:
                with st.expander(f"⚒️ Craft (x{quantity})", expanded=False):
                    st.info("Aucun historique")
        
        # Séparateur entre les lignes
        st.divider()

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

# --- AFFICHAGE EN-TÊTES ---
st.markdown("---")
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.6, 2.5, 0.6, 1.2, 1.2, 0.6, 1.2, 1.2])

with col1:
    st.markdown("**ID**")
with col2:
    st.markdown("**Nom**")
with col3:
    st.markdown("**Niv**")
with col4:
    st.markdown("**Supertype**")
with col5:
    st.markdown("**Type**")
with col6:
    st.markdown("**Craft**")
with col7:
    st.markdown(f"**HDV (x{quantity})**")
with col8:
    st.markdown(f"**Craft (x{quantity})**")

st.markdown("---")

# --- AFFICHAGE DES LIGNES AVEC 3 DROPDOWNS ---
if len(df_page) > 0:
    for idx, row in df_page.iterrows():
        item_id = row['_item_id']
        item = data[item_id]
        display_item_row(item, item_id, data, quantity)
else:
    st.info("Aucun résultat ne correspond à vos critères de recherche.")

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