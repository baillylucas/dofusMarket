# import streamlit as st
# import streamlit.components.v1 as components
# import pandas as pd
# from datetime import datetime
# from googleDriveJSON import GoogleDriveJSON
# import json

# st.markdown("# Page 3")
# st.sidebar.markdown("# Page 3")

# # Configuration Google Drive
# FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

# @st.cache_data(ttl=600)
# def charger_donnees():
#     """Charge les données depuis Google Drive"""
#     try:
#         drive = GoogleDriveJSON(FILE_ID)
#         data = drive.read()
#         # Garder uniquement les clés numériques
#         data = {k: v for k, v in data.items() if str(k).isdigit()}
#         return data
#     except Exception as e:
#         st.error(f"Erreur lors du chargement : {e}")
#         return None

# def get_latest_entry(dico):
#     """Récupère l'entrée la plus récente d'un dictionnaire daté"""
#     if not dico:
#         return None
#     try:
#         return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
#     except Exception:
#         return None

# def get_ingredient_name(data, ingredient_id):
#     """Récupère le nom d'un ingrédient par son ID"""
#     item_id = str(ingredient_id)
#     if item_id in data:
#         return data[item_id].get('name', f"Item #{ingredient_id}")
#     return f"Item #{ingredient_id}"

# def get_recipe_html(data, item):
#     """Génère le HTML de la recette"""
#     if not item.get('ingredients'):
#         return "<p><em>Cet item n'a pas de recette</em></p>"
    
#     html = "<div style='margin: 15px 0;'><strong>🧪 Recette de fabrication</strong><table style='width: 100%; margin-top: 10px; border-collapse: collapse;'>"
#     html += "<tr style='background-color: rgba(28, 131, 225, 0.2);'><th style='padding: 8px; border: 1px solid #444;'>Ingrédient</th><th style='padding: 8px; border: 1px solid #444;'>ID</th><th style='padding: 8px; border: 1px solid #444;'>Quantité</th></tr>"
    
#     for ing in item['ingredients']:
#         ing_name = get_ingredient_name(data, ing['id'])
#         html += f"<tr><td style='padding: 8px; border: 1px solid #444;'>{ing_name}</td><td style='padding: 8px; border: 1px solid #444;'>{ing['id']}</td><td style='padding: 8px; border: 1px solid #444;'>{ing['quantity']}</td></tr>"
    
#     html += "</table></div>"
#     return html

# def get_price_history_html(prix_dict, quantity, title):
#     """Génère le HTML de l'historique des prix"""
#     if not prix_dict:
#         return f"<p><em>Aucun historique disponible</em></p>"
    
#     html = f"<div style='margin: 15px 0;'><strong>{title}</strong><table style='width: 100%; margin-top: 10px; border-collapse: collapse;'>"
#     html += "<tr style='background-color: rgba(28, 131, 225, 0.2);'><th style='padding: 8px; border: 1px solid #444;'>Date</th><th style='padding: 8px; border: 1px solid #444;'>Prix</th></tr>"
    
#     try:
#         sorted_dates = sorted(prix_dict.keys(), key=lambda k: datetime.fromisoformat(k), reverse=True)[:5]
#     except:
#         sorted_dates = sorted(prix_dict.keys(), reverse=True)[:5]
    
#     for date in sorted_dates:
#         price = prix_dict[date].get(str(quantity))
#         if price is not None:
#             try:
#                 date_formatted = datetime.fromisoformat(date).strftime('%d/%m/%Y %H:%M')
#             except:
#                 date_formatted = date
#             html += f"<tr><td style='padding: 8px; border: 1px solid #444;'>{date_formatted}</td><td style='padding: 8px; border: 1px solid #444;'>{price} K</td></tr>"
    
#     html += "</table></div>"
#     return html

# def create_custom_expander(item_id, item, data, quantity, index):
#     """Crée un expander personnalisé en HTML/CSS/JS"""
    
