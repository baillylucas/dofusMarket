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
                'image': f"https://api.dofusdb.fr/img/items/{item.get('iconId', item.get('id'))}.png",
                'name': item.get('name'),
                'level': item.get('level'),
                'hdv': item.get('hdv', 'N/A'),
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

        all_hdv = sorted([hdv for hdv in df['hdv'].unique() if hdv != 'N/A'])
        hdv_filter = st.multiselect("HDV", options=all_hdv)
    
    # Appliquer les filtres
    df_filtered = df.copy()
    if search_name:
        df_filtered = df_filtered[df_filtered['name'].str.contains(search_name, case=False, na=False) |
                                   df_filtered['id'].astype(str).str.contains(search_name)]
    df_filtered = df_filtered[(df_filtered['level'] >= min_level) & (df_filtered['level'] <= max_level)]
    if hdv_filter:
        df_filtered = df_filtered[df_filtered['hdv'].isin(hdv_filter)]
    
    # Réinitialiser l'index pour que hide_index fonctionne correctement
    df_filtered = df_filtered.reset_index(drop=True)
    
    # Bouton Afficher les IDs
    if st.button("📋 Afficher les IDs", key="btn_show_ids"):
        st.info(f"**IDs du scrapper ({len(scrapper_items)}):** {', '.join(map(str, scrapper_items))}")
    
    st.markdown(f"**Affichage : {len(df_filtered)} / {len(df)} items**")

    # Afficher le tableau avec tri natif
    event = st.dataframe(
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
        key="dataframe_scrapper"
    )

    # Supprimer les items sélectionnés
    if st.button("🗑️ Supprimer la sélection", key="btn_delete_selection"):
        if event.selection and event.selection.rows:
            selected_indices = event.selection.rows
            selected_ids = df_filtered.iloc[selected_indices]['id'].tolist()
            removed_count = remove_items_from_scrapper(selected_ids)
            if removed_count > 0:
                st.toast(f"✓ {removed_count} item(s) supprimé(s) du scrapper", icon="✅")
                st.rerun()
        else:
            st.toast("⚠️ Sélectionnez des items à supprimer", icon="⚠️")

else:
    st.info("📭 Le scrapper est vide. Ajoutez des items depuis la page 'Prix des items'")


