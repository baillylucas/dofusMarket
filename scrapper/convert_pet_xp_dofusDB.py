"""
Convertit data/pet_xp_dofusDB.txt vers data/xp_familiers/pet_xp_dofusDB.csv.

Format d'entrée (une ligne par item) :
  :inventory_resources: Nom (Niv. X) | XP_VALUE :picto_experience: (...)

Format de sortie CSV : ID;Ressources;XP
L'ID est recherché via l'API dofusdb si non disponible.
"""

import re
import csv
import sys
import requests
import unicodedata
from pathlib import Path

# Forcer UTF-8 sur stdout (terminal Windows en cp1252 par défaut)
sys.stdout.reconfigure(encoding="utf-8")

PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH  = PROJECT_DIR / "data" / "pet_xp_dofusDB.txt"
OUTPUT_PATH = PROJECT_DIR / "data" / "xp_familiers" / "pet_xp_dofusDB.csv"
DOFUSDB_API = "https://api.dofusdb.fr/items"

LINE_RE = re.compile(
    r':inventory_resources:\s+(.+?)\s+\(Niv\.\s*\d+\)\s+\|\s+([\d\s,]+)\s+:picto_experience:'
)


# ── Helpers API (repris de 7_update_xp_familier.py) ──────────────────────────

def strip_accents(text: str) -> str:
    text = text.replace("\u0152", "Oe").replace("\u0153", "oe")
    text = text.replace("\u00c6", "Ae").replace("\u00e6", "ae")
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def normalize(text: str) -> str:
    return strip_accents(text).strip().lower()


def search_item_id(name: str) -> tuple[int, str] | None:
    """Recherche l'ID d'un item par son nom via l'API dofusdb."""
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

    # 2) Fallback par regex sur le dernier mot significatif
    stop_words = {"de", "du", "des", "le", "la", "les", "en", "un", "une", "et", "d"}
    words = re.findall(r"[A-Za-zÀ-ÿŒœ]+", name)
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


# ── Parsing ───────────────────────────────────────────────────────────────────

def parse_xp(raw: str) -> float:
    """Convertit un nombre au format français (espace/espace fine=milliers, virgule=décimale) en float."""
    return float(raw.replace("\u202f", "").replace(" ", "").replace(",", "."))


def parse_line(line: str):
    """Retourne (name, xp) ou None si la ligne ne correspond pas au format attendu."""
    m = LINE_RE.search(line)
    if not m:
        return None
    name = m.group(1).strip()
    xp   = parse_xp(m.group(2).strip())
    return name, xp


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not INPUT_PATH.exists():
        print(f"[ERREUR] Fichier introuvable : {INPUT_PATH}")
        return

    lines = INPUT_PATH.read_text(encoding="utf-8").splitlines()
    print(f"{len(lines)} lignes lues depuis '{INPUT_PATH.name}'\n")

    parsed = []
    for line in lines:
        result = parse_line(line)
        if result:
            parsed.append(result)
        elif line.strip():
            print(f"  [WARN] Ligne non reconnue : {line[:80]}")

    print(f"{len(parsed)} items parses\n")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    not_found = []

    for name, xp in parsed:
        print(f"  [?] '{name}'...")
        result = search_item_id(name)
        if result is not None:
            item_id, official_name = result
            print(f"    [OK] ID={item_id} ('{official_name}')")
            rows.append((item_id, name, xp))
        else:
            print(f"    [NOT FOUND]")
            not_found.append(name)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "Ressources", "XP"])
        for item_id, name, xp in rows:
            writer.writerow([item_id, name, xp])

    print(f"\n{len(rows)} items ecrits dans '{OUTPUT_PATH.name}'")
    if not_found:
        print(f"{len(not_found)} items non trouves :")
        for n in not_found:
            print(f"   - {n}")


if __name__ == "__main__":
    main()