#     prix = get_latest_entry(item.get("prix_hdv", {})) or {}
#     craft = get_latest_entry(item.get("cout_craft", {})) or {}
    
#     prix_val = prix.get(str(quantity), '-')
#     craft_val = craft.get(str(quantity), '-')
#     craft_icon = '✓' if item.get('is_craft') else '✗'
    
#     last_maj = item.get('last_maj', 'N/A')
#     if last_maj != 'N/A':
#         try:
#             last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
#         except:
#             pass
    
#     # Contenu détaillé
#     detail_content = f"""
#     <div style="padding: 20px; background-color: rgba(28, 131, 225, 0.05);">
#         <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
#             <div>
#                 <div style="font-size: 0.85em; color: #888;">ID</div>
#                 <div style="font-size: 1.5em; font-weight: bold;">{item['id']}</div>
#                 <div style="font-size: 0.85em; color: #888; margin-top: 10px;">Niveau</div>
#                 <div style="font-size: 1.5em; font-weight: bold;">{item['level']}</div>
#             </div>
#             <div>
#                 <div style="font-size: 0.85em; color: #888;">Supertype</div>
#                 <div style="font-size: 1.5em; font-weight: bold;">{item.get('supertype', 'N/A')}</div>
#                 <div style="font-size: 0.85em; color: #888; margin-top: 10px;">Type</div>
#                 <div style="font-size: 1.5em; font-weight: bold;">{item.get('type', 'N/A')}</div>
#             </div>
#             <div>
#                 <div style="font-size: 0.85em; color: #888;">Craftable</div>
#                 <div style="font-size: 1.5em; font-weight: bold;">{"Oui ✓" if item.get('is_craft') else "Non ✗"}</div>
#                 <div style="font-size: 0.85em; color: #888; margin-top: 10px;">Dernière MAJ</div>
#                 <div style="font-size: 1.5em; font-weight: bold;">{last_maj}</div>
#             </div>
#         </div>
#         <hr style="border: none; border-top: 1px solid #444; margin: 20px 0;">
#     """
    
#     # Ajouter la recette si craftable
#     if item.get('is_craft') and item.get('ingredients'):
#         detail_content += get_recipe_html(data, item)
#         detail_content += "<hr style='border: none; border-top: 1px solid #444; margin: 20px 0;'>"
    
#     # Ajouter les historiques de prix
#     detail_content += "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>"
#     detail_content += "<div>" + get_price_history_html(item.get('prix_hdv', {}), quantity, f"📊 Prix HDV (x{quantity})") + "</div>"
#     detail_content += "<div>" + get_price_history_html(item.get('cout_craft', {}), quantity, f"📊 Coût Craft (x{quantity})") + "</div>"
#     detail_content += "</div>"
    
#     detail_content += "</div>"
    
#     html = f"""
#     <div class="custom-expander" style="border: 1px solid rgba(250, 250, 250, 0.2); border-radius: 0; margin: 0; background-color: rgba(28, 131, 225, 0.05);">
#         <div class="expander-header" onclick="toggleExpander({index})" style="
#             display: grid; 
#             grid-template-columns: 7% 23% 8% 12% 12% 8% 13% 13%; 
#             gap: 8px; 
#             padding: 12px; 
#             cursor: pointer; 
#             background-color: rgba(28, 131, 225, 0.05);
#             border-radius: 0;
#             font-family: monospace;
#             align-items: center;
#             transition: background-color 0.2s;
#         " onmouseover="this.style.backgroundColor='rgba(28, 131, 225, 0.15)'" onmouseout="this.style.backgroundColor='rgba(28, 131, 225, 0.05)'">
#             <div style="font-weight: bold;">▶ {item.get('id')}</div>
#             <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{item.get('name')}</div>
#             <div>{item.get('level')}</div>
#             <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{item.get('supertype', 'N/A')}</div>
#             <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{item.get('type', 'N/A')}</div>
#             <div>{craft_icon}</div>
#             <div>{prix_val}</div>
#             <div>{craft_val}</div>
#         </div>
#         <div id="expander-content-{index}" class="expander-content" style="display: none; border-top: 1px solid rgba(250, 250, 250, 0.2);">
#             {detail_content}
#         </div>
#     </div>
    
