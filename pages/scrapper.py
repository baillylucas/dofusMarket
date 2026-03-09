import streamlit as st
import pandas as pd
from googleDriveJSON import GoogleDriveJSON
from utils import (
    load_scrapper_items, load_scrapper_ingredients,
    remove_items_from_scrapper, remove_ingredients_from_scrapper,
    get_user_groups, add_items_to_group, remove_items_from_group,
)

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
st.session_state.scrapper_user_groups = get_user_groups()


def _get_selected_ids(event, df):
    if event and event.selection and event.selection.rows:
        return df.iloc[event.selection.rows]['id'].tolist()
    return []

# Session state
if 'show_scraping_summary' not in st.session_state:
    st.session_state.show_scraping_summary = False
if 'scrapper_user_groups' not in st.session_state:
    st.session_state.scrapper_user_groups = {}
if 'scrapper_selected_group_for_action' not in st.session_state:
    st.session_state.scrapper_selected_group_for_action = None

# --- Sélection du type de scraper ---
scraper_type = st.radio(
    "Type de scraper",
    options=["💰 Prix des ressources (HDV)", "🐾 XP Familier"],
    horizontal=True,
    key="scraper_type",
    help=(
        "**Prix HDV** : relève les prix de vente de chaque ressource dans les HDVs.\n\n"
        "**XP Familier** : achète ou récupère les ressources et mesure l'XP donné au familier par chacune."
    ),
)
is_familier_mode = scraper_type.startswith("🐾")

