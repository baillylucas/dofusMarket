"""
Met à jour le fichier data/items_xp.csv avec les données XP familier
provenant du fichier Excel "data/Excel Familier Discord.xlsx".

- Si l'item existe déjà dans items_xp.csv (correspondance par libellé), met à jour xp_1.
- Si l'item n'existe pas, récupère son ID via l'API dofusdb et l'ajoute.
"""

import pandas as pd
import requests
import re
import unicodedata
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
ITEMS_XP_PATH = DATA_DIR / "items_xp.csv"
EXCEL_PATH = DATA_DIR / "Excel Familier Discord.xlsx"
DOFUSDB_API = "https://api.dofusdb.fr/items"


def strip_accents(text: str) -> str:
    """Retire les accents et normalise les ligatures (Œ->oe, Æ->ae)."""
    text = text.replace("\u0152", "Oe").replace("\u0153", "oe")  # Œ, œ
    text = text.replace("\u00c6", "Ae").replace("\u00e6", "ae")  # Æ, æ
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def normalize(text: str) -> str:
    """Normalise un texte pour comparaison insensible aux accents et à la casse."""
    return strip_accents(text).strip().lower()


def search_item_id(name: str) -> tuple[int, str] | None:
    """
    Recherche l'ID d'un item par son nom via l'API dofusdb.
    Tente d'abord une recherche exacte, puis un fallback par regex sur un mot-clé.
    Retourne (id, nom_officiel) ou None.
    """
    norm_name = normalize(name)

    # 1) Recherche exacte
    try:
        resp = requests.get(DOFUSDB_API, params={"name.fr": name, "$limit": 5}, timeout=10)
        resp.raise_for_status()
        for item in resp.json().get("data", []):
            if normalize(item["name"]["fr"]) == norm_name:
                return item["id"], item["name"]["fr"]
    except Exception:
        pass

    # 2) Fallback : recherche par regex sur le dernier mot significatif
    # Extraire un mot-clé distinctif (>= 4 chars, en fin de nom, pas un mot courant)
    words = re.findall(r"[A-Za-zÀ-ÿŒœ]+", name)
    stop_words = {"de", "du", "des", "le", "la", "les", "en", "un", "une", "et", "d"}
    keywords = [w for w in words if len(w) >= 4 and w.lower() not in stop_words]
    if not keywords:
        keywords = [w for w in words if w.lower() not in stop_words]

    for keyword in reversed(keywords):
        try:
            resp = requests.get(
                DOFUSDB_API,
                params={"name.fr[$regex]": keyword, "$limit": 50},
                timeout=10,
            )
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                if normalize(item["name"]["fr"]) == norm_name:
                    return item["id"], item["name"]["fr"]
        except Exception:
            continue

    return None


def main():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    default_date = "2025-01-01 00:00"

    # 1. Lire le fichier Excel
    df_excel = pd.read_excel(EXCEL_PATH, sheet_name=0)
    print(f"Excel : {len(df_excel)} items lus")

    # 2. Lire le CSV existant
    df_csv = pd.read_csv(ITEMS_XP_PATH, delimiter=";")
    print(f"CSV   : {len(df_csv)} items existants")

    # Ajouter la colonne last_update si absente, avec la date par défaut
    if "last_update" not in df_csv.columns:
        df_csv["last_update"] = default_date

    # Index normalisé libelle -> index ligne dans le CSV
    csv_norm_to_idx = {}
    for idx, row in df_csv.iterrows():
        csv_norm_to_idx[normalize(str(row["libelle"]))] = idx

    updated = 0
    added = 0
    not_found = []

    for _, row in df_excel.iterrows():
        name = str(row["Ressources"])
        xp = row["XP"]
        norm_name = normalize(name)

        if norm_name in csv_norm_to_idx:
            # Item existe : mettre à jour xp_1
            csv_idx = csv_norm_to_idx[norm_name]
            old_xp = df_csv.at[csv_idx, "xp_1"]
            df_csv.at[csv_idx, "xp_1"] = xp
            df_csv.at[csv_idx, "last_update"] = today
            updated += 1
            if pd.notna(old_xp) and old_xp != xp:
                print(f"  MAJ  '{name}': xp_1 {old_xp} -> {xp}")
        else:
            # Item absent : chercher l'ID via l'API
            print(f"  NEW  '{name}' -> recherche API...", end=" ")
            result = search_item_id(name)
            if result is not None:
                item_id, official_name = result
                new_row = pd.DataFrame([{
                    "id": item_id,
                    "libelle": official_name,
                    "xp_1": xp,
                    "xp_2": "",
                    "last_update": today,
                }])
                df_csv = pd.concat([df_csv, new_row], ignore_index=True)
                csv_norm_to_idx[norm_name] = len(df_csv) - 1
                added += 1
                print(f"ID={item_id} '{official_name}'")
            else:
                not_found.append(name)
                print("NON TROUVÉ")

    # 3. Sauvegarder le CSV
    df_csv.to_csv(ITEMS_XP_PATH, sep=";", index=False)

    print(f"\nRésultat :")
    print(f"  {updated} items mis à jour")
    print(f"  {added} items ajoutés")
    if not_found:
        print(f"  {len(not_found)} items non trouvés sur l'API :")
        for name in not_found:
            print(f"    - {name}")


if __name__ == "__main__":
    main()
