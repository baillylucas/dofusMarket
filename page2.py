import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON

st.markdown("# Page 2 🎉")
st.sidebar.markdown("# Page 2 🎉")

# Configuration Google Drive - UTILISEZ LE BON FILE_ID
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"  # ← Le FILE_ID qui fonctionne

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

def display_recipe(data, item):
    """Affiche la recette d'un item"""
    if not item.get('ingredients'):
        st.info("Cet item n'a pas de recette")
        return
    
    st.markdown("#### 🧪 Recette de fabrication")
    
    recipe_data = []
    for ing in item['ingredients']:
        ing_name = get_ingredient_name(data, ing['id'])
        recipe_data.append({
            'Ingrédient': ing_name,
            'ID': ing['id'],
            'Quantité': ing['quantity']
        })
    
    st.dataframe(
        pd.DataFrame(recipe_data),
        width='stretch',
        hide_index=True,
        column_config={
            "Ingrédient": st.column_config.TextColumn("Ingrédient", width="large"),
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Quantité": st.column_config.NumberColumn("Quantité", width="small")
        }
    )

def display_price_history(prix_dict, quantity, title):
    """Affiche l'historique des 5 derniers prix"""
    if not prix_dict:
        st.info(f"Aucun historique disponible pour {title}")
        return
    
    st.markdown(f"#### 📊 Historique - {title}")
    
    # Trie par date décroissante et prend les 5 derniers
    try:
        sorted_dates = sorted(prix_dict.keys(), key=lambda k: datetime.fromisoformat(k), reverse=True)[:5]
    except:
        sorted_dates = sorted(prix_dict.keys(), reverse=True)[:5]
    
    history_data = []
    for date in sorted_dates:
        price = prix_dict[date].get(str(quantity))
        if price is not None:
            try:
                date_formatted = datetime.fromisoformat(date).strftime('%d/%m/%Y %H:%M')
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
            column_config={
                "Date": st.column_config.TextColumn("Date"),
                "Prix": st.column_config.NumberColumn("Prix", format="%d K")
            }
        )
        
        # Graphique d'évolution
        st.line_chart(
            df_history.set_index('Date')['Prix'],
            use_container_width=True
        )
    else:
        st.info(f"Aucune donnée pour la quantité x{quantity}")

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

# --- TRANSFORMATION EN DATAFRAME ---
rows = []
for item_id, item in data.items():
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft = get_latest_entry(item.get("cout_craft", {})) or {}
    
    rows.append({
        "id": item.get("id"),
        "name": item.get("name"),
        "level": item.get("level"),
        "supertype": item.get("supertype"),
        "type": item.get("type"),
        "is_craft": '✓' if item.get("is_craft") else '✗',
        "prix_hdv": prix.get(str(quantity), '-'),
        "cout_craft": craft.get(str(quantity), '-'),
        "_item_id": item_id  # Pour retrouver l'item complet
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
    df = df[df["is_craft"] == '✓']
elif craft_filter == "Non craftables":
    df = df[df["is_craft"] == '✗']

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

# --- AFFICHAGE DU TABLEAU ---
df_page = df_display.iloc[start_idx:end_idx].copy()
df_page_display = df_page.drop(columns=['_item_id'])

st.dataframe(
    df_page_display,
    width='stretch',
    hide_index=True,
    column_config={
        "id": st.column_config.NumberColumn("ID", width="small"),
        "name": st.column_config.TextColumn("Nom", width="large"),
        "level": st.column_config.NumberColumn("Niveau", width="small"),
        "supertype": st.column_config.TextColumn("Supertype", width="medium"),
        "type": st.column_config.TextColumn("Type", width="medium"),
        "is_craft": st.column_config.TextColumn("Craft", width="small"),
        "prix_hdv": st.column_config.TextColumn(f"Prix HDV (x{quantity})", width="medium"),
        "cout_craft": st.column_config.TextColumn(f"Coût Craft (x{quantity})", width="medium")
    }
)

# --- DÉTAILS D'UN ITEM ---
st.markdown("---")
st.markdown("### 🔎 Voir les détails d'un item")

if len(df_page) > 0:
    # Créer une liste des noms avec leur ID pour éviter les doublons
    items_display = [f"{row['name']} (ID: {row['id']})" for _, row in df_page.iterrows()]
    
    selected_display = st.selectbox(
        "Sélectionnez un item",
        options=[''] + items_display,
        format_func=lambda x: "-- Sélectionnez --" if x == '' else x
    )
    
    if selected_display:
        # Extraire l'ID depuis la chaîne sélectionnée
        selected_id = selected_display.split("(ID: ")[1].rstrip(")")
        
        # Retrouver l'item_id correspondant
        selected_row = df_page[df_page['id'] == int(selected_id)].iloc[0]
        item_id = selected_row['_item_id']
        selected_item = data[item_id]
        
        # Affichage des détails dans un expander
        with st.expander(f"📋 Détails de : **{selected_item['name']}**", expanded=True):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("ID", selected_item['id'])
                st.metric("Niveau", selected_item['level'])
            
            with col2:
                st.metric("Supertype", selected_item.get('supertype', 'N/A'))
                st.metric("Type", selected_item.get('type', 'N/A'))
            
            with col3:
                st.metric("Craftable", "Oui ✓" if selected_item.get('is_craft') else "Non ✗")
                last_maj = selected_item.get('last_maj', 'N/A')
                if last_maj != 'N/A':
                    try:
                        last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                st.metric("Dernière MAJ", last_maj)
            
            st.markdown("---")
            
            # Recette si craftable
            if selected_item.get('is_craft') and selected_item.get('ingredients'):
                display_recipe(data, selected_item)
                st.markdown("---")
            
            # Historique des prix
            col_hist1, col_hist2 = st.columns(2)
            
            with col_hist1:
                display_price_history(
                    selected_item.get('prix_hdv', {}),
                    quantity,
                    f"Prix HDV (x{quantity})"
                )
            
            with col_hist2:
                display_price_history(
                    selected_item.get('cout_craft', {}),
                    quantity,
                    f"Coût Craft (x{quantity})"
                )
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













