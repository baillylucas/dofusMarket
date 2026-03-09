"""
Page Bashing — Visualisation des données de farming par zone/race
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from googleDriveJSON import GoogleDriveJSON

st.set_page_config(layout="wide")
st.markdown("# ⚔️ Bashing")
st.sidebar.markdown("# ⚙️ Filtres")

DATA_DIR = Path("data")
FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"
SERVICE_ACCOUNT_FILE = "credentials/service_account.json"


# ─── Chargement ──────────────────────────────────────────────────────────────

@st.cache_data
def load_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=600)
def load_item_data():
    try:
        drive = GoogleDriveJSON(FILE_ID, SERVICE_ACCOUNT_FILE)
        return drive.read()
    except Exception as e:
        st.error(f"Erreur chargement Google Drive : {e}")
        return {}


def get_latest_price(prix_hdv: dict) -> float | None:
    """Retourne le prix unitaire (x1) de la dernière entrée prix_hdv."""
    if not prix_hdv:
        return None
    latest_key = max(prix_hdv.keys())
    prices = prix_hdv.get(latest_key) or {}
    for qty in ["1", "10", "100", "1000"]:
        val = prices.get(qty)
        if val not in (None, -1):
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    return None


# ─── Construction du tableau principal ───────────────────────────────────────

@st.cache_data(ttl=600)
def build_main_table(monsters_raw, races, subareas, areas, super_areas, items_raw):
    """Construit une ligne par (subarea_id, race_id) avec les colonnes agrégées."""
    item_prices = {iid: get_latest_price(item.get("prix_hdv", {})) for iid, item in items_raw.items()}

    # Grouper les monstres par (subarea_id, race_id)
    groups: dict[tuple, list] = {}
    for monster in monsters_raw.values():
        race_id = monster.get("raceId")
        if race_id is None:
            continue
        for sub_id in monster.get("subAreaIds", []):
            groups.setdefault((sub_id, race_id), []).append(monster)

    rows = []
    for (sub_id, race_id), group_monsters in groups.items():
        subarea = subareas.get(str(sub_id), {})
        area_id = subarea.get("areaId")
        area = areas.get(str(area_id), {}) if area_id is not None else {}
        super_area_id = area.get("superAreaId")
        super_area_name = super_areas.get(str(super_area_id), "") if super_area_id is not None else ""

        levels = [m["level"] for m in group_monsters if m.get("level") is not None]
        niveau_moyen = round(sum(levels) / len(levels)) if levels else None

        drop_moyen = 0.0
        has_price = False
        for monster in group_monsters:
            for drop in monster.get("drops", []):
                price = item_prices.get(str(drop["id"]))
                if price is not None:
                    has_price = True
                    drop_moyen += price * drop.get("avgRate", 0) / 100

        rows.append({
            "_sub_id": sub_id,
            "_race_id": race_id,
            "Monde": super_area_name,
            "Région": area.get("name", ""),
            "Territoire": subarea.get("name", ""),
            "Race": races.get(str(race_id), f"Race {race_id}"),
            "Niveau moyen": niveau_moyen,
            "Drop moyen (K)": round(drop_moyen) if has_price else None,
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["Niveau moyen"] = pd.to_numeric(df["Niveau moyen"], errors="coerce")
    df["Drop moyen (K)"] = pd.to_numeric(df["Drop moyen (K)"], errors="coerce")
    return df.sort_values("Drop moyen (K)", ascending=False, na_position="last").reset_index(drop=True)


# ─── Détail d'un monstre ─────────────────────────────────────────────────────

def render_monster_table(monster: dict, items_raw: dict):
    name = monster.get("name") or f"Monstre #{monster['id']}"
    gfx_id = monster.get("gfxId")

    col_img, col_name = st.columns([1, 10])
    with col_img:
        if gfx_id:
            st.image(f"https://api.dofusdb.fr/img/monsters/{gfx_id}.png", width=64)
    with col_name:
        st.markdown(f"#### {name}")

    drops = monster.get("drops", [])
    if not drops:
        st.caption("Aucun drop connu.")
        st.divider()
        return

    rows = []
    for drop in drops:
        iid = str(drop["id"])
        item = items_raw.get(iid, {})
        icon_id = item.get("iconId", drop["id"])
        price = get_latest_price(item.get("prix_hdv", {}))
        rate = drop.get("avgRate", 0)
        weighted = round(price * rate / 100) if price is not None else None
        rows.append({
            "img": f"https://api.dofusdb.fr/img/items/{icon_id}.png",
            "ID": drop["id"],
            "Ressource": item.get("name", f"Item #{drop['id']}"),
            "Taux (%)": rate,
            "Prix (K)": round(price) if price is not None else None,
            "Prix pondéré (K)": weighted,
        })

    df = pd.DataFrame(rows)
    total_pondere = df["Prix pondéré (K)"].sum(skipna=True)
    total_prix = df["Prix (K)"].sum(skipna=True)
    total_row = pd.DataFrame([{
        "img": "",
        "ID": None,
        "Ressource": "TOTAL",
        "Taux (%)": None,
        "Prix (K)": round(total_prix),
        "Prix pondéré (K)": round(total_pondere),
    }])
    df = pd.concat([df, total_row], ignore_index=True)

    st.dataframe(
        df,
        column_config={
            "img": st.column_config.ImageColumn("", width="small"),
            "ID": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "Ressource": st.column_config.TextColumn("Ressource", width="large"),
            "Taux (%)": st.column_config.NumberColumn("Taux (%)", format="%.2f", width="small"),
            "Prix (K)": st.column_config.NumberColumn("Prix (K)", format="%d K", width="small"),
            "Prix pondéré (K)": st.column_config.NumberColumn("Prix pondéré (K)", format="%d K", width="medium"),
        },
        hide_index=True,
        use_container_width=True,
    )
    st.divider()


def render_detail(sub_id: int, race_id: int, monsters_raw: dict, items_raw: dict, subareas: dict, races: dict):
    subarea_name = subareas.get(str(sub_id), {}).get("name", f"Zone {sub_id}")
    race_name = races.get(str(race_id), f"Race {race_id}")
    st.markdown(f"## {subarea_name} — {race_name}")

    group_monsters = [
        m for m in monsters_raw.values()
        if m.get("raceId") == race_id and sub_id in m.get("subAreaIds", [])
    ]

    if not group_monsters:
        st.info("Aucun monstre trouvé pour ce groupe.")
        return

    item_prices = {iid: get_latest_price(item.get("prix_hdv", {})) for iid, item in items_raw.items()}
    total_drop = 0.0
    for monster in group_monsters:
        for drop in monster.get("drops", []):
            price = item_prices.get(str(drop["id"]))
            if price is not None:
                total_drop += price * drop.get("avgRate", 0) / 100
    st.markdown(f"**Drop moyen total : {round(total_drop):,} K**".replace(",", " "))

    (tab_territoire,) = st.tabs(["🗺️ Territoire"])
    with tab_territoire:
        for monster in group_monsters:
            render_monster_table(monster, items_raw)


# ─── Chargement ──────────────────────────────────────────────────────────────

with st.spinner("Chargement des données..."):
    monsters_raw = load_json("monsters.json")
    races = load_json("races.json")
    subareas = load_json("subareas.json")
    areas = load_json("areas.json")
    super_areas = load_json("super_areas.json")
    items_raw = load_item_data()

if not monsters_raw:
    st.error("❌ Données monstres introuvables. Lancez d'abord : `python scrapper/2_download_monsters.py`")
    st.stop()

# ─── Tableau principal ────────────────────────────────────────────────────────

df = build_main_table(monsters_raw, races, subareas, areas, super_areas, items_raw)

if df.empty:
    st.info("Aucune donnée à afficher.")
    st.stop()

# ─── Filtres sidebar ──────────────────────────────────────────────────────────

with st.sidebar:
    selected_mondes = st.multiselect(
        "Monde", options=sorted(df["Monde"].dropna().unique()), key="bash_monde"
    )
    selected_regions = st.multiselect(
        "Région", options=sorted(df["Région"].dropna().unique()), key="bash_region"
    )
    selected_races = st.multiselect(
        "Race", options=sorted(df["Race"].dropna().unique()), key="bash_race"
    )
    search = st.text_input("🔍 Territoire / Race", "", key="bash_search")

    level_vals = df["Niveau moyen"].dropna()
    lv_min, lv_max = int(level_vals.min()) if not level_vals.empty else 1, int(level_vals.max()) if not level_vals.empty else 200
    if lv_min < lv_max:
        level_range = st.slider("Niveau moyen", lv_min, lv_max, (lv_min, lv_max), key="bash_level")
    else:
        level_range = (lv_min, lv_max)

    only_with_prices = st.checkbox("Uniquement avec drop moyen > 0", value=True, key="bash_prices")

# ─── Application des filtres ──────────────────────────────────────────────────

df_filtered = df.copy()
if selected_mondes:
    df_filtered = df_filtered[df_filtered["Monde"].isin(selected_mondes)]
if selected_regions:
    df_filtered = df_filtered[df_filtered["Région"].isin(selected_regions)]
if selected_races:
    df_filtered = df_filtered[df_filtered["Race"].isin(selected_races)]
if search:
    mask = (
        df_filtered["Territoire"].str.contains(search, case=False, na=False)
        | df_filtered["Race"].str.contains(search, case=False, na=False)
    )
    df_filtered = df_filtered[mask]
if only_with_prices:
    df_filtered = df_filtered[df_filtered["Drop moyen (K)"].notna() & (df_filtered["Drop moyen (K)"] > 0)]
df_filtered = df_filtered[
    df_filtered["Niveau moyen"].isna()
    | ((df_filtered["Niveau moyen"] >= level_range[0]) & (df_filtered["Niveau moyen"] <= level_range[1]))
]

df_display = df_filtered.reset_index(drop=True)
DISPLAY_COLS = ["Monde", "Région", "Territoire", "Race", "Niveau moyen", "Drop moyen (K)"]

st.markdown(f"**{len(df_display)} combinaisons zone / race**")

event = st.dataframe(
    df_display[DISPLAY_COLS],
    column_config={
        "Monde": st.column_config.TextColumn("Monde", width="medium"),
        "Région": st.column_config.TextColumn("Région", width="medium"),
        "Territoire": st.column_config.TextColumn("Territoire", width="medium"),
        "Race": st.column_config.TextColumn("Race", width="medium"),
        "Niveau moyen": st.column_config.NumberColumn("Niveau moyen", format="%d", width="small"),
        "Drop moyen (K)": st.column_config.NumberColumn("Drop moyen (K)", format="%d K", width="medium"),
    },
    hide_index=True,
    use_container_width=True,
    selection_mode="single-row",
    on_select="rerun",
    key="bashing_dataframe",
)

# ─── Détail on-select ────────────────────────────────────────────────────────

if event.selection and event.selection.rows:
    idx = event.selection.rows[0]
    row = df_display.iloc[idx]
    st.divider()
    render_detail(int(row["_sub_id"]), int(row["_race_id"]), monsters_raw, items_raw, subareas, races)