#     <script>
#     function toggleExpander(index) {{
#         var content = document.getElementById('expander-content-' + index);
#         var header = content.previousElementSibling;
#         var arrow = header.querySelector('div:first-child');
        
#         if (content.style.display === 'none') {{
#             content.style.display = 'block';
#             arrow.textContent = arrow.textContent.replace('▶', '▼');
#         }} else {{
#             content.style.display = 'none';
#             arrow.textContent = arrow.textContent.replace('▼', '▶');
#         }}
#     }}
#     </script>
#     """
    
#     return html

# # --- CHARGEMENT DES DONNÉES ---
# st.title("🎮 Encyclopédie des Items")

# with st.spinner("Chargement des données depuis Google Drive..."):
#     data = charger_donnees()

# if data is None or len(data) == 0:
#     st.error("❌ Impossible de charger les données")
#     st.stop()

# st.success(f"✅ {len(data)} items chargés avec succès")

# # Bouton de rafraîchissement
# col_refresh, col_empty = st.columns([1, 5])
# with col_refresh:
#     if st.button("🔄 Rafraîchir"):
#         st.cache_data.clear()
#         st.rerun()

# # --- SIDEBAR : PARAMÈTRES ET FILTRES ---
# with st.sidebar:
#     st.header("⚙️ Paramètres")
    
#     # Sélecteur de quantité
#     quantity = st.selectbox(
#         "Quantité pour les prix",
#         options=[1, 10, 100, 1000],
#         index=1
#     )
    
#     st.markdown("---")
#     st.markdown("### 📋 Filtres")
    
#     # Recherche
#     search_term = st.text_input("🔍 Rechercher par nom ou ID", "")
    
#     # Filtres par supertype et type
#     all_supertypes = sorted(set(item.get('supertype', 'N/A') for item in data.values()))
#     supertype_filter = st.multiselect(
#         "Supertype",
#         options=all_supertypes,
#         default=[]
#     )
    
#     all_types = sorted(set(item.get('type', 'N/A') for item in data.values()))
#     type_filter = st.multiselect(
#         "Type",
#         options=all_types,
#         default=[]
#     )
    
#     # Filtre craftable
#     craft_filter = st.radio(
#         "Type d'item",
#         options=["Tous", "Craftables uniquement", "Non craftables"],
#         index=0
#     )
    
#     # Filtre par niveau
#     max_level = max((item.get('level', 0) for item in data.values()), default=200)
#     level_range = st.slider(
#         "Niveau",
#         min_value=1,
#         max_value=max_level,
#         value=(1, max_level)
#     )

# # --- TRANSFORMATION EN DATAFRAME POUR FILTRAGE ---
# rows = []
# for item_id, item in data.items():
#     rows.append({
#         "id": item.get("id"),
#         "name": item.get("name"),
#         "level": item.get("level"),
#         "supertype": item.get("supertype"),
#         "type": item.get("type"),
#         "is_craft": item.get("is_craft"),
#         "_item_id": item_id
#     })

# df = pd.DataFrame(rows)

# # --- APPLICATION DES FILTRES ---
# if search_term:
#     df = df[
#         df["name"].str.contains(search_term, case=False, na=False) |
#         df["id"].astype(str).str.contains(search_term, na=False)
#     ]

# if supertype_filter:
#     df = df[df["supertype"].isin(supertype_filter)]

# if type_filter:
#     df = df[df["type"].isin(type_filter)]

