# import streamlit as st
# import pandas as pd
# from datetime import datetime
# from googleDriveJSON import GoogleDriveJSON

# # Configuration
# st.set_page_config(layout="wide")

# st.markdown("# Page 3")
# st.sidebar.markdown("# Page 3")

# # --- CSS ---
# st.markdown("""
# <style>
#     details { border: 1px solid #555; border-top: none; border-radius: 0; margin: 0; background-color: rgba(40, 50, 60, 0.6); }
#     details:first-of-type { border-top: 1px solid #555; }
#     summary {
#         display: grid;
#         grid-template-columns: 3% 7% 20% 8% 12% 12% 8% 13% 13%;
#         gap: 8px;
#         padding: 16px 12px;
#         cursor: pointer;
#         background-color: rgba(40, 50, 60, 0.6);
#         border-radius: 0;
#         font-family: monospace;
#         align-items: center;
#         transition: background-color 0.2s;
#         color: #ddd;
#         min-height: 20px;
#         list-style: none;
#     }
#     summary::-webkit-details-marker { display: none; }
#     summary::marker { display: none; }
#     summary:hover { background-color: rgba(70, 120, 180, 0.4); }
#     details[open] summary { border-bottom: 1px solid #555; }
#     .arrow-cell { color: #6db3ff; font-weight: bold; text-align: center; }
#     .id-cell { color: #6db3ff; font-weight: bold; }
#     .details-content { padding: 20px; background-color: rgba(30, 40, 50, 0.8); }
#     .info-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }
#     .info-item { color: #fff; }
#     .info-label { font-size: 0.85em; color: #888; margin-bottom: 5px; }
#     .info-value { font-size: 1.5em; font-weight: bold; color: #fff; }
#     .recipe-table, .history-table { width: 100%; margin-top: 10px; border-collapse: collapse; }
#     .recipe-table th, .history-table th { background-color: rgba(100, 180, 255, 0.3); padding: 8px; border: 1px solid #666; color: #fff; text-align: left; }
#     .recipe-table td, .history-table td { background-color: rgba(50, 50, 60, 0.5); padding: 8px; border: 1px solid #666; color: #ddd; }
#     .section-title { color: #fff; font-weight: bold; margin: 15px 0 10px 0; }
#     .price-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
#     hr { border: none; border-top: 1px solid #666; margin: 20px 0; }
#     .craft-yes { color: #5eff5e; }
#     .craft-no { color: #ff5e5e; }
#     .price-value { color: #ffd966; }
#     details .arrow-cell::after { content: '▶'; color: #6db3ff; font-weight: bold; }
#     details[open] .arrow-cell::after { content: '▼'; }
#     .checkbox-cell input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; accent-color: #6db3ff; }
    
#     /* Style pour les boutons de header */
#     .stButton > button {
#         background-color: transparent !important;
#         border: none !important;
#         color: #fff !important;
#         font-weight: bold !important;
#         padding: 0 !important;
#         font-family: monospace !important;
#         box-shadow: none !important;
#         cursor: pointer !important;
#         height: auto !important;
#         width: auto !important;
#     }
#     .stButton > button:hover {
#         background-color: transparent !important;
#         color: #6db3ff !important;
#         border: none !important;
#         box-shadow: none !important;
#     }
#     .stButton > button:active,
#     .stButton > button:focus {
#         background-color: transparent !important;
#         border: none !important;
#         box-shadow: none !important;
#     }
    
#     /* Container pour le header */
#     .header-container {
#         display: grid;
#         grid-template-columns: 3% 7% 20% 8% 12% 12% 8% 13% 13%;
#         gap: 8px;
#         padding: 16px 12px;
#         background-color: rgba(70, 120, 180, 0.5);
#         font-weight: bold;
#         border: 1px solid #555;
#         color: #fff;
#         font-family: monospace;
#         align-items: center;
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- Google Drive ---
# FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

# # --- Session State defaults ---
# if 'selected_items' not in st.session_state:
#     st.session_state.selected_items = set()
# if 'select_all_checkbox' not in st.session_state:
#     st.session_state.select_all_checkbox = False
# if 'child_toggled' not in st.session_state:
#     st.session_state.child_toggled = False
# if 'sort_column' not in st.session_state:
#     st.session_state.sort_column = 'id'
# if 'sort_ascending' not in st.session_state:
#     st.session_state.sort_ascending = True

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

