import streamlit as st
import pandas as pd
from googleDriveJSON import GoogleDriveJSON
from utils import load_scrapper_items, load_scrapper_ingredients, remove_items_from_scrapper

# Configuration
st.set_page_config(layout="wide")

st.markdown("# 🔍 Scrapper")

st.sidebar.markdown("# ⚙️ Filtres")

# --- CSS pour rendre les checkboxes toujours visibles ---
st.markdown("""
<style>
    /* Cible tous les checkboxes */
    input[type="checkbox"] {
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Checkboxes dans le header et les cellules */
    input[type="checkbox"] {
        width: 20px !important;
        height: 20px !important;
        cursor: pointer !important;
        margin: 0 5px !important;
    }
    
    /* Augmenter la taille de la cellule du checkbox */
    td:first-child, th:first-child {
        min-width: 50px !important;
        width: 50px !important;
    }
    
    /* Rendre les checkboxes toujours opaques */
    [role="grid"] input[type="checkbox"],
    [role="gridcell"] input[type="checkbox"] {
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Au hover */
    [role="row"]:hover input[type="checkbox"] {
        opacity: 1 !important;
        transform: scale(1.1);
    }
</style>
""", unsafe_allow_html=True)

# --- Google Drive ---
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"
SERVICE_ACCOUNT_FILE = "credentials/service_account.json"

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

with st.spinner("Chargement des données depuis Google Drive..."):
    data = charger_donnees()

if not data:
    st.error("❌ Impossible de charger les données")
    st.stop()

# Charger les items et ingrédients du scrapper depuis le fichier JSON
scrapper_items = load_scrapper_items()
scrapper_ingredients = load_scrapper_ingredients()

# Session state pour gérer l'affichage du résumé
if 'show_scraping_summary' not in st.session_state:
    st.session_state.show_scraping_summary = False

# --- Boutons d'action ---
if scrapper_items or scrapper_ingredients:
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        # Bouton Afficher les IDs
        if st.button("📋 Afficher les IDs", key="btn_show_all_ids"):
            # Créer une liste unique combinant items et ingrédients
            all_ids = sorted(set(scrapper_items + scrapper_ingredients))
            st.info(f"**IDs totaux du scrapper ({len(all_ids)}):** {', '.join(map(str, all_ids))}")
            st.info(f"**Items ({len(scrapper_items)}):** {', '.join(map(str, scrapper_items))}")
            st.info(f"**Ingrédients ({len(scrapper_ingredients)}):** {', '.join(map(str, scrapper_ingredients))}")

    with col_btn2:
        # Bouton Voir le résumé
        if st.button("📊 Voir le résumé du scraping", key="btn_show_summary"):
            st.session_state.show_scraping_summary = True

    with col_btn3:
        # Bouton Lancer le scraping directement
        if st.button("🚀 Lancer le scraping", key="btn_launch_scraping_direct", type="primary"):
            from utils import launch_scrapper

            with st.spinner("Lancement du script de scraping..."):
                success, message, process = launch_scrapper()

                if success:
                    st.success(f"✅ {message}")
                    st.info("""
                    **Le scraping est en cours !**
                    - Une nouvelle console s'est ouverte avec le script de scraping
                    - Suivez la progression dans cette console
                    - Ne fermez pas la console avant la fin du scraping
                    - Les données seront automatiquement sauvegardées sur Google Drive
                    """)
                else:
                    st.error(f"❌ {message}")
                    st.warning("""
                    **Alternative manuelle :**
                    Ouvrez un terminal et exécutez :
                    ```
                    cd scrapper
                    python 4_dofus_scrapper.py
                    ```
                    """)