# if craft_filter == "Craftables uniquement":
#     df = df[df["is_craft"] == True]
# elif craft_filter == "Non craftables":
#     df = df[df["is_craft"] == False]

# df = df[(df["level"] >= level_range[0]) & (df["level"] <= level_range[1])]

# # --- TRI ---
# st.markdown(f"### 📦 Items ({len(df)} résultats)")

# col_sort1, col_sort2 = st.columns(2)
# with col_sort1:
#     sort_column = st.selectbox(
#         "Trier par",
#         options=['id', 'name', 'level', 'supertype', 'type'],
#         index=1
#     )

# with col_sort2:
#     sort_order = st.radio(
#         "Ordre",
#         options=['Croissant', 'Décroissant'],
#         horizontal=True,
#         index=0
#     )

# ascending = (sort_order == 'Croissant')
# df_display = df.sort_values(by=sort_column, ascending=ascending).reset_index(drop=True)

# # --- PAGINATION ---
# items_per_page = st.selectbox("Items par page", [10, 20, 50, 100], index=1)
# total_pages = max((len(df_display) - 1) // items_per_page + 1, 1)

# col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
# with col_page2:
#     current_page = st.number_input(
#         f"Page (1-{total_pages})",
#         min_value=1,
#         max_value=total_pages,
#         value=1,
#         step=1
#     )

# start_idx = (current_page - 1) * items_per_page
# end_idx = min(start_idx + items_per_page, len(df_display))

# df_page = df_display.iloc[start_idx:end_idx]

# # --- EN-TÊTE DU TABLEAU ---
# st.markdown("""
# <div style="display: grid; grid-template-columns: 7% 23% 8% 12% 12% 8% 13% 13%; gap: 8px; padding: 12px; background-color: rgba(28, 131, 225, 0.3); font-weight: bold; border: 1px solid rgba(250, 250, 250, 0.2); border-radius: 0; font-family: monospace;">
#     <div>ID</div>
#     <div>Nom</div>
#     <div>Niveau</div>
#     <div>Supertype</div>
#     <div>Type</div>
#     <div>Craft</div>
#     <div>Prix HDV</div>
#     <div>Coût Craft</div>
# </div>
# """, unsafe_allow_html=True)

# # --- AFFICHAGE DES LIGNES AVEC EXPANDERS PERSONNALISÉS ---
# if len(df_page) > 0:
#     all_html = ""
#     for idx, row in df_page.iterrows():
#         item_id = row['_item_id']
#         item = data[item_id]
#         all_html += create_custom_expander(item_id, item, data, quantity, idx)
    
#     components.html(all_html, height=len(df_page) * 60, scrolling=True)
# else:
#     st.info("Aucun résultat ne correspond à vos critères de recherche.")

# # --- STATISTIQUES ---
# st.markdown("---")
# col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

# with col_stat1:
#     st.metric("Total items", len(data))

# with col_stat2:
#     craftable_count = sum(1 for item in data.values() if item.get('is_craft'))
#     st.metric("Items craftables", craftable_count)

# with col_stat3:
#     with_hdv = sum(1 for item in data.values() if item.get('prix_hdv'))
#     st.metric("Prix HDV disponibles", with_hdv)

# with col_stat4:
#     with_craft = sum(1 for item in data.values() if item.get('cout_craft'))
#     st.metric("Coûts craft disponibles", with_craft)










































import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON
import json