# def get_latest_entry(dico):
#     if not dico:
#         return None
#     try:
#         return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
#     except Exception:
#         return None

# def get_ingredient_name(data, ingredient_id):
#     item_id = str(ingredient_id)
#     if item_id in data:
#         return data[item_id].get('name', f"Item #{ingredient_id}")
#     return f"Item #{ingredient_id}"

# def get_recipe_html(data, item):
#     if not item.get('ingredients'):
#         return "<p style='color: #aaa;'><em>Cet item n'a pas de recette</em></p>"
#     html = "<div class='section-title'>🧪 Recette de fabrication</div>"
#     html += "<table class='recipe-table'><tr><th>Ingrédient</th><th>ID</th><th>Quantité</th></tr>"
#     for ing in item['ingredients']:
#         ing_name = get_ingredient_name(data, ing['id'])
#         html += f"<tr><td>{ing_name}</td><td>{ing['id']}</td><td>{ing['quantity']}</td></tr>"
#     html += "</table>"
#     return html

# def get_price_history_html(prix_dict, quantity, title):
#     if not prix_dict:
#         return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucun historique disponible</em></p></div>"
#     html = f"<div><div class='section-title'>{title}</div><table class='history-table'><tr><th>Date</th><th>Prix</th></tr>"
#     try:
#         sorted_dates = sorted(prix_dict.keys(), key=lambda k: datetime.fromisoformat(k), reverse=True)[:5]
#     except:
#         sorted_dates = sorted(prix_dict.keys(), reverse=True)[:5]
#     has_data = False
#     for date in sorted_dates:
#         price = prix_dict[date].get(str(quantity))
#         if price is not None:
#             has_data = True
#             try:
#                 date_formatted = datetime.fromisoformat(date).strftime('%d/%m/%Y %H:%M')
#             except:
#                 date_formatted = date
#             html += f"<tr><td>{date_formatted}</td><td>{price} K</td></tr>"
#     html += "</table></div>"
#     if not has_data:
#         return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucune donnée pour la quantité x{quantity}</em></p></div>"
#     return html

# def create_item_html(item, data, quantity):
#     prix = get_latest_entry(item.get("prix_hdv", {})) or {}
#     craft = get_latest_entry(item.get("cout_craft", {})) or {}
#     prix_val = prix.get(str(quantity), '-')
#     craft_val = craft.get(str(quantity), '-')
#     craft_icon = '✓' if item.get('is_craft') else '✗'
#     craft_class = 'craft-yes' if item.get('is_craft') else 'craft-no'
#     last_maj = item.get('last_maj', 'N/A')
#     if last_maj != 'N/A':
#         try: last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
#         except: pass

#     html = f"""
#     <details>
#     <summary>
#         <div class="arrow-cell"></div>
#         <div class="id-cell">{item.get('id')}</div>
#         <div class="item-name">{item.get('name')}</div>
#         <div class="item-info">{item.get('level')}</div>
#         <div class="item-info">{item.get('supertype', 'N/A')}</div>
#         <div class="item-info">{item.get('type', 'N/A')}</div>
#         <div class="{craft_class}">{craft_icon}</div>
#         <div class="price-value">{prix_val}</div>
#         <div class="price-value">{craft_val}</div>
#     </summary>
#     <div class='details-content'>
#         <div class='info-grid'>
#             <div class='info-item'>
#                 <div class='info-label'>ID</div><div class='info-value'>{item['id']}</div>
#                 <div class='info-label' style='margin-top: 10px;'>Niveau</div><div class='info-value'>{item['level']}</div>
#             </div>
#             <div class='info-item'>
#                 <div class='info-label'>Supertype</div><div class='info-value'>{item.get('supertype', 'N/A')}</div>
#                 <div class='info-label' style='margin-top: 10px;'>Type</div><div class='info-value'>{item.get('type', 'N/A')}</div>
#             </div>
#             <div class='info-item'>
#                 <div class='info-label'>Craftable</div>
#                 <div class='info-value'>{"Oui ✓" if item.get('is_craft') else "Non ✗"}</div>
#                 <div class='info-label' style='margin-top: 10px;'>Dernière MAJ</div>
#                 <div class='info-value'>{last_maj}</div>
#             </div>
#         </div>
#         <hr>
#     """
#     if item.get('is_craft') and item.get('ingredients'):
#         html += get_recipe_html(data, item) + "<hr>"
#     html += f"""
#         <div class='price-grid'>
#             {get_price_history_html(item.get('prix_hdv', {}), quantity, f"📊 Prix HDV (x{quantity})")}
#             {get_price_history_html(item.get('cout_craft', {}), quantity, f"📊 Coût Craft (x{quantity})")}
#         </div>
#     </div></details>"""
#     return html

