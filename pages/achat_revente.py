import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON
from utils import (
    add_items_to_scrapper,
    get_user_groups, add_items_to_group, remove_items_from_group,
    get_items_in_groups, get_all_ingredients_recursive
)

# Configuration
st.set_page_config(layout="wide")

st.markdown("# 💰 Achat / Revente")

st.sidebar.markdown("# ⚙️ Filtres")

# --- Google Drive ---
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"
SERVICE_ACCOUNT_FILE = "credentials/service_account.json"

# --- Session State defaults ---
if 'selected_items_ar' not in st.session_state:
    st.session_state.selected_items_ar = set()
if 'user_groups' not in st.session_state:
    st.session_state.user_groups = {}
if 'notification_shown_ar' not in st.session_state:
    st.session_state.notification_shown_ar = False

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

def get_price_for_quantity(prices_dict, qty_str):
    """Récupère le prix pour une quantité donnée"""
    if not prices_dict:
        return None
    price = prices_dict.get(qty_str)
    if price is None or price == -1:
        return None
    return int(price)

def find_arbitrage_opportunities(item, prix_dict, min_profit_pct, max_profit_pct):
    """
    Trouve les opportunités d'arbitrage pour un item.
    Compare uniquement les quantités adjacentes (facteur 10x).

    Retourne une liste d'opportunités avec les détails.
    """
    opportunities = []

    # Récupérer les prix pour chaque quantité
    prices = {
        1: get_price_for_quantity(prix_dict, "1"),
        10: get_price_for_quantity(prix_dict, "10"),
        100: get_price_for_quantity(prix_dict, "100"),
        1000: get_price_for_quantity(prix_dict, "1000")
    }

    # Paires adjacentes autorisées (facteur 10x)
    adjacent_pairs = [
        (1, 10),
        (10, 100),
        (100, 1000)
    ]

    for qty_small, qty_large in adjacent_pairs:
        price_small = prices[qty_small]
        price_large = prices[qty_large]

        if price_small is None or price_large is None:
            continue

        # Cas 1: Acheter en petite quantité (10 fois), revendre en grande quantité
        # Ex: Acheter 10×x1 à 10K chacun = 100K, revendre x10 à 200K = bénéfice 100K
        cost_buying_small = price_small * 10  # On achète 10 fois la petite quantité
        revenue_selling_large = price_large

        if cost_buying_small > 0:
            profit_case1 = revenue_selling_large - cost_buying_small
            profit_pct_case1 = (profit_case1 / cost_buying_small) * 100

            if min_profit_pct <= profit_pct_case1 <= max_profit_pct:
                opportunities.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "iconId": item.get("iconId", item.get("id")),
                    "supertype": item.get("supertype"),
                    "achat": price_small,
                    "qty_achat": f"x{qty_small}",
                    "nb_achats": 10,
                    "revente": price_large,
                    "qty_revente": f"x{qty_large}",
                    "nb_reventes": 1,
                    "cout_total": cost_buying_small,
                    "revenu_total": revenue_selling_large,
                    "benefice": profit_case1,
                    "benefice_pct": profit_pct_case1
                })

        # Cas 2: Acheter en grande quantité, revendre en petite quantité (10 fois)
        # Ex: Acheter x10 à 80K, revendre 10×x1 à 10K chacun = 100K = bénéfice 20K
        cost_buying_large = price_large
        revenue_selling_small = price_small * 10  # On revend 10 fois la petite quantité

        if cost_buying_large > 0:
            profit_case2 = revenue_selling_small - cost_buying_large
            profit_pct_case2 = (profit_case2 / cost_buying_large) * 100

            if min_profit_pct <= profit_pct_case2 <= max_profit_pct:
                opportunities.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "iconId": item.get("iconId", item.get("id")),
                    "supertype": item.get("supertype"),
                    "achat": price_large,
                    "qty_achat": f"x{qty_large}",
                    "nb_achats": 1,
                    "revente": price_small,
                    "qty_revente": f"x{qty_small}",
                    "nb_reventes": 10,
                    "cout_total": cost_buying_large,
                    "revenu_total": revenue_selling_small,
                    "benefice": profit_case2,
                    "benefice_pct": profit_pct_case2
                })

    return opportunities