st.markdown("# Page 3")
st.sidebar.markdown("# Page 3")

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
    
    html = "<div style='margin: 15px 0;'><strong style='color: #fff;'>🧪 Recette de fabrication</strong><table style='width: 100%; margin-top: 10px; border-collapse: collapse;'>"
    html += "<tr style='background-color: rgba(100, 180, 255, 0.3);'><th style='padding: 8px; border: 1px solid #666; color: #fff;'>Ingrédient</th><th style='padding: 8px; border: 1px solid #666; color: #fff;'>ID</th><th style='padding: 8px; border: 1px solid #666; color: #fff;'>Quantité</th></tr>"
    
    for ing in item['ingredients']:
        ing_name = get_ingredient_name(data, ing['id'])
        html += f"<tr style='background-color: rgba(50, 50, 60, 0.5);'><td style='padding: 8px; border: 1px solid #666; color: #ddd;'>{ing_name}</td><td style='padding: 8px; border: 1px solid #666; color: #ddd;'>{ing['id']}</td><td style='padding: 8px; border: 1px solid #666; color: #ddd;'>{ing['quantity']}</td></tr>"
    
    html += "</table></div>"
    return html

def get_price_history_html(prix_dict, quantity, title):
    """Génère le HTML de l'historique des prix"""
    if not prix_dict:
        return f"<p style='color: #aaa;'><em>Aucun historique disponible</em></p>"
    
    html = f"<div style='margin: 15px 0;'><strong style='color: #fff;'>{title}</strong><table style='width: 100%; margin-top: 10px; border-collapse: collapse;'>"
    html += "<tr style='background-color: rgba(100, 180, 255, 0.3);'><th style='padding: 8px; border: 1px solid #666; color: #fff;'>Date</th><th style='padding: 8px; border: 1px solid #666; color: #fff;'>Prix</th></tr>"
    
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
            html += f"<tr style='background-color: rgba(50, 50, 60, 0.5);'><td style='padding: 8px; border: 1px solid #666; color: #ddd;'>{date_formatted}</td><td style='padding: 8px; border: 1px solid #666; color: #ddd;'>{price} K</td></tr>"
    
    html += "</table></div>"
    
    if not has_data:
        return f"<p style='color: #aaa;'><em>Aucune donnée pour la quantité x{quantity}</em></p>"
    
    return html

def create_custom_expander(item_id, item, data, quantity, index):
    """Crée un expander personnalisé en HTML/CSS/JS"""
    
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft = get_latest_entry(item.get("cout_craft", {})) or {}
    
    prix_val = prix.get(str(quantity), '-')
    craft_val = craft.get(str(quantity), '-')
    craft_icon = '✓' if item.get('is_craft') else '✗'
    
    last_maj = item.get('last_maj', 'N/A')
    if last_maj != 'N/A':
        try:
            last_maj = datetime.fromisoformat(last_maj).strftime('%d/%m/%Y %H:%M')
        except:
            pass
    
    # Contenu détaillé
    detail_content = f"""
    <div style="padding: 20px; background-color: rgba(30, 40, 50, 0.8);">
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div>
                <div style="font-size: 0.85em; color: #888;">ID</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{item['id']}</div>
                <div style="font-size: 0.85em; color: #888; margin-top: 10px;">Niveau</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{item['level']}</div>
            </div>
            <div>
                <div style="font-size: 0.85em; color: #888;">Supertype</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{item.get('supertype', 'N/A')}</div>
                <div style="font-size: 0.85em; color: #888; margin-top: 10px;">Type</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{item.get('type', 'N/A')}</div>
            </div>
            <div>
                <div style="font-size: 0.85em; color: #888;">Craftable</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{"Oui ✓" if item.get('is_craft') else "Non ✗"}</div>
                <div style="font-size: 0.85em; color: #888; margin-top: 10px;">Dernière MAJ</div>
                <div style="font-size: 1.5em; font-weight: bold; color: #fff;">{last_maj}</div>
            </div>
        </div>
        <hr style="border: none; border-top: 1px solid #666; margin: 20px 0;">
    """
    
    # Ajouter la recette si craftable
    if item.get('is_craft') and item.get('ingredients'):
        detail_content += get_recipe_html(data, item)
        detail_content += "<hr style='border: none; border-top: 1px solid #666; margin: 20px 0;'>"
    
    # Ajouter les historiques de prix
    detail_content += "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>"
    detail_content += "<div>" + get_price_history_html(item.get('prix_hdv', {}), quantity, f"📊 Prix HDV (x{quantity})") + "</div>"
    detail_content += "<div>" + get_price_history_html(item.get('cout_craft', {}), quantity, f"📊 Coût Craft (x{quantity})") + "</div>"
    detail_content += "</div>"
    
    detail_content += "</div>"
    
    html = f"""
    <div class="custom-expander" style="border: 1px solid #555; border-radius: 0; margin: 0; background-color: rgba(40, 50, 60, 0.6);">
        <div class="expander-header" onclick="toggleExpander('{index}')" style="
            display: grid; 
            grid-template-columns: 7% 23% 8% 12% 12% 8% 13% 13%; 
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
        " onmouseover="this.style.backgroundColor='rgba(70, 120, 180, 0.4)'" onmouseout="this.style.backgroundColor='rgba(40, 50, 60, 0.6)'">
            <div id="arrow-{index}" style="font-weight: bold; color: #6db3ff;">▶ {item.get('id')}</div>
            <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #fff;">{item.get('name')}</div>
            <div style="color: #ddd;">{item.get('level')}</div>
            <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #ddd;">{item.get('supertype', 'N/A')}</div>
            <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #ddd;">{item.get('type', 'N/A')}</div>
            <div style="color: {'#5eff5e' if item.get('is_craft') else '#ff5e5e'};">{craft_icon}</div>
            <div style="color: #ffd966;">{prix_val}</div>
            <div style="color: #ffd966;">{craft_val}</div>
        </div>
        <div id="expander-content-{index}" class="expander-content" style="display: none; border-top: 1px solid #555;">
            {detail_content}
        </div>
    </div>
    """
    
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