# # --- PAGE ---
# st.title("🎮 Encyclopédie des Items")
# with st.spinner("Chargement des données depuis Google Drive..."):
#     data = charger_donnees()

# if not data:
#     st.error("❌ Impossible de charger les données")
#     st.stop()

# st.success(f"✅ {len(data)} items chargés avec succès")

# col_refresh, _ = st.columns([1, 5])
# with col_refresh:
#     if st.button("🔄 Rafraîchir"):
#         st.cache_data.clear()
#         st.rerun()

# # --- Sidebar ---
# with st.sidebar:
#     st.header("⚙️ Paramètres")
#     quantity = st.selectbox("Quantité pour les prix", [1, 10, 100, 1000], index=1)
#     st.markdown("---")
#     st.markdown("### 📋 Filtres")
#     search_term = st.text_input("🔍 Rechercher par nom ou ID", "")
#     all_supertypes = sorted(set(item.get('supertype', 'N/A') for item in data.values()))
#     supertype_filter = st.multiselect("Supertype", options=all_supertypes)
#     all_types = sorted(set(item.get('type', 'N/A') for item in data.values()))
#     type_filter = st.multiselect("Type", options=all_types)
#     craft_filter = st.radio("Type d'item", ["Tous", "Craftables uniquement", "Non craftables"])
#     max_level = max((item.get('level', 0) for item in data.values()), default=200)
#     level_range = st.slider("Niveau", 1, max_level, (1, max_level))

# # --- Filtrage ---
# rows = [{
#     "id": item.get("id"),
#     "name": item.get("name"),
#     "level": item.get("level"),
#     "supertype": item.get("supertype"),
#     "type": item.get("type"),
#     "is_craft": item.get("is_craft"),
#     "_item_id": item_id
# } for item_id, item in data.items()]
# df = pd.DataFrame(rows)

# if search_term:
#     df = df[df["name"].str.contains(search_term, case=False, na=False) | df["id"].astype(str).str.contains(search_term)]
# if supertype_filter:
#     df = df[df["supertype"].isin(supertype_filter)]
# if type_filter:
#     df = df[df["type"].isin(type_filter)]
# if craft_filter == "Craftables uniquement":
#     df = df[df["is_craft"]]
# elif craft_filter == "Non craftables":
#     df = df[~df["is_craft"]]
# df = df[(df["level"] >= level_range[0]) & (df["level"] <= level_range[1])]

# # --- Tri et pagination ---
# st.markdown(f"### 📦 Items ({len(df)} résultats)")

# # Tri basé sur le session state
# df_display = df.sort_values(by=st.session_state.sort_column, ascending=st.session_state.sort_ascending).reset_index(drop=True)

# items_per_page = st.selectbox("Items par page", [10, 20, 50, 100], index=1)
# total_pages = max((len(df_display) - 1) // items_per_page + 1, 1)
# col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
# with col_page2:
#     current_page = st.number_input(f"Page (1-{total_pages})", 1, total_pages, 1)
# start_idx, end_idx = (current_page - 1) * items_per_page, min(current_page * items_per_page, len(df_display))
# df_page = df_display.iloc[start_idx:end_idx]

# # --- Helpers pour callbacks ---
# def make_child_changed(widget_key, item_real_id):
#     def _child_changed():
#         if st.session_state.get(widget_key):
#             st.session_state.selected_items.add(item_real_id)
#         else:
#             st.session_state.selected_items.discard(item_real_id)
#         st.session_state.child_toggled = True
#     return _child_changed

# def master_changed():
#     checked = st.session_state.get("select_all_checkbox", False)
#     # ✅ Tous les items filtrés
#     all_filtered_ids = df_display['id'].tolist()
#     if checked:
#         st.session_state.selected_items.update(all_filtered_ids)
#     else:
#         st.session_state.selected_items.clear()
#     # Synchroniser les cases visibles
#     for _, row in df_page.iterrows():
#         item_id = row['_item_id']
#         widget_key = f"check_{item_id}_{current_page}"
#         st.session_state[widget_key] = checked
#     st.session_state.child_toggled = False