# --- PAGE ---
with st.spinner("Chargement des données depuis Google Drive..."):
    data = charger_donnees()

if not data:
    st.error("❌ Impossible de charger les données")
    st.stop()

# Toujours charger les groupes de l'utilisateur
st.session_state.user_groups = get_user_groups()

if not st.session_state.notification_shown_ar:
    st.toast(f"✅ {len(data)} items chargés avec succès", icon="✅")
    st.session_state.notification_shown_ar = True

# --- Supertypes des HDV Ressources et Consommables ---
SUPERTYPES_HDV_RESSOURCES = ["Ressource"]
SUPERTYPES_HDV_CONSOMMABLES = ["Consommable", "Consommables de combat"]
SUPERTYPES_HDV_TARGET = SUPERTYPES_HDV_RESSOURCES + SUPERTYPES_HDV_CONSOMMABLES

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📊 Rentabilité")
    col_min, col_max = st.columns(2)
    with col_min:
        min_profit_pct = st.number_input("Min %", min_value=-100, max_value=1000, value=5, step=1, key="ar_min_profit")
    with col_max:
        max_profit_pct = st.number_input("Max %", min_value=-100, max_value=1000, value=100, step=1, key="ar_max_profit")

    st.markdown("---")

    # Filtre par groupes
    group_options = {group_id: f"{group_data['name']} ({group_data['owner']})"
                     for group_id, group_data in st.session_state.user_groups.items()}
    selected_group_filters = st.multiselect(
        "Filtrer par groupe(s)",
        options=list(group_options.keys()),
        format_func=lambda x: group_options[x],
        key="ar_group_filter_multiselect"
    )

    search_term = st.text_input("🔍 Rechercher par nom ou ID", "", key="ar_search")

    # Filtre par supertype (identique à prices.py)
    all_supertypes = sorted(set(item.get('supertype', 'N/A') for item in data.values()))
    supertype_filter = st.multiselect("Supertype", options=all_supertypes, key="ar_supertype")

    # Filtre par type (identique à prices.py)
    all_types = sorted(set(item.get('type', 'N/A') for item in data.values()))
    type_filter = st.multiselect("Type", options=all_types, key="ar_type")

    # Filtre par métier (identique à prices.py)
    all_jobs = sorted(set(item.get('job') for item in data.values() if item.get('job')))
    job_filter = st.multiselect("Métier", options=all_jobs, key="ar_job")

    # Filtre par niveau
    max_level = max((item.get('level', 0) for item in data.values()), default=200)
    level_range = st.slider("Niveau", 1, max_level, (1, max_level), key="ar_level")

# --- Calcul des items éligibles basés sur le groupe ---
# Si un groupe est sélectionné, on prend :
# 1. Les ressources/consommables directement dans le groupe
# 2. Les ingrédients des équipements du groupe (récursivement)
eligible_item_ids = None  # None = pas de filtre groupe

if selected_group_filters:
    group_items = get_items_in_groups(selected_group_filters)

    eligible_ids = set()

    for item_id in group_items:
        item_id_str = str(item_id)
        if item_id_str in data:
            item = data[item_id_str]
            supertype = item.get('supertype', 'N/A')

            # Si c'est une ressource/consommable, l'ajouter directement
            if supertype in SUPERTYPES_HDV_TARGET:
                eligible_ids.add(item_id)

            # Si c'est un équipement craftable, extraire ses ingrédients
            if item.get('is_craft') and item.get('ingredients'):
                ingredients = get_all_ingredients_recursive(data, [item_id])
                # Filtrer pour ne garder que les ressources/consommables parmi les ingrédients
                for ing_id in ingredients:
                    ing_id_str = str(ing_id)
                    if ing_id_str in data:
                        ing_supertype = data[ing_id_str].get('supertype', 'N/A')
                        if ing_supertype in SUPERTYPES_HDV_TARGET:
                            eligible_ids.add(ing_id)

    eligible_item_ids = eligible_ids

    # Afficher les items éligibles après filtre groupe
    if eligible_ids:
        eligible_names = []
        for eid in eligible_ids:
            eid_str = str(eid)
            if eid_str in data:
                eligible_names.append(f"{data[eid_str].get('name')} (ID: {eid})")
        eligible_names.sort()
        st.info(f"📦 **{len(eligible_ids)} ressources/consommables éligibles :**\n" + ", ".join(eligible_names))
    else:
        st.warning("⚠️ Aucune ressource/consommable trouvée dans le(s) groupe(s) sélectionné(s)")