# --- CONTENEUR POUR ALIGNER HEADER ET ITEMS ---
st.markdown('<div style="width: 100%;">', unsafe_allow_html=True)

# --- EN-TÊTE DU TABLEAU ---
st.markdown("""
<div style="display: grid; grid-template-columns: 7% 23% 8% 12% 12% 8% 13% 13%; gap: 8px; padding: 12px; background-color: rgba(70, 120, 180, 0.5); font-weight: bold; border: 1px solid #555; border-radius: 0; font-family: monospace; color: #fff; margin-bottom: 0;">
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

# --- AFFICHAGE DES LIGNES AVEC EXPANDERS PERSONNALISÉS ---
if len(df_page) > 0:
    all_html = """
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
    </style>
    <script>
        function toggleExpander(index) {
            var content = document.getElementById('expander-content-' + index);
            var arrow = document.getElementById('arrow-' + index);
            
            if (content.style.display === 'none' || content.style.display === '') {
                content.style.display = 'block';
                arrow.innerHTML = arrow.innerHTML.replace('▶', '▼');
                // Envoyer la nouvelle hauteur à Streamlit
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: document.body.scrollHeight}, '*');
            } else {
                content.style.display = 'none';
                arrow.innerHTML = arrow.innerHTML.replace('▼', '▶');
                // Envoyer la nouvelle hauteur à Streamlit
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: document.body.scrollHeight}, '*');
            }
        }
        
        // S'assurer que la hauteur est correcte au chargement
        window.addEventListener('load', function() {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: document.body.scrollHeight}, '*');
        });
    </script>
    """
    for idx, row in df_page.iterrows():
        item_id = row['_item_id']
        item = data[item_id]
        all_html += create_custom_expander(item_id, item, data, quantity, idx)
    
    # Calculer la hauteur : ~52px par ligne fermée + marge de sécurité
    estimated_height = len(df_page) * 52 + 50
    
    # Pas de scrollbar, hauteur estimée (sera ajustée dynamiquement)
    components.html(all_html, height=estimated_height, scrolling=False)
else:
    st.info("Aucun résultat ne correspond à vos critères de recherche.")

st.markdown('</div>', unsafe_allow_html=True)

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