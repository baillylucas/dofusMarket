import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from math import ceil
from googleDriveJSON import GoogleDriveJSON
from functools import lru_cache
from utils import (
    add_items_to_scrapper,
    get_user_groups, add_items_to_group, remove_items_from_group,
    get_items_in_groups
)


# Configuration
st.set_page_config(layout="wide")

st.markdown("# 🐾 XP Familiers")

st.sidebar.markdown("# ⚙️ Filtres")

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


@st.cache_data
def load_xp_data():
    """Charge les données XP depuis tous les fichiers du dossier data/xp_familiers/.

    Seuls les fichiers ayant les colonnes 'ID' et 'XP' sont lus.
    Retourne : (xp_dict, xp_sources)
    - xp_dict: {item_id: {source: xp_value}}
    - xp_sources: {item_id: [list_of_sources]}
    """
    try:
        xp_dir = Path('data/xp_familiers')
        if not xp_dir.exists():
            return {}, {}

        source_files = list(xp_dir.glob("*.csv")) + list(xp_dir.glob("*.xlsx")) + list(xp_dir.glob("*.xls"))

        xp_dict = {}
        xp_sources = {}

        for source_file in source_files:
            source = source_file.stem
            try:
                if source_file.suffix.lower() == ".csv":
                    df = pd.read_csv(source_file, delimiter=';')
                else:
                    df = pd.read_excel(source_file, sheet_name=0)

                if 'ID' not in df.columns or 'XP' not in df.columns:
                    continue

                df['XP'] = pd.to_numeric(df['XP'], errors='coerce')

                for _, row in df.iterrows():
                    id_val = row.get('ID')
                    xp_value = row['XP']

                    if pd.isna(id_val) or pd.isna(xp_value):
                        continue

                    try:
                        item_id = int(id_val)
                    except (ValueError, TypeError):
                        continue

                    if item_id not in xp_dict:
                        xp_dict[item_id] = {}
                        xp_sources[item_id] = []

                    xp_dict[item_id][source] = float(xp_value)
                    if source not in xp_sources[item_id]:
                        xp_sources[item_id].append(source)

            except Exception:
                continue

        return xp_dict, xp_sources
    except Exception as e:
        st.error(f"Erreur lors du chargement des XP : {e}")
        return {}, {}


@st.cache_data
def load_level_xp():
    """Charge la table XP cumulatif par niveau depuis data/level_xp.csv.

    Retourne un dict {level: cumulative_xp}.
    """
    try:
        path = Path('data/level_xp.csv')
        if not path.exists():
            return {}
        df = pd.read_csv(path, sep=';')
        return {int(row['x']): float(row['y']) for _, row in df.iterrows()}
    except Exception as e:
        st.error(f"Erreur lors du chargement de level_xp.csv : {e}")
        return {}


# --- Session State ---
if 'fam_craft_cache' not in st.session_state:
    st.session_state.fam_craft_cache = {}
if 'fam_last_quantity' not in st.session_state:
    st.session_state.fam_last_quantity = 1
if 'fam_allowed_hdv_qtys' not in st.session_state:
    st.session_state.fam_allowed_hdv_qtys = [1, 10, 100, 1000]
if 'fam_notification_shown' not in st.session_state:
    st.session_state.fam_notification_shown = False
if 'fam_user_groups' not in st.session_state:
    st.session_state.fam_user_groups = {}
if 'fam_quantity_mode' not in st.session_state:
    st.session_state.fam_quantity_mode = "Adaptée au niveau cible"
if 'fam_last_levels' not in st.session_state:
    st.session_state.fam_last_levels = (1, 100)


# --- Calcul des prix ---
def get_latest_entry(dico):
    if not dico:
        return None
    try:
        return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
    except Exception:
        return None