# --- Recherche des opportunités d'arbitrage ---
all_opportunities = []
items_analyzed = set()  # Pour compter les items uniques analysés

for item_id, item in data.items():
    # Filtrer uniquement les items des HDV Ressources et Consommables
    supertype = item.get('supertype', 'N/A')
    if supertype not in SUPERTYPES_HDV_TARGET:
        continue

    # Filtre groupe (prioritaire) : vérifier si l'item est éligible
    if eligible_item_ids is not None:
        if item.get('id') not in eligible_item_ids:
            continue

    # Appliquer les autres filtres
    if supertype_filter and supertype not in supertype_filter:
        continue

    if type_filter and item.get('type') not in type_filter:
        continue

    if job_filter and item.get('job') not in job_filter:
        continue

    level = item.get('level', 0)
    if level < level_range[0] or level > level_range[1]:
        continue

    if search_term:
        name_match = search_term.lower() in item.get('name', '').lower()
        id_match = search_term in str(item.get('id', ''))
        if not (name_match or id_match):
            continue

    # Compter cet item comme analysé
    items_analyzed.add(item.get('id'))

    # Extraire les prix
    prix_dict = get_latest_entry(item.get("prix_hdv", {})) or {}

    # Trouver les opportunités
    opportunities = find_arbitrage_opportunities(item, prix_dict, min_profit_pct, max_profit_pct)
    all_opportunities.extend(opportunities)

# Créer le DataFrame
df = pd.DataFrame(all_opportunities)

if len(df) > 0:
    # Trier par bénéfice % décroissant
    df_display = df.sort_values(by="benefice_pct", ascending=False).reset_index(drop=True)
else:
    df_display = df

# --- Boutons d'action ---
col_refresh, col_group_select, col_group_add, col_group_remove, col_scrapper, col_display = st.columns([0.5, 1.2, 0.6, 0.6, 0.8, 2.3])

with col_refresh:
    if st.button("🔄", help="Rafraîchir", key="ar_refresh"):
        st.cache_data.clear()
        st.rerun()

with col_group_select:
    if st.session_state.user_groups:
        group_options_action = {gid: gdata['name'] for gid, gdata in st.session_state.user_groups.items()}

        if 'selected_group_for_action_ar' not in st.session_state:
            st.session_state.selected_group_for_action_ar = list(group_options_action.keys())[0] if group_options_action else None

        selected_group_action = st.selectbox(
            "Groupe",
            options=list(group_options_action.keys()),
            format_func=lambda x: group_options_action[x],
            index=list(group_options_action.keys()).index(st.session_state.selected_group_for_action_ar) if st.session_state.selected_group_for_action_ar in group_options_action else 0,
            key="ar_group_action_select_widget",
            label_visibility="collapsed",
            on_change=lambda: st.session_state.update({'selected_group_for_action_ar': st.session_state.ar_group_action_select_widget})
        )
    else:
        selected_group_action = None
        st.info("Aucun groupe")

with col_group_add:
    if st.button("➕ Groupe", help="Ajouter au groupe", key="ar_add_group"):
        if st.session_state.selected_items_ar and selected_group_action:
            added_count = add_items_to_group(selected_group_action, list(st.session_state.selected_items_ar))
            if added_count > 0:
                st.toast(f"✓ {added_count} item(s) ajouté(s) au groupe", icon="✅")
            else:
                st.toast("⚠️ Item(s) déjà dans le groupe", icon="ℹ️")
        elif not st.session_state.selected_items_ar:
            st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
        else:
            st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

with col_group_remove:
    if st.button("➖ Groupe", help="Retirer du groupe", key="ar_remove_group"):
        if st.session_state.selected_items_ar and selected_group_action:
            removed_count = remove_items_from_group(selected_group_action, list(st.session_state.selected_items_ar))
            if removed_count > 0:
                st.toast(f"✓ {removed_count} item(s) retiré(s) du groupe", icon="✅")
            else:
                st.toast("⚠️ Aucun item à retirer du groupe", icon="ℹ️")
        elif not st.session_state.selected_items_ar:
            st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
        else:
            st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