# Afficher le résumé si demandé
if st.session_state.show_scraping_summary:
    from utils import get_scrapper_items_by_hdv

    st.markdown("---")
    st.markdown("## 📊 Résumé du scraping")

    # Récupérer les items organisés par HDV
    items_by_hdv = get_scrapper_items_by_hdv(data)

    if not items_by_hdv:
        st.error("❌ Aucun item à scraper.")
    else:
        for hdv_name, items in items_by_hdv.items():
            with st.expander(f"**{hdv_name.upper()}** ({len(items)} items)", expanded=True):
                st.write(", ".join(items))

        st.info("""
        **⚠️ Instructions importantes avant de lancer :**
        1. Assurez-vous que Dofus est ouvert et que vous êtes connecté
        2. Placez votre personnage dans une zone accessible aux HDV
        3. Ne touchez pas à la souris/clavier pendant le scraping
        4. Cliquez sur le bouton "🚀 Lancer le scraping" ci-dessus
        """)

        if st.button("❌ Masquer le résumé", key="btn_hide_summary"):
            st.session_state.show_scraping_summary = False
            st.rerun()

# --- Affichage du tableau ---
if scrapper_items or scrapper_ingredients:
    # === SECTION 1: ITEMS CHOISIS PAR L'UTILISATEUR ===
    st.markdown("## 📦 Items choisis par l'utilisateur")

    if scrapper_items:
        # Préparer les données pour le tableau des items
        items_data = []
        for item_id in scrapper_items:
            item_id_str = str(item_id)
            if item_id_str in data:
                item = data[item_id_str]
                items_data.append({
                    'id': item.get('id'),
                    'image': f"https://api.dofusdb.fr/img/items/{item.get('iconId', item.get('id'))}.png",
                    'name': item.get('name'),
                    'level': item.get('level'),
                    'hdv': item.get('hdv', 'N/A'),
                })

        df = pd.DataFrame(items_data)
    else:
        df = pd.DataFrame()
    
    # --- Filtres dans la sidebar pour les items ---
    with st.sidebar:
        st.markdown("### Filtres pour les items")
        search_name_items = st.text_input("Rechercher par libellé (items)", "", key="search_items")

        if not df.empty:
            all_levels_items = sorted(df['level'].unique())
            min_level_items, max_level_items = st.slider(
                "Niveau (items)",
                min_value=min(all_levels_items),
                max_value=max(all_levels_items),
                value=(min(all_levels_items), max(all_levels_items)),
                key="level_items"
            )

            all_hdv_items = sorted([hdv for hdv in df['hdv'].unique() if hdv != 'N/A'])
            hdv_filter_items = st.multiselect("HDV (items)", options=all_hdv_items, key="hdv_items")
        else:
            min_level_items = max_level_items = 0
            hdv_filter_items = []

    # Appliquer les filtres pour les items
    if not df.empty:
        df_filtered = df.copy()
        if search_name_items:
            df_filtered = df_filtered[df_filtered['name'].str.contains(search_name_items, case=False, na=False) |
                                       df_filtered['id'].astype(str).str.contains(search_name_items)]
        df_filtered = df_filtered[(df_filtered['level'] >= min_level_items) & (df_filtered['level'] <= max_level_items)]
        if hdv_filter_items:
            df_filtered = df_filtered[df_filtered['hdv'].isin(hdv_filter_items)]

        # Réinitialiser l'index pour que hide_index fonctionne correctement
        df_filtered = df_filtered.reset_index(drop=True)
    else:
        df_filtered = df

    st.markdown(f"**Affichage : {len(df_filtered)} / {len(df)} items**")

    # Afficher le tableau des items avec tri natif
    if not df_filtered.empty:
        event_items = st.dataframe(
            df_filtered,
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID",
                    width="small"
                ),
                "image": st.column_config.ImageColumn(
                    "Image",
                    width="small"
                ),
                "name": st.column_config.TextColumn(
                    "Libellé",
                    width="large"
                ),
                "level": st.column_config.NumberColumn(
                    "Niveau",
                    width="small"
                ),
                "hdv": st.column_config.TextColumn(
                    "HDV",
                    width="medium"
                ),
            },
            hide_index=True,
            use_container_width=True,
            selection_mode="multi-row",
            on_select="rerun",
            key="dataframe_scrapper_items"
        )

        # Supprimer les items sélectionnés
        if st.button("🗑️ Supprimer la sélection", key="btn_delete_items"):
            if event_items.selection and event_items.selection.rows:
                selected_indices = event_items.selection.rows
                selected_ids = df_filtered.iloc[selected_indices]['id'].tolist()
                removed_count = remove_items_from_scrapper(selected_ids, data=data)
                if removed_count > 0:
                    st.toast(f"✓ {removed_count} item(s) supprimé(s) du scrapper", icon="✅")
                    st.rerun()
            else:
                st.toast("⚠️ Sélectionnez des items à supprimer", icon="⚠️")
    else:
        st.info("📭 Aucun item sélectionné pour le scrapper")

    # === SECTION 2: INGRÉDIENTS NÉCESSAIRES ===
    st.markdown("---")
    st.markdown("## 🧪 Ingrédients nécessaires pour les crafts")

    if scrapper_ingredients:
        # Préparer les données pour le tableau des ingrédients
        ingredients_data = []
        for ing_id in scrapper_ingredients:
            ing_id_str = str(ing_id)
            if ing_id_str in data:
                item = data[ing_id_str]
                ingredients_data.append({
                    'id': item.get('id'),
                    'image': f"https://api.dofusdb.fr/img/items/{item.get('iconId', item.get('id'))}.png",
                    'name': item.get('name'),
                    'level': item.get('level'),
                    'hdv': item.get('hdv', 'N/A'),
                })

        df_ingredients = pd.DataFrame(ingredients_data)

        # --- Filtres dans la sidebar pour les ingrédients ---
        with st.sidebar:
            st.markdown("---")
            st.markdown("### Filtres pour les ingrédients")
            search_name_ing = st.text_input("Rechercher par libellé (ingrédients)", "", key="search_ingredients")

            if not df_ingredients.empty:
                all_levels_ing = sorted(df_ingredients['level'].unique())
                min_level_ing, max_level_ing = st.slider(
                    "Niveau (ingrédients)",
                    min_value=min(all_levels_ing),
                    max_value=max(all_levels_ing),
                    value=(min(all_levels_ing), max(all_levels_ing)),
                    key="level_ingredients"
                )

                all_hdv_ing = sorted([hdv for hdv in df_ingredients['hdv'].unique() if hdv != 'N/A'])
                hdv_filter_ing = st.multiselect("HDV (ingrédients)", options=all_hdv_ing, key="hdv_ingredients")
            else:
                min_level_ing = max_level_ing = 0
                hdv_filter_ing = []

        # Appliquer les filtres pour les ingrédients
        df_ingredients_filtered = df_ingredients.copy()
        if search_name_ing:
            df_ingredients_filtered = df_ingredients_filtered[
                df_ingredients_filtered['name'].str.contains(search_name_ing, case=False, na=False) |
                df_ingredients_filtered['id'].astype(str).str.contains(search_name_ing)
            ]
        df_ingredients_filtered = df_ingredients_filtered[
            (df_ingredients_filtered['level'] >= min_level_ing) &
            (df_ingredients_filtered['level'] <= max_level_ing)
        ]
        if hdv_filter_ing:
            df_ingredients_filtered = df_ingredients_filtered[df_ingredients_filtered['hdv'].isin(hdv_filter_ing)]

        # Réinitialiser l'index
        df_ingredients_filtered = df_ingredients_filtered.reset_index(drop=True)

        st.markdown(f"**Affichage : {len(df_ingredients_filtered)} / {len(df_ingredients)} ingrédients**")

        # Afficher le tableau des ingrédients
        event_ingredients = st.dataframe(
            df_ingredients_filtered,
            column_config={
                "id": st.column_config.NumberColumn(
                    "ID",
                    width="small"
                ),
                "image": st.column_config.ImageColumn(
                    "Image",
                    width="small"
                ),
                "name": st.column_config.TextColumn(
                    "Libellé",
                    width="large"
                ),
                "level": st.column_config.NumberColumn(
                    "Niveau",
                    width="small"
                ),
                "hdv": st.column_config.TextColumn(
                    "HDV",
                    width="medium"
                ),
            },
            hide_index=True,
            use_container_width=True,
            key="dataframe_scrapper_ingredients"
        )
    else:
        st.info("📭 Aucun ingrédient requis (aucun item craftable sélectionné)")

else:
    st.info("📭 Le scrapper est vide. Ajoutez des items depuis la page 'Prix des items'")