@lru_cache(maxsize=10000)
def calculate_optimal_price_cached(prices_tuple, target_quantity):
    """Greedy par prix unitaire : prend le lot le moins cher par unité en premier (max 25 par lot).
    Fallback sur le plus grand lot sans limite si un résidu persiste.
    Retourne (prix, fallback_used)."""
    if not prices_tuple:
        return None, False
    sorted_by_unit = sorted(prices_tuple, key=lambda x: x[1] / x[0])
    remaining = target_quantity
    total_cost = 0
    for qty, price in sorted_by_unit:
        if remaining <= 0:
            break
        count = min(25, remaining // qty)
        total_cost += count * price
        remaining -= count * qty
    fallback_used = False
    if remaining > 0:
        fallback_used = True
        max_lot = max(prices_tuple, key=lambda x: x[0])
        times = (remaining + max_lot[0] - 1) // max_lot[0]
        total_cost += times * max_lot[1]
    return int(round(total_cost)), fallback_used


def calculate_optimal_price(prices_dict, target_quantity, allowed_quantities=None):
    """Retourne (prix, fallback_used) ou (None, False)."""
    if not prices_dict:
        return None, False

    valid_prices = []
    for qty_str, price in prices_dict.items():
        if price is not None and price != -1:
            try:
                qty_int = int(qty_str)
                if allowed_quantities is not None and qty_int not in allowed_quantities:
                    continue
                price_float = float(price)
                if price_float > 0:
                    valid_prices.append((qty_int, price_float))
            except (ValueError, TypeError):
                continue

    if not valid_prices:
        return None, False

    prices_tuple = tuple(sorted(valid_prices))
    return calculate_optimal_price_cached(prices_tuple, target_quantity)


def calculate_craft_cost_recursive(data, item_id, quantity, memo=None, is_root=True):
    if memo is None:
        memo = st.session_state.fam_craft_cache

    cache_key = (str(item_id), quantity, is_root)
    if cache_key in memo:
        return memo[cache_key]

    item_id_str = str(item_id)
    if item_id_str not in data:
        memo[cache_key] = (None, None)
        return (None, None)

    item = data[item_id_str]

    prix_hdv_dict = get_latest_entry(item.get("prix_hdv", {})) or {}
    prix_hdv, _ = calculate_optimal_price(prix_hdv_dict, quantity)

    if not item.get('is_craft') or not item.get('ingredients'):
        result = (prix_hdv, 'HDV') if prix_hdv is not None else (None, None)
        memo[cache_key] = result
        return result

    craft_cost = 0
    for ingredient in item['ingredients']:
        ing_id = ingredient['id']
        total_ing_qty = ingredient['quantity'] * quantity
        ing_cost, _ = calculate_craft_cost_recursive(data, ing_id, total_ing_qty, memo, is_root=False)

        if ing_cost is None:
            craft_cost = None
            break

        craft_cost += ing_cost

    if craft_cost is None:
        result = (prix_hdv, 'HDV') if prix_hdv is not None else (None, None)
    elif prix_hdv is None:
        result = (craft_cost, 'Craft')
    else:
        if is_root:
            result = (craft_cost, 'Craft')
        else:
            result = (craft_cost, 'Craft') if craft_cost <= prix_hdv else (prix_hdv, 'HDV')

    memo[cache_key] = result
    return result


def precalculate_all_crafts(data, quantity):
    memo = st.session_state.fam_craft_cache
    for item_id in data.keys():
        calculate_craft_cost_recursive(data, item_id, quantity, memo, is_root=True)
        calculate_craft_cost_recursive(data, item_id, quantity, memo, is_root=False)


# --- PAGE ---
with st.spinner("Chargement des données depuis Google Drive..."):
    data = charger_donnees()

if not data:
    st.error("❌ Impossible de charger les données")
    st.stop()

st.session_state.fam_user_groups = get_user_groups()

xp_data, xp_sources = load_xp_data()
level_xp = load_level_xp()

if not st.session_state.fam_notification_shown:
    st.toast(f"✅ {len(data)} items chargés avec succès", icon="✅")
    st.session_state.fam_notification_shown = True

# --- Sidebar ---
with st.sidebar:
    # Niveaux familier
    st.markdown("### Niveau familier")
    col_cur, col_tgt = st.columns(2)
    with col_cur:
        pet_level_current = st.number_input("Actuel", min_value=1, max_value=100, value=1, step=1, key="fam_level_current")
    with col_tgt:
        pet_level_target = st.number_input("Souhaité", min_value=1, max_value=100, value=100, step=1, key="fam_level_target")

    if pet_level_target <= pet_level_current:
        st.warning("Le niveau souhaité doit être supérieur au niveau actuel.")

    # Mode de quantité
    quantity_mode = st.radio(
        "Mode quantité",
        ["Fixe", "Adaptée au niveau cible"],
        index=0 if st.session_state.fam_quantity_mode == "Fixe" else 1,
        horizontal=True,
        key="fam_quantity_mode_radio"
    )
    if quantity_mode != st.session_state.fam_quantity_mode:
        st.session_state.fam_quantity_mode = quantity_mode
        st.session_state.fam_craft_cache = {}

    # Quantité Achat/Craft (uniquement en mode Fixe)
    if quantity_mode == "Fixe":
        quantity = st.number_input(
            "Quantité Achat/Craft",
            min_value=1,
            max_value=999999,
            value=st.session_state.fam_last_quantity,
            step=1,
            key="fam_quantity"
        )
        if st.session_state.fam_last_quantity != quantity:
            st.session_state.fam_craft_cache = {}
            st.session_state.fam_last_quantity = quantity
    else:
        quantity = st.session_state.fam_last_quantity  # valeur de repli non utilisée

    # Quantités HDV autorisées
    allowed_hdv_qtys = st.multiselect(
        "Quantités HDV",
        options=[1, 10, 100, 1000],
        default=st.session_state.fam_allowed_hdv_qtys,
        format_func=lambda x: f"x{x}",
        key="fam_allowed_hdv_qtys_input"
    )
    if sorted(allowed_hdv_qtys) != sorted(st.session_state.fam_allowed_hdv_qtys):
        st.session_state.fam_allowed_hdv_qtys = allowed_hdv_qtys
    allowed_hdv_qtys_set = set(allowed_hdv_qtys) if allowed_hdv_qtys else None

    # Filtre par groupes
    group_options = {
        group_id: f"{group_data['name']} ({group_data['owner']})"
        for group_id, group_data in st.session_state.fam_user_groups.items()
    }
    selected_group_filters = st.multiselect(
        "Filtrer par groupe(s)",
        options=list(group_options.keys()),
        format_func=lambda x: group_options[x],
        key="fam_group_filter_multiselect"
    )

    search_term = st.text_input("🔍 Rechercher par nom ou ID", "", key="fam_search")

    craft_filter = st.radio("Type d'item", ["Tous", "Craftables uniquement", "Non craftables uniquement"], key="fam_craft_filter")

    all_sources = sorted(set(source for sources_list in xp_sources.values() for source in sources_list))
    default_xp_sources = ["pet_xp_dofusDB"] if "pet_xp_dofusDB" in all_sources else []
    xp_source_filter = st.multiselect("📊 Source XP", options=all_sources, default=default_xp_sources, key="fam_xp_source")

    xp_filter = st.radio("📚 XP", ["Tous", "XP connu uniquement", "XP inconnu uniquement"], index=1, key="fam_xp_filter")

    cout_familier = st.number_input("🐾 Coût familier", min_value=0, value=500000, step=100000, help="Valeur (K)", key="fam_cout_familier")
    revente = st.number_input("💰 Revente", min_value=0, value=5500000, step=100000, help="Valeur (K)", key="fam_revente")
    benefice_min = st.number_input("📈 Bénéfice min (%)", value=15, step=1, key="fam_benefice_min")

    max_item_level = max((item.get('level', 0) for item in data.values()), default=200)
    level_range = st.slider("Niveau item", 1, max_item_level, (1, max_item_level), key="fam_level_range")


# Invalider le cache si les niveaux ont changé en mode adaptatif
current_levels = (pet_level_current, pet_level_target)
if quantity_mode == "Adaptée au niveau cible" and st.session_state.fam_last_levels != current_levels:
    st.session_state.fam_craft_cache = {}
    st.session_state.fam_last_levels = current_levels

# Pré-calculer tous les crafts (uniquement en mode Fixe, car en mode adaptatif la quantité est différente par item)
if quantity_mode == "Fixe" and not st.session_state.fam_craft_cache:
    with st.spinner(f"Calcul des coûts de craft pour la quantité {quantity}..."):
        precalculate_all_crafts(data, quantity)

# --- Construction du DataFrame ---
rows = []
for item_id, item in data.items():
    # XP et unités nécessaires (calculés en premier pour déterminer effective_qty)
    item_int_id = item.get('id')
    xp_per_unit = None
    units_needed = None

    if item_int_id in xp_data:
        xp_sources_dict = xp_data[item_int_id]
        if xp_source_filter:
            xp_per_unit = next((v for s, v in xp_sources_dict.items() if s in xp_source_filter), None)
        else:
            xp_per_unit = next(iter(xp_sources_dict.values())) if xp_sources_dict else None

        if xp_per_unit is not None and xp_per_unit > 0:
            if (level_xp and pet_level_current in level_xp and pet_level_target in level_xp
                    and pet_level_target > pet_level_current):
                xp_needed_val = level_xp[pet_level_target] - level_xp[pet_level_current]
                if xp_needed_val > 0:
                    units_needed = ceil(xp_needed_val / xp_per_unit)

    # Quantité effective selon le mode
    if quantity_mode == "Adaptée au niveau cible" and units_needed is not None:
        effective_qty = units_needed
    else:
        effective_qty = quantity

    prix_hdv_dict = get_latest_entry(item.get("prix_hdv", {})) or {}
    prix_val, prix_fallback = calculate_optimal_price(prix_hdv_dict, effective_qty, allowed_hdv_qtys_set)

    is_craftable = bool(item.get('is_craft') and item.get('ingredients'))
    if is_craftable:
        craft_val, _ = calculate_craft_cost_recursive(data, item.get('id'), effective_qty, is_root=True)
    else:
        craft_val = None

    # Meilleur prix
    if prix_val is not None and craft_val is not None:
        best_price = min(prix_val, craft_val)
    elif prix_val is not None:
        best_price = prix_val
    elif craft_val is not None:
        best_price = craft_val
    else:
        best_price = None

    best_price_per_u = (best_price // effective_qty) if best_price is not None else None

    # XP avec la quantité effective
    xp_value = None
    xp_per_10kk = None
    if xp_per_unit is not None:
        if quantity_mode == "Adaptée au niveau cible":
            xp_value = xp_per_unit
        else:
            xp_value = xp_per_unit * effective_qty
        if best_price is not None and best_price > 0:
            xp_total = xp_per_unit * effective_qty
            xp_per_10kk = (xp_total / best_price) * 10000

    rows.append({
        "id": item.get("id"),
        "image": f"https://api.dofusdb.fr/img/items/{item.get('iconId', item.get('id'))}.png",
        "name": item.get("name"),
        "level": item.get("level"),
        "is_craft": is_craftable,
        "prix_hdv": prix_val,
        "fallback": "⚠️" if prix_fallback and prix_val == best_price else None,
        "cout_craft": craft_val,
        "meilleur_prix": best_price,
        "meilleur_prix_u": best_price_per_u,
        "benefice": round((revente - (best_price + cout_familier)) / (best_price + cout_familier) * 100, 1) if best_price and best_price > 0 else None,
        "prix_u_max": int((revente / (1 + benefice_min / 100) - cout_familier) / effective_qty) if effective_qty and benefice_min is not None else None,
        "xp": round(xp_value, 2) if xp_value is not None else None,
        "xp_per_10kk": round(xp_per_10kk, 1) if xp_per_10kk is not None else None,
        "units": units_needed,
        "effective_qty": effective_qty,
        "_has_xp": xp_per_unit is not None,
        "_item_id": item_id
    })

df = pd.DataFrame(rows)

# Forcer float64 pour éviter l'affichage "None" (dtype object) dans st.dataframe
for col in ["prix_hdv", "cout_craft", "meilleur_prix", "meilleur_prix_u", "xp", "xp_per_10kk", "units"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Filtres ---
if search_term:
    df = df[
        df["name"].str.contains(search_term, case=False, na=False) |
        df["id"].astype(str).str.contains(search_term)
    ]
if craft_filter == "Craftables uniquement":
    df = df[df["is_craft"] == True]
elif craft_filter == "Non craftables uniquement":
    df = df[df["is_craft"] != True]
if xp_filter == "XP connu uniquement":
    df = df[df["_has_xp"] == True]
elif xp_filter == "XP inconnu uniquement":
    df = df[df["_has_xp"] == False]
if selected_group_filters:
    group_items = get_items_in_groups(selected_group_filters)
    df = df[df["id"].isin(group_items)]
df = df[(df["level"] >= level_range[0]) & (df["level"] <= level_range[1])]
if benefice_min is not None:
    df = df[df["benefice"].notna() & (df["benefice"] >= benefice_min)]

df_display = df.reset_index(drop=True)


def _get_selected_ids(event, df):
    if event and hasattr(event, 'selection') and event.selection and event.selection.rows:
        return df.iloc[event.selection.rows]['id'].tolist()
    return []


tab_nourritures, tab_definitions = st.tabs(["🥩 Nourritures", "📖 Définition des indicateurs"])

with tab_definitions:
    st.markdown("""
### Prix HDV
Le prix HDV affiché est le **coût greedy** pour acquérir la quantité demandée en achetant sur l'Hôtel des Ventes.

Le HDV propose 4 tailles de lot : x1, x10, x100, x1000. L'algorithme trie les lots par **prix unitaire croissant** (moins cher par unité en premier), puis achète autant que possible de chaque lot (max 25 achats par taille de lot) :

1. Pour chaque taille de lot (du moins cher au plus cher par unité) : achète `min(25, restant // taille_lot)` fois
2. Si un résidu subsiste après tous les lots : **fallback** sur le plus grand lot disponible, sans limite d'achats

> Exemple pour 158 unités avec x1=1 096K, x10=10 994K, x100=325 000K :
> - Prix unitaires : x1=1 096, x10=1 099, x100=3 250 → ordre : x1 → x10 → x100
> - 25 × x1 = 25 unités, restant = 133
> - 13 × x10 = 130 unités, restant = 3
> - 3 × x1... déjà épuisé → fallback x100 × 1 = 325 000K
>
> *Note : l'algorithme greedy peut laisser un résidu si x1 est épuisé avant x10.*

---

### Coût Craft
Le coût craft est calculé **récursivement** sur l'arbre d'ingrédients.

Pour chaque ingrédient, la quantité totale nécessaire est `quantité_recette × quantité_demandée`. Son coût est ensuite résolu de deux façons :
- S'il est **non craftable** : prix HDV optimal (même algorithme que ci-dessus)
- S'il est **craftable** : comparaison craft vs HDV, on prend le **moins cher**

La quantité d'ingrédient est passée en bloc au calcul HDV — le greedy cherche donc le meilleur achat pour l'ensemble, ce qui favorise naturellement les gros lots (x1000 pour 20 000 unités = 20 achats).

> Exemple : crafter 5 000× A qui nécessite 4× B
> → `calculate_optimal_price(B, 20 000)` → 20 × x1000

---

### XP / 10kk
Ratio d'efficacité : **combien d'XP familier on obtient par 10 000 000 kamas dépensés**.

```
XP/10kk = (XP_par_unité × quantité) / meilleur_prix × 10 000
```

Plus ce chiffre est élevé, plus la nourriture est rentable en termes d'XP par kama investi.

---

### Unités nécessaires
Nombre d'unités à nourrir pour passer du **niveau actuel** au **niveau souhaité** (configurables dans la sidebar).

```
unités = ceil((XP_cumulatif_niveau_cible - XP_cumulatif_niveau_actuel) / XP_par_unité)
```

---

### Meill. Prix / Meill. Prix/u
**Meill. Prix** = `min(Prix HDV, Coût Craft)` — le moins cher des deux options pour acquérir la quantité demandée.

**Meill. Prix/u** = `Meill. Prix / quantité` — coût par unité individuelle (divisé par la quantité fixe saisie, indépendamment du mode adaptatif).

---

### ⚠️ Fallback HDV
Indique que le calcul du Prix HDV a dû recourir au **fallback** (achat d'un lot en excès) parce qu'un résidu non divisible par les tailles de lots disponibles subsistait après l'étape greedy.

Le ⚠️ n'est affiché que si c'est le **Prix HDV** (et non le Coût Craft) qui est retenu comme Meill. Prix — car dans le cas contraire le fallback n'impacte pas le prix affiché.

---

### Bénéfice
Marge bénéficiaire en % entre le prix de revente et le coût total d'acquisition (Meill. Prix + Coût familier).

```
Bénéfice (%) = (Revente - (Meill. Prix + Coût familier)) / (Meill. Prix + Coût familier) × 100
```

---

### Prix/u Max
Prix unitaire maximum qu'une ressource ne doit pas dépasser pour satisfaire le **Bénéfice min** configuré.

```
Prix/u Max = (Revente / (1 + Bénéfice_min / 100) - Coût familier) / quantité_effective
```

Si **Meill. Prix/u ≤ Prix/u Max**, la ressource satisfait le seuil de rentabilité.

---

### Revente & Coût familier
- **Revente** : prix de vente HDV du familier une fois nourri (en K). Paramétrable dans la sidebar.
- **Coût familier** : coût fixe additionnel à intégrer dans le calcul (achat du familier nu, taxes, etc.). S'ajoute à Meill. Prix dans le calcul du Bénéfice et du Prix/u Max.
""")

with tab_nourritures:
    # --- Boutons d'action ---
    if st.session_state.fam_user_groups:
        group_options_action = {gid: gdata['name'] for gid, gdata in st.session_state.fam_user_groups.items()}
        if 'fam_selected_group_for_action' not in st.session_state:
            st.session_state.fam_selected_group_for_action = list(group_options_action.keys())[0] if group_options_action else None
    else:
        group_options_action = {}

    col_refresh, col_group_select, col_group_add, col_group_remove, col_scrapper, col_display_count = st.columns(
        [0.4, 1.2, 0.6, 0.6, 0.8, 2.0]
    )

    with col_refresh:
        if st.button("🔄", help="Rafraîchir", key="fam_refresh"):
            st.cache_data.clear()
            st.session_state.fam_craft_cache = {}
            calculate_optimal_price_cached.cache_clear()
            st.rerun()

    with col_group_select:
        if group_options_action:
            selected_group_action = st.selectbox(
                "Groupe",
                options=list(group_options_action.keys()),
                format_func=lambda x: group_options_action[x],
                index=list(group_options_action.keys()).index(st.session_state.fam_selected_group_for_action)
                      if st.session_state.fam_selected_group_for_action in group_options_action else 0,
                key="fam_group_action_select_widget",
                label_visibility="collapsed",
                on_change=lambda: st.session_state.update(
                    {'fam_selected_group_for_action': st.session_state.fam_group_action_select_widget}
                )
            )
        else:
            selected_group_action = None
            st.info("Aucun groupe")

    with col_group_add:
        if st.button("➕ Groupe", help="Ajouter la sélection au groupe", key="fam_group_add"):
            event = st.session_state.get("fam_dataframe")
            selected_ids = _get_selected_ids(event, df_display)
            if selected_ids and selected_group_action:
                added = add_items_to_group(selected_group_action, selected_ids)
                st.toast(f"✓ {added} item(s) ajouté(s) au groupe" if added > 0 else "⚠️ Item(s) déjà dans le groupe", icon="✅" if added > 0 else "ℹ️")
            elif not selected_ids:
                st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
            else:
                st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

    with col_group_remove:
        if st.button("➖ Groupe", help="Retirer la sélection du groupe", key="fam_group_remove"):
            event = st.session_state.get("fam_dataframe")
            selected_ids = _get_selected_ids(event, df_display)
            if selected_ids and selected_group_action:
                removed = remove_items_from_group(selected_group_action, selected_ids)
                st.toast(f"✓ {removed} item(s) retiré(s)" if removed > 0 else "⚠️ Aucun item à retirer", icon="✅" if removed > 0 else "ℹ️")
            elif not selected_ids:
                st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")
            else:
                st.toast("⚠️ Sélectionnez un groupe", icon="⚠️")

    with col_scrapper:
        if st.button("➕ Scrapper", help="Ajouter la sélection au scrapper", key="fam_scrapper_add"):
            event = st.session_state.get("fam_dataframe")
            selected_ids = _get_selected_ids(event, df_display)
            if selected_ids:
                added = add_items_to_scrapper(selected_ids, data=data)
                st.toast(f"✓ {added} item(s) ajouté(s) au scrapper" if added > 0 else "⚠️ Item(s) déjà dans le scrapper", icon="✅" if added > 0 else "ℹ️")
            else:
                st.toast("⚠️ Sélectionnez des items d'abord", icon="⚠️")

    with col_display_count:
        st.markdown(f"<div style='padding-top: 10px;'><b>Affichage : {len(df_display)} / {len(data)} items</b></div>", unsafe_allow_html=True)

    # --- Tableau ---
    cols_to_show = ["id", "image", "name", "level", "prix_hdv", "fallback", "cout_craft", "meilleur_prix", "meilleur_prix_u", "benefice", "prix_u_max", "xp", "xp_per_10kk", "units"]
    df_table = df_display[cols_to_show].copy()

    event = st.dataframe(
        df_table,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "image": st.column_config.ImageColumn("Image", width="small"),
            "name": st.column_config.TextColumn("Ressource", width="large"),
            "level": st.column_config.NumberColumn("Niveau", width="small"),
            "prix_hdv": st.column_config.NumberColumn("Prix HDV", width="small", format="%d K"),
            "fallback": st.column_config.TextColumn("", width="small", help="⚠️ Le prix HDV inclut un lot en excès (résidu non divisible par les tailles disponibles)"),
            "cout_craft": st.column_config.NumberColumn("Coût Craft", width="small", format="%d K"),
            "meilleur_prix": st.column_config.NumberColumn("Meill. Prix", width="small", format="%d K"),
            "meilleur_prix_u": st.column_config.NumberColumn("Meill. Prix/u", width="small", format="%d K"),
            "benefice": st.column_config.NumberColumn("Bénéfice", width="small", format="%.1f%%"),
            "prix_u_max": st.column_config.NumberColumn("Prix/u Max", width="small", format="%d K"),
            "xp": st.column_config.NumberColumn("XP/u" if quantity_mode == "Adaptée au niveau cible" else "XP", width="small", format="%.2f"),
            "xp_per_10kk": st.column_config.NumberColumn("XP/10kk", width="small", format="%.1f"),
            "units": st.column_config.NumberColumn("Unités", width="small", format="%d"),
        },
        hide_index=True,
        use_container_width=True,
        selection_mode="multi-row",
        on_select="rerun",
        key="fam_dataframe"
    )


# --- Panneau de détails (1 ligne sélectionnée) ---
selected_rows = event.selection.rows if event and event.selection else []
if len(selected_rows) == 1:
    selected_row = df_display.iloc[selected_rows[0]]
    selected_item_id = str(selected_row["_item_id"])
    item = data.get(selected_item_id, {})

    st.markdown(f"### {item.get('id', '')} {item.get('name', '')} — Détails")

    tab_resume, tab_ingredients, tab_historique, tab_graph = st.tabs(["📋 Résumé", "🧪 Ingrédients", "📊 Historique des prix", "📈 Évolution des prix"])

    with tab_resume:
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        with col_i1:
            st.metric("ID", item.get("id", "-"))
        with col_i2:
            st.metric("Niveau", item.get("level", "-"))
        with col_i3:
            st.metric("Craftable", "Oui" if item.get("is_craft") else "Non")
        with col_i4:
            last_maj = item.get("last_maj", "N/A")
            if last_maj != "N/A":
                try:
                    last_maj = datetime.fromisoformat(last_maj).strftime("%d/%m/%Y %H:%M")
                except Exception:
                    pass
            st.metric("Dernière MAJ", last_maj)

    with tab_ingredients:
        if item.get("is_craft") and item.get("ingredients"):
            detail_qty = int(selected_row["effective_qty"]) if not pd.isna(selected_row.get("effective_qty", float('nan'))) else quantity
            recipe_rows = []
            for ing in item["ingredients"]:
                ing_id = ing["id"]
                ing_qty_total = ing["quantity"] * detail_qty
                ing_id_str = str(ing_id)
                ing_name = data[ing_id_str].get("name", f"Item #{ing_id}") if ing_id_str in data else f"Item #{ing_id}"
                cost, method = calculate_craft_cost_recursive(data, ing_id, ing_qty_total, None, is_root=False)
                unit_cost = int(round(cost / ing_qty_total)) if cost is not None and ing_qty_total > 0 else None
                recipe_rows.append({
                    "Ingrédient": ing_name,
                    "ID": ing_id,
                    "Quantité": ing_qty_total,
                    "Prix/u (K)": unit_cost,
                    "Total (K)": cost,
                    "Méthode": method or "-",
                })
            st.dataframe(
                pd.DataFrame(recipe_rows),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Prix/u (K)": st.column_config.NumberColumn(format="%d K"),
                    "Total (K)": st.column_config.NumberColumn(format="%d K"),
                }
            )
        else:
            st.info("Cet item n'est pas craftable.")

    with tab_historique:
        prix_dict = item.get("prix_hdv", {})
        if prix_dict:
            def extract_price(prices, qty_str):
                try:
                    v = prices.get(qty_str)
                    if v is None:
                        return None
                    fv = float(v)
                    return int(fv) if fv > 0 else None
                except (TypeError, ValueError):
                    return None

            def has_any_price(prices):
                return any(extract_price(prices, q) is not None for q in ["1", "10", "100", "1000"])

            try:
                all_dates = sorted(prix_dict.keys(), key=lambda k: datetime.fromisoformat(k), reverse=True)
            except Exception:
                all_dates = sorted(prix_dict.keys(), reverse=True)

            sorted_dates = [d for d in all_dates if has_any_price(prix_dict[d])][:5]

            hist_rows = []
            for date in sorted_dates:
                prices_for_date = prix_dict[date]
                try:
                    date_fmt = datetime.fromisoformat(date).strftime("%d/%m/%Y %H:%M")
                except Exception:
                    date_fmt = date
                p1    = extract_price(prices_for_date, "1")
                p10   = extract_price(prices_for_date, "10")
                p100  = extract_price(prices_for_date, "100")
                p1000 = extract_price(prices_for_date, "1000")
                hist_rows.append({
                    "Date": date_fmt,
                    "x1 (K)": p1,
                    "x10 (K)": p10,
                    "x100 (K)": p100,
                    "x1000 (K)": p1000,
                })
            if hist_rows:
                st.dataframe(
                    pd.DataFrame(hist_rows),
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "x1 (K)": st.column_config.NumberColumn(format="%d K"),
                        "x10 (K)": st.column_config.NumberColumn(format="%d K"),
                        "x100 (K)": st.column_config.NumberColumn(format="%d K"),
                        "x1000 (K)": st.column_config.NumberColumn(format="%d K"),
                    }
                )
        else:
            st.info("Aucun historique de prix disponible.")

    with tab_graph:
        import altair as alt
        prix_dict_graph = item.get("prix_hdv", {})
        if prix_dict_graph:
            graph_rows = []
            for date_str, prices in prix_dict_graph.items():
                try:
                    date_parsed = datetime.fromisoformat(date_str)
                except Exception:
                    continue
                for qty_label, qty_key, divisor in [("x1", "1", 1), ("x10", "10", 10), ("x100", "100", 100), ("x1000", "1000", 1000)]:
                    try:
                        v = prices.get(qty_key)
                        if v is not None and float(v) > 0:
                            graph_rows.append({
                                "Date": date_parsed,
                                "Quantité": qty_label,
                                "Prix bundle (K)": float(v),
                                "Prix unitaire (K)": float(v) / divisor,
                            })
                    except (TypeError, ValueError):
                        pass

            if graph_rows:
                df_graph = pd.DataFrame(graph_rows).sort_values("Date")
                all_qty_labels = ["x1", "x10", "x100", "x1000"]

                zoom_choice = st.radio(
                    "Axe du zoom (molette)",
                    ["Les deux", "Temps (X)", "Prix (Y)"],
                    horizontal=True,
                    key=f"fam_graph_zoom_{selected_item_id}",
                )
                zoom_encodings = {"Les deux": ["x", "y"], "Temps (X)": ["x"], "Prix (Y)": ["y"]}[zoom_choice]

                legend_selection = alt.selection_point(fields=["Quantité"], bind="legend", empty=True)
                zoom_selection = alt.selection_interval(bind="scales", encodings=zoom_encodings)

                chart = (
                    alt.Chart(df_graph)
                    .mark_line(point=alt.OverlayMarkDef(filled=True, size=80))
                    .encode(
                        x=alt.X("Date:T", title="Date"),
                        y=alt.Y("Prix unitaire (K):Q", title="Prix unitaire (K)"),
                        color=alt.Color("Quantité:N", scale=alt.Scale(
                            domain=all_qty_labels,
                            range=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
                        )),
                        opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.1)),
                        tooltip=[
                            alt.Tooltip("Date:T", title="Date", format="%d/%m/%Y %H:%M"),
                            alt.Tooltip("Prix bundle (K):Q", title="Prix bundle (K)", format=".0f"),
                            alt.Tooltip("Prix unitaire (K):Q", title="Prix unitaire (K)", format=".0f"),
                        ],
                    )
                    .add_params(legend_selection, zoom_selection)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Aucune donnée de prix valide pour le graphique.")
        else:
            st.info("Aucun historique de prix disponible.")


# --- Statistiques ---
st.markdown("---")
xp_known_count = df["_has_xp"].sum() if not df.empty else 0
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("Items affichés", len(df_display))
with col_stat2:
    st.metric("Items avec XP connu", int(xp_known_count))
with col_stat3:
    st.metric("Sources XP disponibles", len(all_sources))
