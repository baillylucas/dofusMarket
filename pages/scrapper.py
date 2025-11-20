# import streamlit as st
# import pandas as pd
# from googleDriveJSON import GoogleDriveJSON
# from utils.items_manager import add_items
# import streamlit as st

# # Configuration
# st.set_page_config(layout="wide")

# st.markdown("# 🔍 Scrapper")

# st.sidebar.markdown("# ⚙️ Filtres")

# # --- CSS pour rendre les checkboxes toujours visibles ---
# st.markdown("""
# <style>
#     /* Cible tous les checkboxes */
#     input[type="checkbox"] {
#         opacity: 1 !important;
#         visibility: visible !important;
#     }
    
#     /* Checkboxes dans le header et les cellules */
#     input[type="checkbox"] {
#         width: 20px !important;
#         height: 20px !important;
#         cursor: pointer !important;
#         margin: 0 5px !important;
#     }
    
#     /* Augmenter la taille de la cellule du checkbox */
#     td:first-child, th:first-child {
#         min-width: 50px !important;
#         width: 50px !important;
#     }
    
#     /* Rendre les checkboxes toujours opaques */
#     [role="grid"] input[type="checkbox"],
#     [role="gridcell"] input[type="checkbox"] {
#         opacity: 1 !important;
#         visibility: visible !important;
#     }
    
#     /* Au hover */
#     [role="row"]:hover input[type="checkbox"] {
#         opacity: 1 !important;
#         transform: scale(1.1);
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- Google Drive ---
# FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

# # --- Session State defaults ---
# if 'scrapper_items' not in st.session_state:
#     st.session_state.scrapper_items = []

# # --- Chargement des données ---
# @st.cache_data(ttl=600)
# def charger_donnees():
#     try:
#         drive = GoogleDriveJSON(FILE_ID)
#         data = drive.read()
#         data = {k: v for k, v in data.items() if str(k).isdigit()}
#         return data
#     except Exception as e:
#         st.error(f"Erreur lors du chargement : {e}")
#         return None

# with st.spinner("Chargement des données depuis Google Drive..."):
#     data = charger_donnees()

# if not data:
#     st.error("❌ Impossible de charger les données")
#     st.stop()

# # --- Affichage du tableau ---
# if st.session_state.scrapper_items:
#     # Préparer les données pour le tableau
#     items_data = []
#     for item_id in st.session_state.scrapper_items:
#         item_id_str = str(item_id)
#         if item_id_str in data:
#             item = data[item_id_str]
#             items_data.append({
#                 'id': item.get('id'),
#                 'name': item.get('name'),
#                 'level': item.get('level'),
#                 'type': item.get('type', 'N/A'),
#                 'supertype': item.get('supertype', 'N/A'),
#             })
    
#     df = pd.DataFrame(items_data)
    
#     # --- Filtres dans la sidebar ---
#     with st.sidebar:
#         search_name = st.text_input("Rechercher par libellé", "")
        
#         all_levels = sorted(df['level'].unique())
#         min_level, max_level = st.slider(
#             "Niveau",
#             min_value=min(all_levels),
#             max_value=max(all_levels),
#             value=(min(all_levels), max(all_levels))
#         )
        
#         all_types = sorted(df['type'].unique())
#         type_filter = st.multiselect("Type", options=all_types)
        
#         all_supertypes = sorted(df['supertype'].unique())
#         supertype_filter = st.multiselect("Supertype", options=all_supertypes)
    
#     # Appliquer les filtres
#     df_filtered = df.copy()
#     if search_name:
#         df_filtered = df_filtered[df_filtered['name'].str.contains(search_name, case=False, na=False) | 
#                                    df_filtered['id'].astype(str).str.contains(search_name)]
#     df_filtered = df_filtered[(df_filtered['level'] >= min_level) & (df_filtered['level'] <= max_level)]
#     if type_filter:
#         df_filtered = df_filtered[df_filtered['type'].isin(type_filter)]
#     if supertype_filter:
#         df_filtered = df_filtered[df_filtered['supertype'].isin(supertype_filter)]
    
#     # Réinitialiser l'index pour que hide_index fonctionne correctement
#     df_filtered = df_filtered.reset_index(drop=True)
    
#     # Bouton Afficher les IDs
#     if st.button("📋 Afficher les IDs", key="btn_show_ids"):
#         st.info(f"**IDs du scrapper ({len(st.session_state.scrapper_items)}):** {', '.join(map(str, st.session_state.scrapper_items))}")
    
#     st.markdown(f"**Affichage : {len(df_filtered)} / {len(df)} items**")
    
#     # Afficher le tableau avec le mode dynamic (checkboxes du header natif)
#     edited_df = st.data_editor(
#         df_filtered,
#         column_config={
#             "id": st.column_config.Column(
#                 "ID",
#                 width="small"
#             ),
#             "name": st.column_config.Column(
#                 "Libellé",
#                 width="large"
#             ),
#             "level": st.column_config.Column(
#                 "Niveau",
#                 width="small"
#             ),
#             "type": st.column_config.Column(
#                 "Type",
#                 width="medium"
#             ),
#             "supertype": st.column_config.Column(
#                 "Supertype",
#                 width="medium"
#             ),
#         },
#         hide_index=True,
#         use_container_width=True,
#         disabled=["id", "name", "level", "type", "supertype"],
#         num_rows="dynamic",
#         key="data_editor_scrapper"
#     )
    