# --- Option Debug ---
debug_mode = st.checkbox("🔧 Mode Debug (screenshots élargis)", key="debug_mode", help="Génère un deuxième screenshot plus large (+/- 50px) pour chaque capture, utile pour le débogage")

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
        # Bouton Voir le résumé (uniquement en mode Prix)
        if not is_familier_mode:
            if st.button("📊 Voir le résumé du scraping", key="btn_show_summary"):
                st.session_state.show_scraping_summary = True
        else:
            st.info("ℹ️ Le résumé n'est pas disponible en mode XP Familier.")

    with col_btn3:
        # Bouton Lancer le scraping
        btn_label = "🚀 Lancer le scraping XP Familier" if is_familier_mode else "🚀 Lancer le scraping"
        if st.button(btn_label, key="btn_launch_scraping_direct", type="primary"):
            if is_familier_mode:
                from utils import launch_familier_scrapper
                with st.spinner("Lancement du scraper XP Familier..."):
                    success, message, process = launch_familier_scrapper(debug=debug_mode)
                    script_name = "8_familier_xp_scrapper.py"
            else:
                from utils import launch_scrapper
                with st.spinner("Lancement du script de scraping..."):
                    success, message, process = launch_scrapper(debug=debug_mode)
                    script_name = "5_dofus_scrapper.py"

            if success:
                st.success(f"✅ {message}")
                debug_info = "\n- **Mode DEBUG activé** : des screenshots élargis seront générés" if debug_mode else ""
                xp_info = "\n- Les résultats XP seront sauvegardés dans `data/xp_familiers/`" if is_familier_mode else "\n- Les données seront automatiquement sauvegardées sur Google Drive"
                st.info(f"""
                **Le scraping est en cours !**
                - Une nouvelle console s'est ouverte avec le script de scraping
                - Suivez la progression dans cette console
                - Ne fermez pas la console avant la fin du scraping{xp_info}{debug_info}
                """)
            else:
                st.error(f"❌ {message}")
                debug_arg = " --debug" if debug_mode else ""
                st.warning(f"""
                **Alternative manuelle :**
                Ouvrez un terminal et exécutez :
                ```
                cd scrapper
                python {script_name}{debug_arg}
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
            if len(all_levels_items) > 1:
                min_level_items, max_level_items = st.slider(
                    "Niveau (items)",
                    min_value=min(all_levels_items),
                    max_value=max(all_levels_items),
                    value=(min(all_levels_items), max(all_levels_items)),
                    key="level_items"
                )
            else:
                # Si un seul niveau, pas de slider
                min_level_items = max_level_items = all_levels_items[0]
                st.info(f"Niveau unique : {all_levels_items[0]}")

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

        # Boutons d'action sous le tableau items
        group_options_action = {gid: gdata['name'] for gid, gdata in st.session_state.scrapper_user_groups.items()}
        if group_options_action and st.session_state.scrapper_selected_group_for_action not in group_options_action:
            st.session_state.scrapper_selected_group_for_action = list(group_options_action.keys())[0]

        col_group_select, col_group_add, col_group_remove, col_delete = st.columns([1.5, 0.6, 0.6, 0.8])

        with col_group_select:
            if group_options_action:
                selected_group_action = st.selectbox(
                    "Groupe",
                    options=list(group_options_action.keys()),
                    format_func=lambda x: group_options_action[x],
                    index=list(group_options_action.keys()).index(st.session_state.scrapper_selected_group_for_action)
                          if st.session_state.scrapper_selected_group_for_action in group_options_action else 0,
                    key="scrapper_group_action_select_widget",
                    label_visibility="collapsed",
                    on_change=lambda: st.session_state.update(
                        {'scrapper_selected_group_for_action': st.session_state.scrapper_group_action_select_widget}
                    )
                )
            else:
                selected_group_action = None
                st.info("Aucun groupe")

        with col_group_add:
            if st.button("➕ Groupe", help="Ajouter la sélection au groupe", key="scrapper_group_add"):
                selected_ids = _get_selected_ids(event_items, df_filtered)
                if selected_ids and selected_group_action:
                    added = add_items_to_group(selected_group_action, selected_ids)
                    st.toast(f"✓ {added} item(s) ajouté(s) au groupe" if added > 0 else "⚠️ Item(s) déjà dans le groupe", icon="✅" if added > 0 else "ℹ️")
                elif not selected_ids:
                    st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
                else:
                    st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

        with col_group_remove:
            if st.button("➖ Groupe", help="Retirer la sélection du groupe", key="scrapper_group_remove"):
                selected_ids = _get_selected_ids(event_items, df_filtered)
                if selected_ids and selected_group_action:
                    removed = remove_items_from_group(selected_group_action, selected_ids)
                    st.toast(f"✓ {removed} item(s) retiré(s)" if removed > 0 else "⚠️ Aucun item à retirer", icon="✅" if removed > 0 else "ℹ️")
                elif not selected_ids:
                    st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
                else:
                    st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

        with col_delete:
            if st.button("🗑️ Supprimer", key="btn_delete_items"):
                selected_ids = _get_selected_ids(event_items, df_filtered)
                if selected_ids:
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
                if len(all_levels_ing) > 1:
                    min_level_ing, max_level_ing = st.slider(
                        "Niveau (ingrédients)",
                        min_value=min(all_levels_ing),
                        max_value=max(all_levels_ing),
                        value=(min(all_levels_ing), max(all_levels_ing)),
                        key="level_ingredients"
                    )
                else:
                    # Si un seul niveau, pas de slider
                    min_level_ing = max_level_ing = all_levels_ing[0]
                    st.info(f"Niveau unique : {all_levels_ing[0]}")

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
            selection_mode="multi-row",
            on_select="rerun",
            key="dataframe_scrapper_ingredients"
        )

        # Supprimer les ingrédients sélectionnés
        if st.button("🗑️ Supprimer la sélection", key="btn_delete_ingredients"):
            if event_ingredients.selection and event_ingredients.selection.rows:
                selected_indices = event_ingredients.selection.rows
                selected_ids = df_ingredients_filtered.iloc[selected_indices]['id'].tolist()
                removed_count = remove_ingredients_from_scrapper(selected_ids)
                if removed_count > 0:
                    st.toast(f"✓ {removed_count} ingrédient(s) supprimé(s) du scrapper", icon="✅")
                    st.rerun()
            else:
                st.toast("⚠️ Sélectionnez des ingrédients à supprimer", icon="⚠️")
    else:
        st.info("📭 Aucun ingrédient requis (aucun item craftable sélectionné)")

else:
    st.info("📭 Le scrapper est vide. Ajoutez des items depuis la page 'Prix des items'")


