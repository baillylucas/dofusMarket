"""
Met à jour le fichier data/items_xp.csv avec les données XP familier
provenant de tous les fichiers CSV/XLSX du dossier data/xp_familiers/.

Structure du fichier de sortie :
- id : ID de l'item
- libelle : Nom de l'item
- xp : Valeur XP
- source : Nom du fichier source (sans extension)

Structure des fichiers sources (CSV ou XLSX) :
- Ressources : Nom de l'item (obligatoire)
- XP : Valeur XP (obligatoire)
- ID : ID de l'item (optionnel, sinon recherche via API)
"""

import pandas as pd
import requests
import re
import unicodedata
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
XP_FAMILIERS_DIR = DATA_DIR / "xp_familiers"
ITEMS_XP_PATH = DATA_DIR / "items_xp.csv"
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


def write_ids_to_source(file_path: Path, ids_to_write: dict[str, int], df_source: pd.DataFrame):
    """
    Écrit les IDs trouvés via l'API dans le fichier source.
    ids_to_write : {nom_ressource: item_id}
    Crée la colonne ID si elle n'existe pas.
    """
    if not ids_to_write:
        return

    suffix = file_path.suffix.lower()

    try:
        # Ajouter la colonne ID si elle n'existe pas
        if "ID" not in df_source.columns:
            df_source["ID"] = pd.NA

        # Mettre à jour chaque ID
        for name, item_id in ids_to_write.items():
            mask = df_source["Ressources"].astype(str).str.strip() == name
            if mask.any():
                df_source.loc[mask, "ID"] = item_id

        # Réécrire le fichier source
        if suffix == ".csv":
            # Détecter l'encodage d'origine pour réécrire dans le même format
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            write_encoding = 'utf-8'
            for encoding in encodings:
                try:
                    file_path.read_text(encoding=encoding)
                    write_encoding = encoding
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue

            df_source.to_csv(file_path, sep=";", index=False, encoding=write_encoding)
        elif suffix in [".xlsx", ".xls"]:
            df_source.to_excel(file_path, index=False)

        print(f"  💾 {len(ids_to_write)} ID(s) écrits dans '{file_path.name}'")
    except Exception as e:
        print(f"  ⚠️ Impossible d'écrire les IDs dans '{file_path.name}': {e}")


def read_source_file(file_path: Path) -> pd.DataFrame:
    """
    Lit un fichier source (CSV ou XLSX) et retourne un DataFrame normalisé.
    Colonnes attendues : Ressources, XP, (optionnel) ID
    """
    suffix = file_path.suffix.lower()

    try:
        if suffix == ".csv":
            # Essayer plusieurs encodages pour les CSV
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            last_error = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, delimiter=";", encoding=encoding)
                    break
                except (UnicodeDecodeError, UnicodeError) as e:
                    last_error = e
                    continue

            if df is None:
                raise last_error

        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, sheet_name=0)
        else:
            print(f"  SKIP '{file_path.name}': format non supporté")
            return pd.DataFrame()

        # Vérifier les colonnes obligatoires
        if "Ressources" not in df.columns or "XP" not in df.columns:
            print(f"  SKIP '{file_path.name}': colonnes 'Ressources' ou 'XP' manquantes")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"  ERROR '{file_path.name}': {e}")
        return pd.DataFrame()


def main():
    # Créer le dossier xp_familiers s'il n'existe pas
    XP_FAMILIERS_DIR.mkdir(parents=True, exist_ok=True)

    # Lister tous les fichiers CSV et XLSX
    source_files = list(XP_FAMILIERS_DIR.glob("*.csv")) + list(XP_FAMILIERS_DIR.glob("*.xlsx")) + list(XP_FAMILIERS_DIR.glob("*.xls"))

    if not source_files:
        print(f"Aucun fichier CSV/XLSX trouvé dans {XP_FAMILIERS_DIR}")
        return

    print(f"Fichiers trouvés : {len(source_files)}")
    for f in source_files:
        print(f"  - {f.name}")

    # Stocker toutes les données fusionnées
    all_items = []

    # Pour éviter les doublons, garder un index (id, source) -> données
    items_index = {}

    # Traiter chaque fichier source
    for source_file in source_files:
        source_name = source_file.stem  # Nom sans extension
        print(f"\nTraitement de '{source_file.name}'...")

        df_source = read_source_file(source_file)
        if df_source.empty:
            continue

        items_count = 0
        not_found = []
        ids_to_write = {}  # IDs trouvés via API à écrire dans le fichier source

        has_id_column = "ID" in df_source.columns

        for _, row in df_source.iterrows():
            name = str(row["Ressources"]).strip()
            xp_raw = row["XP"]

            # Convertir XP en float (gérer virgule et point comme séparateur décimal)
            try:
                if pd.notna(xp_raw):
                    # Remplacer virgule par point pour le format européen
                    xp_str = str(xp_raw).replace(',', '.')
                    xp = float(xp_str)
                else:
                    xp = None
            except (ValueError, TypeError):
                print(f"    WARN '{name}': XP invalide '{xp_raw}', ignoré")
                continue

            if xp is None or name == "nan":
                continue

            # Vérifier si un ID est fourni
            item_id = None
            if has_id_column:
                id_val = row.get("ID")
                if id_val is not None and pd.notna(id_val):
                    try:
                        item_id = int(id_val)
                        official_name = name
                    except (ValueError, TypeError):
                        pass

            # Si pas d'ID, chercher via l'API
            if item_id is None:
                print(f"    🔍 Recherche API pour '{name}'...")
                result = search_item_id(name)
                if result is not None:
                    item_id, official_name = result
                    print(f"    ✅ Trouvé : ID={item_id} ('{official_name}')")
                    ids_to_write[name] = item_id
                else:
                    not_found.append(name)
                    print(f"    ❌ NOT FOUND '{name}'")
                    continue

            # Ajouter ou mettre à jour l'item
            key = (item_id, source_name)
            items_index[key] = {
                "id": item_id,
                "libelle": official_name,
                "xp": xp,
                "source": source_name
            }
            items_count += 1

        # Écrire les IDs trouvés via API dans le fichier source
        if ids_to_write:
            write_ids_to_source(source_file, ids_to_write, df_source)

        print(f"  ✓ {items_count} items traités")
        if not_found:
            print(f"  ✗ {len(not_found)} items non trouvés")

    # Convertir en DataFrame
    all_items = list(items_index.values())

    if not all_items:
        print("\nAucune donnée à sauvegarder.")
        return

    df_final = pd.DataFrame(all_items)

    # Convertir XP en numérique pour s'assurer du type
    df_final["xp"] = pd.to_numeric(df_final["xp"], errors="coerce")

    # Trier par ID puis source
    df_final = df_final.sort_values(by=["id", "source"]).reset_index(drop=True)

    # Sauvegarder
    df_final.to_csv(ITEMS_XP_PATH, sep=";", index=False)

    print(f"\n✅ Fichier '{ITEMS_XP_PATH.name}' mis à jour avec {len(df_final)} entrées.")
    print(f"   Sources : {sorted(df_final['source'].unique())}")


if __name__ == "__main__":
    main()
