import streamlit as st
import pandas as pd
from datetime import datetime
from googleDriveJSON import GoogleDriveJSON

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Objets Dofus - Liste", layout="wide")

FILE_ID = "1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu"

@st.cache_data(ttl=600)
def charger_donnees():
    drive = GoogleDriveJSON(FILE_ID)
    data = drive.read()
    # garder uniquement les clés numériques
    data = {k: v for k, v in data.items() if str(k).isdigit()}
    return data

def get_latest_entry(dico):
    if not dico:
        return None
    try:
        return dico[max(dico.keys(), key=lambda k: datetime.fromisoformat(k))]
    except Exception:
        return None

# --- CHARGEMENT DES DONNÉES ---
data = charger_donnees()

# --- TRANSFORMATION EN DATAFRAME ---
rows = []
for item in data.values():
    prix = get_latest_entry(item.get("prix_hdv", {})) or {}
    craft = get_latest_entry(item.get("cout_craft", {})) or {}
    rows.append({
        "ID": item.get("id"),
        "Nom": item.get("name"),
        "Niveau": item.get("level"),
        "Prix 1x": prix.get("1"),
        "Prix 10x": prix.get("10"),
        "Prix 100x": prix.get("100"),
        "Coût 1x": craft.get("1"),
        "Coût 10x": craft.get("10"),
        "Type": item.get("type"),
    })

df = pd.DataFrame(rows)

# --- BARRE DE RECHERCHE & TRI ---
st.sidebar.header("🔎 Recherche et tri")

recherche = st.sidebar.text_input("Rechercher un objet (nom ou ID)")
col_tri = st.sidebar.selectbox("Trier par colonne", df.columns, index=1)
ordre = st.sidebar.radio("Ordre", ["⬆️ Croissant", "⬇️ Décroissant"], horizontal=True)

if recherche:
    df = df[df["Nom"].str.contains(recherche, case=False, na=False) |
            df["ID"].astype(str).str.contains(recherche)]

asc = True if ordre == "⬆️ Croissant" else False
df = df.sort_values(by=col_tri, ascending=asc)

# --- PAGINATION ---
page_size = st.sidebar.number_input("Résultats par page", 5, 50, 15)
nb_pages = (len(df) - 1) // page_size + 1
page_actuelle = st.sidebar.number_input("Page", 1, nb_pages, 1)
start, end = (page_actuelle - 1) * page_size, page_actuelle * page_size

st.write(f"### Page {page_actuelle}/{nb_pages} — {len(df)} objets au total")

# --- AFFICHAGE PRINCIPAL ---
st.dataframe(
    df.iloc[start:end].reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

# AFFICHAGE TEST
st.dataframe(
    df,
    use_container_width=True,
    hide_index=False
)

# --- CLIQUER POUR VOIR LES DÉTAILS ---
st.markdown("### 🔍 Détails d'un objet")
id_select = st.text_input("Entrer l'ID de l'objet à afficher :")

if id_select and id_select in data:
    item = data[id_select]
    st.subheader(f"{item['name']} (Niveau {item['level']})")
    st.write(f"Type : **{item['type']}** — Supertype : **{item['supertype']}**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Historique HDV")
        if item["prix_hdv"]:
            st.json(item["prix_hdv"])
        else:
            st.info("Aucun prix enregistré.")

    with col2:
        st.markdown("#### ⚒️ Historique Craft")
        if item["cout_craft"]:
            st.json(item["cout_craft"])
        else:
            st.info("Aucun coût de craft disponible.")

    st.markdown("#### 🧩 Ingrédients")
    if item.get("ingredients"):
        for ing in item["ingredients"]:
            st.write(f"- ID {ing['id']} × {ing['quantity']}")
    else:
        st.write("Non craftable.")
else:
    st.info("Saisis un ID d'objet pour afficher les détails.")