with col_scrapper:
    if st.button("➕ Scrapper", help="Ajouter au scrapper", key="ar_add_scrapper"):
        if st.session_state.selected_items_ar:
            added_count = add_items_to_scrapper(list(st.session_state.selected_items_ar), data=data)
            if added_count > 0:
                st.toast(f"✓ {added_count} item(s) ajouté(s) au scrapper", icon="✅")
            else:
                st.toast("⚠️ Item(s) déjà présent dans le scrapper", icon="ℹ️")
        else:
            st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")

with col_display:
    st.markdown(f"<div style='padding-top: 10px;'><b>Opportunités : {len(df_display)}</b> | <b>Ingrédients éligibles : {len(items_analyzed)}</b></div>", unsafe_allow_html=True)

# --- Affichage du DataFrame ---
st.markdown("### 📋 Opportunités d'arbitrage")

if len(df_display) > 0:
    # Préparer le DataFrame pour affichage
    df_for_display = df_display.copy()

    # Ajouter la colonne image URL
    df_for_display["image"] = df_for_display["iconId"].apply(
        lambda x: f"https://api.dofusdb.fr/img/items/{x}.png"
    )

    # Formater les colonnes achat/revente avec quantité
    df_for_display["achat_display"] = df_for_display.apply(
        lambda row: f"{row['achat']} K ({row['qty_achat']} ×{row['nb_achats']})", axis=1
    )
    df_for_display["revente_display"] = df_for_display.apply(
        lambda row: f"{row['revente']} K ({row['qty_revente']} ×{row['nb_reventes']})", axis=1
    )

    # Sélectionner les colonnes pour l'affichage
    df_final = df_for_display[["id", "image", "name", "achat", "qty_achat", "revente", "qty_revente", "benefice", "benefice_pct"]].copy()
    df_final.columns = ["ID", "Image", "Nom", "Achat", "Qté Achat", "Revente", "Qté Revente", "Bénéfice", "Bénéfice %"]

    # Configuration des colonnes
    column_config = {
        "ID": st.column_config.NumberColumn("ID", width="small"),
        "Image": st.column_config.ImageColumn("Image", width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Achat": st.column_config.NumberColumn("Achat", format="%d K", width="small"),
        "Qté Achat": st.column_config.TextColumn("Qté Achat", width="small"),
        "Revente": st.column_config.NumberColumn("Revente", format="%d K", width="small"),
        "Qté Revente": st.column_config.TextColumn("Qté Revente", width="small"),
        "Bénéfice": st.column_config.NumberColumn("Bénéfice", format="%d K", width="small"),
        "Bénéfice %": st.column_config.NumberColumn("Bénéfice %", format="%.1f %%", width="small"),
    }

    # Affichage avec sélection
    event = st.dataframe(
        df_final,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        key="ar_dataframe"
    )

    # Mettre à jour les items sélectionnés
    if event.selection and event.selection.rows:
        selected_indices = event.selection.rows
        selected_ids = df_display.iloc[selected_indices]["id"].tolist()
        st.session_state.selected_items_ar = set(selected_ids)
    else:
        st.session_state.selected_items_ar = set()

    # Afficher le nombre d'items sélectionnés
    if st.session_state.selected_items_ar:
        st.info(f"🔹 {len(st.session_state.selected_items_ar)} item(s) sélectionné(s)")
else:
    st.info("Aucune opportunité d'arbitrage trouvée avec les filtres actuels.")

# --- Statistiques ---
st.markdown("---")

if len(df_display) > 0:
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Total opportunités", len(df_display))
    with col_stat2:
        unique_items = df_display["id"].nunique()
        st.metric("Items uniques", unique_items)
    with col_stat3:
        avg_profit = df_display["benefice_pct"].mean()
        st.metric("Rentabilité moyenne", f"{avg_profit:.1f}%")
    with col_stat4:
        max_profit = df_display["benefice"].max()
        st.metric("Meilleur bénéfice", f"{max_profit} K")
else:
    st.markdown("*Ajustez les filtres de rentabilité pour afficher des opportunités.*")