# # --- Callbacks pour les boutons de header ---
# def header_clicked(column_name):
#     def _callback():
#         if st.session_state.sort_column == column_name:
#             # Toggle l'ordre si on clique sur la même colonne
#             st.session_state.sort_ascending = not st.session_state.sort_ascending
#         else:
#             # Nouvelle colonne : commence par décroissant
#             st.session_state.sort_column = column_name
#             st.session_state.sort_ascending = False
#     return _callback

# def get_sort_arrow(column_name):
#     if st.session_state.sort_column == column_name:
#         return " ▼" if not st.session_state.sort_ascending else " ▲"
#     return ""

# # --- Header avec checkbox maître et boutons ---
# col_header_check, col_header_content = st.columns([0.03, 9.97])

# if st.session_state.get("child_toggled", False):
#     visible_ids = set(df_page['id'].tolist())
#     st.session_state.select_all_checkbox = visible_ids.issubset(st.session_state.selected_items)
#     st.session_state.child_toggled = False

# with col_header_check:
#     st.checkbox("Tout", key="select_all_checkbox", on_change=master_changed, label_visibility="collapsed")

# with col_header_content:
#     # Création d'une grille pour les boutons de header - AJUSTÉE pour correspondre au summary
#     header_cols = st.columns([0.03, 0.07, 0.20, 0.08, 0.12, 0.12, 0.08, 0.13, 0.13])
    
#     with header_cols[0]:
#         st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
#     with header_cols[1]:
#         st.button(f"ID{get_sort_arrow('id')}", key="btn_header_id", on_click=header_clicked('id'))
    
#     with header_cols[2]:
#         st.button(f"Nom{get_sort_arrow('name')}", key="btn_header_nom", on_click=header_clicked('name'))
    
#     with header_cols[3]:
#         st.button(f"Niveau{get_sort_arrow('level')}", key="btn_header_niveau", on_click=header_clicked('level'))
    
#     with header_cols[4]:
#         st.button(f"Supertype{get_sort_arrow('supertype')}", key="btn_header_supertype", on_click=header_clicked('supertype'))
    
#     with header_cols[5]:
#         st.button(f"Type{get_sort_arrow('type')}", key="btn_header_type", on_click=header_clicked('type'))
    
#     with header_cols[6]:
#         st.button(f"Craft{get_sort_arrow('is_craft')}", key="btn_header_craft", on_click=header_clicked('is_craft'))
    
#     with header_cols[7]:
#         st.button(f"Prix HDV", key="btn_header_prix_hdv")
    
#     with header_cols[8]:
#         st.button(f"Coût Craft", key="btn_header_cout_craft")

# # --- Affichage des items ---
# if len(df_page) > 0:
#     for _, row in df_page.iterrows():
#         item_id = row['_item_id']
#         item = data[item_id]
#         item_real_id = item.get('id')
#         col_check, col_content = st.columns([0.03, 9.97])

#         with col_check:
#             widget_key = f"check_{item_real_id}_{current_page}"
#             st.session_state[widget_key] = (item_real_id in st.session_state.selected_items)
#             st.checkbox("option technique", key=widget_key, on_change=make_child_changed(widget_key, item_real_id), label_visibility="collapsed")

#         with col_content:
#             st.markdown(create_item_html(item, data, quantity), unsafe_allow_html=True)
# else:
#     st.info("Aucun résultat ne correspond à vos critères de recherche.")

# # --- Statistiques ---
# st.markdown("---")
# if st.session_state.selected_items:
#     st.info(f"✓ {len(st.session_state.selected_items)} item(s) sélectionné(s) : {sorted(list(st.session_state.selected_items))}")
# col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
# with col_stat1:
#     st.metric("Total items", len(data))
# with col_stat2:
#     st.metric("Items craftables", sum(1 for item in data.values() if item.get('is_craft')))
# with col_stat3:
#     st.metric("Prix HDV disponibles", sum(1 for item in data.values() if item.get('prix_hdv')))
# with col_stat4:
#     st.metric("Coûts craft disponibles", sum(1 for item in data.values() if item.get('cout_craft')))




import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON

# Configuration
st.set_page_config(layout="wide")

st.markdown("# Page 3")
st.sidebar.markdown("# Page 3")

