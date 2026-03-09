"""
Télécharge les données des monstres et de la géographie depuis l'API DofusDB.

Fichiers générés dans data/ :
  - monsters.json    : monstres avec stats moyennes et drops
  - races.json       : id → nom de race
  - subareas.json    : sous-zones (nom, areaId, liste de monstres)
  - areas.json       : zones (nom, superAreaId)
  - super_areas.json : super-zones (id → nom)

Usage :
  python scrapper/2_download_monsters.py
"""

import requests
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "https://api.dofusdb.fr"
DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "data"
LIMIT = 50


def fetch_all(endpoint: str, params: dict = None) -> list:
    """Récupère toutes les pages d'un endpoint paginé."""
    url = f"{BASE_URL}/{endpoint}"
    all_data = []
    skip = 0
    base_params = params or {}

    while True:
        response = requests.get(url, params={**base_params, "$limit": LIMIT, "$skip": skip})
        response.raise_for_status()
        page = response.json()

        batch = page.get("data", [])
        if not batch:
            break

        all_data.extend(batch)
        skip += LIMIT

        total = page.get("total", 0)
        print(f"  {endpoint} : {len(all_data)}/{total}", end="\r")

    print()
    return all_data


def avg_grades(grades: list, field: str) -> float | None:
    """Calcule la moyenne d'un champ sur les grades disponibles."""
    values = [g[field] for g in grades if field in g]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def avg_drop_rate(drop: dict) -> float:
    """Calcule le taux de drop moyen sur les 5 grades."""
    rates = [
        drop.get("percentDropForGrade1", 0),
        drop.get("percentDropForGrade2", 0),
        drop.get("percentDropForGrade3", 0),
        drop.get("percentDropForGrade4", 0),
        drop.get("percentDropForGrade5", 0),
    ]
    return round(sum(rates) / len(rates), 4)


def build_monster_subarea_map(subareas_raw: list) -> dict[int, list[int]]:
    """Construit un mapping monsterId → [subAreaId, ...] depuis les sous-zones."""
    mapping = {}
    for subarea in subareas_raw:
        subarea_id = subarea["id"]
        for monster_id in subarea.get("monsters", []):
            mapping.setdefault(monster_id, []).append(subarea_id)
    return mapping


# ─────────────────────────────────────────────────────────────────────────────
# Téléchargement
# ─────────────────────────────────────────────────────────────────────────────

def download_super_areas() -> dict:
    print("Téléchargement des super-zones...")
    raw = fetch_all("super-areas")
    result = {}
    for item in raw:
        result[str(item["id"])] = item["name"]["fr"]
    print(f"  → {len(result)} super-zones")
    return result


def download_areas() -> dict:
    print("Téléchargement des zones...")
    raw = fetch_all("areas")
    result = {}
    for item in raw:
        result[str(item["id"])] = {
            "id": item["id"],
            "name": item["name"]["fr"],
            "superAreaId": item["superAreaId"],
        }
    print(f"  → {len(result)} zones")
    return result


def download_subareas() -> dict:
    print("Téléchargement des sous-zones...")
    raw = fetch_all("subareas")
    result = {}
    for item in raw:
        result[str(item["id"])] = {
            "id": item["id"],
            "name": item["name"]["fr"],
            "areaId": item["areaId"],
            "monsters": item.get("monsters", []),
        }
    print(f"  → {len(result)} sous-zones")
    return result, raw


def download_races() -> dict:
    print("Téléchargement des races...")
    raw = fetch_all("monster-races")
    result = {}
    for item in raw:
        result[str(item["id"])] = item["name"]["fr"]
    print(f"  → {len(result)} races")
    return result


def download_monsters(monster_subarea_map: dict) -> dict:
    print("Téléchargement des monstres...")
    raw = fetch_all("monsters")
    result = {}

    for monster in raw:
        monster_id = monster["id"]
        grades = monster.get("grades", [])

        # Drops : exclure ceux avec taux moyen nul (drops conditionnels système)
        drops = []
        for drop in monster.get("drops", []):
            rate = avg_drop_rate(drop)
            if rate > 0:
                drops.append({
                    "id": drop["objectId"],
                    "avgRate": rate,
                })

        result[str(monster_id)] = {
            "id": monster_id,
            "name": monster.get("name", {}).get("fr", "") if isinstance(monster.get("name"), dict) else "",
            "gfxId": monster.get("gfxId"),
            "raceId": monster.get("race"),
            "subAreaIds": monster_subarea_map.get(monster_id, []),
            "isBoss": monster.get("isBoss", False),
            "isMiniBoss": monster.get("isMiniBoss", False),
            "isQuestMonster": monster.get("isQuestMonster", False),
            "level": avg_grades(grades, "level"),
            "lifePoints": avg_grades(grades, "lifePoints"),
            "earthResistance": avg_grades(grades, "earthResistance"),
            "fireResistance": avg_grades(grades, "fireResistance"),
            "waterResistance": avg_grades(grades, "waterResistance"),
            "airResistance": avg_grades(grades, "airResistance"),
            "neutralResistance": avg_grades(grades, "neutralResistance"),
            "drops": drops,
        }

    print(f"  → {len(result)} monstres")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Sauvegarde
# ─────────────────────────────────────────────────────────────────────────────

def save_json(data: dict, filename: str) -> None:
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = path.stat().st_size // 1024
    print(f"  ✓ {filename} ({len(data)} entrées, {size_kb} Ko)")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)

    print("=" * 50)
    print("Téléchargement des données monstres — DofusDB")
    print("=" * 50)

    super_areas = download_super_areas()
    areas = download_areas()
    subareas, subareas_raw = download_subareas()
    races = download_races()

    monster_subarea_map = build_monster_subarea_map(subareas_raw)
    monsters = download_monsters(monster_subarea_map)

    print("\nSauvegarde...")
    save_json(super_areas, "super_areas.json")
    save_json(areas, "areas.json")
    save_json(subareas, "subareas.json")
    save_json(races, "races.json")
    save_json(monsters, "monsters.json")

    print("\n✅ Terminé !")