#     # 🔄 Synchroniser automatiquement : supprimer les items qui ne sont plus dans le tableau
#     remaining_ids = set(edited_df['id'].tolist()) if len(edited_df) > 0 else set()
#     original_ids = set(df_filtered['id'].tolist())
#     deleted_ids = original_ids - remaining_ids
    
#     # Supprimer automatiquement de scrapper_items
#     items_deleted = False
#     for item_id in deleted_ids:
#         if item_id in st.session_state.scrapper_items:
#             st.session_state.scrapper_items.remove(item_id)
#             items_deleted = True
    
#     # Si des items ont été supprimés, rerun pour mettre à jour l'UI
#     if items_deleted:
#         st.rerun()

# else:
#     st.info("📭 Le scrapper est vide. Ajoutez des items depuis la page 'Prix des items'")

import streamlit as st
import pandas as pd
from googleDriveJSON import GoogleDriveJSON
from utils import load_scrapper_items, remove_items_from_scrapper

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

# --- Chargement des données ---
@st.cache_data(ttl=600)
def charger_donnees():
    try:
        drive = GoogleDriveJSON(FILE_ID)
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

# Charger les items du scrapper depuis le fichier JSON
scrapper_items = load_scrapper_items()

# --- Affichage du tableau ---
if scrapper_items:
    # Préparer les données pour le tableau
    items_data = []
    for item_id in scrapper_items:
        item_id_str = str(item_id)
        if item_id_str in data:
            item = data[item_id_str]
            items_data.append({
                'id': item.get('id'),
                'name': item.get('name'),
                'level': item.get('level'),
                'type': item.get('type', 'N/A'),
                'supertype': item.get('supertype', 'N/A'),
            })
    
    df = pd.DataFrame(items_data)
    
    # --- Filtres dans la sidebar ---
    with st.sidebar:
        search_name = st.text_input("Rechercher par libellé", "")
        
        all_levels = sorted(df['level'].unique())
        min_level, max_level = st.slider(
            "Niveau",
            min_value=min(all_levels),
            max_value=max(all_levels),
            value=(min(all_levels), max(all_levels))
        )
        
        all_types = sorted(df['type'].unique())
        type_filter = st.multiselect("Type", options=all_types)
        
        all_supertypes = sorted(df['supertype'].unique())
        supertype_filter = st.multiselect("Supertype", options=all_supertypes)
    
    # Appliquer les filtres
    df_filtered = df.copy()
    if search_name:
        df_filtered = df_filtered[df_filtered['name'].str.contains(search_name, case=False, na=False) | 
                                   df_filtered['id'].astype(str).str.contains(search_name)]
    df_filtered = df_filtered[(df_filtered['level'] >= min_level) & (df_filtered['level'] <= max_level)]
    if type_filter:
        df_filtered = df_filtered[df_filtered['type'].isin(type_filter)]
    if supertype_filter:
        df_filtered = df_filtered[df_filtered['supertype'].isin(supertype_filter)]
    
    # Réinitialiser l'index pour que hide_index fonctionne correctement
    df_filtered = df_filtered.reset_index(drop=True)
    
    # Bouton Afficher les IDs
    if st.button("📋 Afficher les IDs", key="btn_show_ids"):
        st.info(f"**IDs du scrapper ({len(scrapper_items)}):** {', '.join(map(str, scrapper_items))}")
    
    st.markdown(f"**Affichage : {len(df_filtered)} / {len(df)} items**")
    
    # Afficher le tableau avec le mode dynamic (checkboxes du header natif)
    edited_df = st.data_editor(
        df_filtered,
        column_config={
            "id": st.column_config.Column(
                "ID",
                width="small"
            ),
            "name": st.column_config.Column(
                "Libellé",
                width="large"
            ),
            "level": st.column_config.Column(
                "Niveau",
                width="small"
            ),
            "type": st.column_config.Column(
                "Type",
                width="medium"
            ),
            "supertype": st.column_config.Column(
                "Supertype",
                width="medium"
            ),
        },
        hide_index=True,
        use_container_width=True,
        disabled=["id", "name", "level", "type", "supertype"],
        num_rows="dynamic",
        key="data_editor_scrapper"
    )
    
    # 🔄 Synchroniser automatiquement : supprimer les items qui ne sont plus dans le tableau
    remaining_ids = set(edited_df['id'].tolist()) if len(edited_df) > 0 else set()
    original_ids = set(df_filtered['id'].tolist())
    deleted_ids = original_ids - remaining_ids
    
    # Supprimer automatiquement du fichier JSON
    if deleted_ids:
        removed_count = remove_items_from_scrapper(list(deleted_ids))
        if removed_count > 0:
            st.toast(f"✓ {removed_count} item(s) supprimé(s) du scrapper", icon="✅")
            st.rerun()

else:
    st.info("📭 Le scrapper est vide. Ajoutez des items depuis la page 'Prix des items'")