# --- CSS ---
st.markdown("""
<style>
    details { border: 1px solid #555; border-top: none; border-radius: 0; margin: 0; background-color: rgba(40, 50, 60, 0.6); }
    details:first-of-type { border-top: 1px solid #555; }
    summary {
        display: grid;
        grid-template-columns: 3% 7% 20% 8% 12% 12% 8% 13% 13%;
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
    hr { border: none; border-top: 1px solid #666; margin: 20px 0; }
    .craft-yes { color: #5eff5e; }
    .craft-no { color: #ff5e5e; }
    .price-value { color: #ffd966; }
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
        grid-template-columns: 3% 7% 20% 8% 12% 12% 8% 13% 13%;
        gap: 8px;
        padding: 16px 12px;
        background-color: rgba(70, 120, 180, 0.5);
        font-weight: bold;
        border: 1px solid #555;
        color: #fff;
        font-family: monospace;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Google Drive ---
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

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

def get_latest_entry(dico):
    if not dico:
        return None
    try:
        return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
    except Exception:
        return None

def get_ingredient_name(data, ingredient_id):
    item_id = str(ingredient_id)
    if item_id in data:
        return data[item_id].get('name', f"Item #{ingredient_id}")
    return f"Item #{ingredient_id}"

def get_recipe_html(data, item):
    if not item.get('ingredients'):
        return "<p style='color: #aaa;'><em>Cet item n'a pas de recette</em></p>"
    html = "<div class='section-title'>🧪 Recette de fabrication</div>"
    html += "<table class='recipe-table'><tr><th>Ingrédient</th><th>ID</th><th>Quantité</th></tr>"
    for ing in item['ingredients']:
        ing_name = get_ingredient_name(data, ing['id'])
        html += f"<tr><td>{ing_name}</td><td>{ing['id']}</td><td>{ing['quantity']}</td></tr>"
    html += "</table>"
    return html

def get_price_history_html(prix_dict, quantity, title):
    if not prix_dict:
        return f"<div><div class='section-title'>{title}</div><p style='color: #aaa;'><em>Aucun historique disponible</em></p></div>"
    html = f"<div><div class='section-title'>{title}</div><table class='history-table'><tr><th>Date</th><th>Prix</th></tr>"
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
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft = get_latest_entry(item.get("cout_craft", {})) or {}
    prix_val = prix.get(str(quantity), '-')
    craft_val = craft.get(str(quantity), '-')
    craft_icon = '✓' if item.get('is_craft') else '✗'
    craft_class = 'craft-yes' if item.get('is_craft') else 'craft-no'
    last_maj = item.get('last_maj', 'N/A')
    if last_maj != 'N/A':
        try: last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
        except: pass

    html = f"""
    <details>
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
        html += get_recipe_html(data, item) + "<hr>"
    html += f"""
        <div class='price-grid'>
            {get_price_history_html(item.get('prix_hdv', {}), quantity, f"📊 Prix HDV (x{quantity})")}
            {get_price_history_html(item.get('cout_craft', {}), quantity, f"📊 Coût Craft (x{quantity})")}
        </div>
    </div></details>"""
    return html

# --- PAGE ---
st.title("🎮 Encyclopédie des Items")
with st.spinner("Chargement des données depuis Google Drive..."):
    data = charger_donnees()

if not data:
    st.error("❌ Impossible de charger les données")
    st.stop()

st.success(f"✅ {len(data)} items chargés avec succès")

col_refresh, _ = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Rafraîchir"):
        st.cache_data.clear()
        st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    quantity = st.selectbox("Quantité pour les prix", [1, 10, 100, 1000], index=1)
    st.markdown("---")
    st.markdown("### 📋 Filtres")
    search_term = st.text_input("🔍 Rechercher par nom ou ID", "")
    all_supertypes = sorted(set(item.get('supertype', 'N/A') for item in data.values()))
    supertype_filter = st.multiselect("Supertype", options=all_supertypes)
    all_types = sorted(set(item.get('type', 'N/A') for item in data.values()))
    type_filter = st.multiselect("Type", options=all_types)
    craft_filter = st.radio("Type d'item", ["Tous", "Craftables uniquement", "Non craftables"])
    max_level = max((item.get('level', 0) for item in data.values()), default=200)
    level_range = st.slider("Niveau", 1, max_level, (1, max_level))

# --- Filtrage ---
rows = []
for item_id, item in data.items():
    # Extraire les prix pour la quantité sélectionnée
    prix_dict = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft_dict = get_latest_entry(item.get("cout_craft", {})) or {}
    
    # Convertir les valeurs en float pour le tri (gérer les '-' et None)
    prix_val = prix_dict.get(str(quantity))
    craft_val = craft_dict.get(str(quantity))
    
    try:
        prix_numeric = float(prix_val) if prix_val not in [None, '-'] else float('inf')
    except:
        prix_numeric = float('inf')
    
    try:
        craft_numeric = float(craft_val) if craft_val not in [None, '-'] else float('inf')
    except:
        craft_numeric = float('inf')
    
    rows.append({
        "id": item.get("id"),
        "name": item.get("name"),
        "level": item.get("level"),
        "supertype": item.get("supertype"),
        "type": item.get("type"),
        "is_craft": item.get("is_craft"),
        "prix_hdv": prix_numeric,
        "cout_craft": craft_numeric,
        "_item_id": item_id
    })

df = pd.DataFrame(rows)

if search_term:
    df = df[df["name"].str.contains(search_term, case=False, na=False) | df["id"].astype(str).str.contains(search_term)]
if supertype_filter:
    df = df[df["supertype"].isin(supertype_filter)]
if type_filter:
    df = df[df["type"].isin(type_filter)]
if craft_filter == "Craftables uniquement":
    df = df[df["is_craft"]]
elif craft_filter == "Non craftables":
    df = df[~df["is_craft"]]
df = df[(df["level"] >= level_range[0]) & (df["level"] <= level_range[1])]

# --- Tri et pagination ---
st.markdown(f"### 📦 Items ({len(df)} résultats)")

# Tri basé sur le session state
df_display = df.sort_values(by=st.session_state.sort_column, ascending=st.session_state.sort_ascending).reset_index(drop=True)

items_per_page = st.selectbox("Items par page", [10, 20, 50, 100], index=1)
total_pages = max((len(df_display) - 1) // items_per_page + 1, 1)
col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
with col_page2:
    current_page = st.number_input(f"Page (1-{total_pages})", 1, total_pages, 1)
start_idx, end_idx = (current_page - 1) * items_per_page, min(current_page * items_per_page, len(df_display))
df_page = df_display.iloc[start_idx:end_idx]

# --- Helpers pour callbacks ---
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
    # Création d'une grille pour les boutons de header - AJUSTÉE pour correspondre au summary
    header_cols = st.columns([0.03, 0.07, 0.20, 0.08, 0.12, 0.12, 0.08, 0.13, 0.13])
    
    with header_cols[0]:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    with header_cols[1]:
        st.button(f"ID{get_sort_arrow('id')}", key="btn_header_id", on_click=header_clicked('id'))
    
    with header_cols[2]:
        st.button(f"Nom{get_sort_arrow('name')}", key="btn_header_nom", on_click=header_clicked('name'))
    
    with header_cols[3]:
        st.button(f"Niveau{get_sort_arrow('level')}", key="btn_header_niveau", on_click=header_clicked('level'))
    
    with header_cols[4]:
        st.button(f"Supertype{get_sort_arrow('supertype')}", key="btn_header_supertype", on_click=header_clicked('supertype'))
    
    with header_cols[5]:
        st.button(f"Type{get_sort_arrow('type')}", key="btn_header_type", on_click=header_clicked('type'))
    
    with header_cols[6]:
        st.button(f"Craft{get_sort_arrow('is_craft')}", key="btn_header_craft", on_click=header_clicked('is_craft'))
    
    with header_cols[7]:
        st.button(f"Prix HDV{get_sort_arrow('prix_hdv')}", key="btn_header_prix_hdv", on_click=header_clicked('prix_hdv'))
    
    with header_cols[8]:
        st.button(f"Coût Craft{get_sort_arrow('cout_craft')}", key="btn_header_cout_craft", on_click=header_clicked('cout_craft'))

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
            st.markdown(create_item_html(item, data, quantity), unsafe_allow_html=True)
else:
    st.info("Aucun résultat ne correspond à vos critères de recherche.")

# --- Statistiques ---
st.markdown("---")
if st.session_state.selected_items:
    st.info(f"✓ {len(st.session_state.selected_items)} item(s) sélectionné(s) : {sorted(list(st.session_state.selected_items))}")
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
with col_stat1:
    st.metric("Total items", len(data))
with col_stat2:
    st.metric("Items craftables", sum(1 for item in data.values() if item.get('is_craft')))
with col_stat3:
    st.metric("Prix HDV disponibles", sum(1 for item in data.values() if item.get('prix_hdv')))
with col_stat4:
    st.metric("Coûts craft disponibles", sum(1 for item in data.values() if item.get('cout_craft')))