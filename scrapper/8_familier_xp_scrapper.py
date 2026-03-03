"""
Scrapper Dofus — XP Familier
=============================

Ce script automatise la récupération des valeurs d'XP que peuvent donner
les ressources au familier du joueur.

Étapes exécutées :
  1. Chargement des items depuis Google Drive (même format que 5_dofus_scrapper).
  2. Scrapping des HDV : pour chaque ressource, vérifie si elle est déjà
     possédée (inventaire ou banque). Si non, tente de l'acheter si le prix
     est <= MAX_PRICE_FAMILIER.
  3. Récupération en banque : retrait des items marqués "en banque".
  4. Nourrissage du familier : glisser-déposer chaque item disponible sur
     le familier et capture de l'XP donné via OCR.
  5. Sauvegarde dans data/xp_familiers/scrapper_<date>.csv (traitable ensuite
     par scrapper/7_update_xp_familier.py).

Utilisation :
    python 8_familier_xp_scrapper.py [--debug]
"""

import pyautogui
import random
import time
from PIL import ImageGrab, Image, ImageEnhance
import pytesseract
import cv2
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Optional
import os
import json
import csv
from datetime import datetime
import unicodedata
import re
import numpy as np
import keyboard
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from googleDriveJSON import GoogleDriveJSON
from constants import *
from difflib import SequenceMatcher

# ─── Configuration Tesseract / PyAutoGUI ────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = TESSERAT_PATH
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# ─── Grille banque / inventaire ──────────────────────────────────────────────
GRID_COLS = 5   # Colonnes visibles dans la grille banque/inventaire
GRID_ROWS = 2   # Lignes à scanner dans la grille banque/inventaire (la recherche filtre en haut)

# Dimensions d'une cellule calculées une seule fois depuis les coordonnées haut-gauche/bas-droit
BANK_ITEM_W = COORDINATES_BANK_GRID_FIRST_ITEM_BOTTOM_RIGHT[0] - COORDINATES_BANK_GRID_FIRST_ITEM_TOP_LEFT[0]
BANK_ITEM_H = COORDINATES_BANK_GRID_FIRST_ITEM_BOTTOM_RIGHT[1] - COORDINATES_BANK_GRID_FIRST_ITEM_TOP_LEFT[1]
INVENTORY_ITEM_W = COORDINATES_INVENTORY_GRID_FIRST_ITEM_BOTTOM_RIGHT[0] - COORDINATES_INVENTORY_GRID_FIRST_ITEM_TOP_LEFT[0]
INVENTORY_ITEM_H = COORDINATES_INVENTORY_GRID_FIRST_ITEM_BOTTOM_RIGHT[1] - COORDINATES_INVENTORY_GRID_FIRST_ITEM_TOP_LEFT[1]

print(f"[Grille banque]     cellule l1c1 → largeur={BANK_ITEM_W}px  hauteur={BANK_ITEM_H}px  padding={BANK_ITEM_PADDING}px  (pas : {BANK_ITEM_W + BANK_ITEM_PADDING}px H / {BANK_ITEM_H + BANK_ITEM_PADDING}px V)")
print(f"[Grille inventaire] cellule l1c1 → largeur={INVENTORY_ITEM_W}px  hauteur={INVENTORY_ITEM_H}px  padding={INVENTORY_ITEM_PADDING}px  (pas : {INVENTORY_ITEM_W + INVENTORY_ITEM_PADDING}px H / {INVENTORY_ITEM_H + INVENTORY_ITEM_PADDING}px V)")

# Seuil de similarité minimal (ratio SequenceMatcher) pour valider un nom
NAME_MATCH_THRESHOLD = 0.80

# Mapping des types HDV vers les onglets disponibles en banque / inventaire.
# Les types sans onglet dédié (forgemagies, creatures, ames) sont redirigés
# vers l'onglet "ressources".
HDV_TO_BANK_TAB = {
    "equipements": "equipements",
    "consommables": "consommables",
    "ressources": "ressources",
    "cosmetiques": "cosmetiques",
    "forgemagies": "ressources",
    "creatures": "cosmetiques",
    "ames": "ressources",
}


# ─── Dataclasses ────────────────────────────────────────────────────────────

@dataclass
class Rectangle:
    """Zone rectangulaire de l'écran définie par deux coins opposés."""
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]

    def center(self) -> Tuple[int, int]:
        return (
            (self.top_left[0] + self.bottom_right[0]) // 2,
            (self.top_left[1] + self.bottom_right[1]) // 2,
        )


@dataclass
class HdvInfo:
    """Informations d'un HDV : coordonnées map, zone bâtiment et nom."""
    file_name: str
    map_coords: Tuple[int, int]
    building_zone: Rectangle
    type_name: str
    entry_zone: Optional[Rectangle] = None


@dataclass
class BankItem:
    """Item à récupérer depuis la banque."""
    item_id: str
    item_name: str
    hdv_type: str          # Type HDV (ex : "ressources")


@dataclass
class XpResult:
    """Résultat de XP donné par un item au familier."""
    item_id: str
    item_name: str
    xp: Optional[float]
    hdv_type: str


# ─── Gestionnaire des HDVs ───────────────────────────────────────────────────

class HdvManager:
    """Référentiel des HDVs avec leurs coordonnées."""

    def __init__(self):
        self.hdvs: Dict[str, HdvInfo] = {
            "ressources.txt": HdvInfo(
                "ressources.txt",
                COORDINATES_MAP_HDV_RESSOURCES,
                Rectangle(COORDINATES_HDV_RESSOURCES_TOP_LEFT, COORDINATES_HDV_RESSOURCES_BOTTOM_RIGHT),
                "ressources",
            ),
            "equipements.txt": HdvInfo(
                "equipements.txt",
                COORDINATES_MAP_HDV_EQUIPEMENT,
                Rectangle(COORDINATES_HDV_EQUIPEMENT_TOP_LEFT, COORDINATES_HDV_EQUIPEMENT_BOTTOM_RIGHT),
                "equipements",
            ),
            "consommables.txt": HdvInfo(
                "consommables.txt",
                COORDINATES_MAP_HDV_CONSOMMABLES,
                Rectangle(COORDINATES_HDV_CONSOMMABLES_TOP_LEFT, COORDINATES_HDV_CONSOMMABLES_BOTTOM_RIGHT),
                "consommables",
            ),
            "forgemagies.txt": HdvInfo(
                "forgemagies.txt",
                COORDINATES_MAP_HDV_FORGEMAGIE,
                Rectangle(COORDINATES_HDV_FORGEMAGIE_TOP_LEFT, COORDINATES_HDV_FORGEMAGIE_BOTTOM_RIGHT),
                "forgemagies",
            ),
            "creatures.txt": HdvInfo(
                "creatures.txt",
                COORDINATES_MAP_HDV_CREATURES,
                Rectangle(COORDINATES_HDV_CREATURES_TOP_LEFT, COORDINATES_HDV_CREATURES_BOTTOM_RIGHT),
                "creatures",
            ),
            "cosmetiques.txt": HdvInfo(
                "cosmetiques.txt",
                COORDINATES_MAP_HDV_COSMETIQUES,
                Rectangle(COORDINATES_HDV_COSMETIQUES_TOP_LEFT, COORDINATES_HDV_COSMETIQUES_BOTTOM_RIGHT),
                "cosmetiques",
                Rectangle(COORDINATES_ENTRY_COSMETIQUES_TOP_LEFT, COORDINATES_ENTRY_COSMETIQUES_BOTTOM_RIGHT),
            ),
            "ames.txt": HdvInfo(
                "ames.txt",
                COORDINATES_MAP_HDV_AMES,
                Rectangle(COORDINATES_HDV_AMES_TOP_LEFT, COORDINATES_HDV_AMES_BOTTOM_RIGHT),
                "ames",
                Rectangle(COORDINATES_ENTRY_AMES_TOP_LEFT, COORDINATES_ENTRY_AMES_BOTTOM_RIGHT),
            ),
        }

    def get_bank_tab_zone(self, hdv_type: str) -> Optional[Rectangle]:
        """Retourne la zone de l'onglet banque correspondant au type HDV."""
        bank_tab_map = {
            "equipements": Rectangle(COORDINATES_BANK_TAB_EQUIPEMENTS_TOP_LEFT, COORDINATES_BANK_TAB_EQUIPEMENTS_BOTTOM_RIGHT),
            "consommables": Rectangle(COORDINATES_BANK_TAB_CONSOMMABLES_TOP_LEFT, COORDINATES_BANK_TAB_CONSOMMABLES_BOTTOM_RIGHT),
            "ressources": Rectangle(COORDINATES_BANK_TAB_RESSOURCES_TOP_LEFT, COORDINATES_BANK_TAB_RESSOURCES_BOTTOM_RIGHT),
            "cosmetiques": Rectangle(COORDINATES_BANK_TAB_COSMETIQUES_TOP_LEFT, COORDINATES_BANK_TAB_COSMETIQUES_BOTTOM_RIGHT),
        }
        tab_key = HDV_TO_BANK_TAB.get(hdv_type, "ressources")
        return bank_tab_map.get(tab_key)

    def get_inventory_tab_zone(self, hdv_type: str) -> Optional[Rectangle]:
        """Retourne la zone de l'onglet inventaire correspondant au type HDV."""
        inventory_tab_map = {
            "equipements": Rectangle(COORDINATES_INVENTORY_TAB_EQUIPEMENTS_TOP_LEFT, COORDINATES_INVENTORY_TAB_EQUIPEMENTS_BOTTOM_RIGHT),
            "consommables": Rectangle(COORDINATES_INVENTORY_TAB_CONSOMMABLES_TOP_LEFT, COORDINATES_INVENTORY_TAB_CONSOMMABLES_BOTTOM_RIGHT),
            "ressources": Rectangle(COORDINATES_INVENTORY_TAB_RESSOURCES_TOP_LEFT, COORDINATES_INVENTORY_TAB_RESSOURCES_BOTTOM_RIGHT),
            "cosmetiques": Rectangle(COORDINATES_INVENTORY_TAB_COSMETIQUES_TOP_LEFT, COORDINATES_INVENTORY_TAB_COSMETIQUES_BOTTOM_RIGHT),
        }
        tab_key = HDV_TO_BANK_TAB.get(hdv_type, "ressources")
        return inventory_tab_map.get(tab_key)


# ─── Traitement des images ───────────────────────────────────────────────────

class ImageProcessor:
    """Capture d'écran, pré-traitement et reconnaissance de texte (OCR)."""

    def __init__(self, debug: bool = False):
        self.screenshot_counter = 0
        self.debug = debug

    def take_screenshot(
        self,
        zone: Rectangle,
        custom_name: Optional[str] = None,
        apply_threshold: bool = False,
    ) -> str:
        """
        Capture la zone indiquée, applique un pré-traitement optionnel et
        sauvegarde l'image dans FOLDER_IMAGE_PATH_XP.

        Args:
            zone: Zone de l'écran à capturer.
            custom_name: Nom de fichier personnalisé (sans extension).
            apply_threshold: Si True, conserve uniquement le texte très clair
                             (utile pour les libellés sur fond sombre).

        Returns:
            Chemin du fichier image sauvegardé.
        """
        screenshot = ImageGrab.grab(bbox=(
            zone.top_left[0], zone.top_left[1],
            zone.bottom_right[0], zone.bottom_right[1],
        ))

        screenshot_array = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2GRAY)

        if apply_threshold:
            threshold_value = 190
            _, binary_mask = cv2.threshold(screenshot_cv, threshold_value, 255, cv2.THRESH_BINARY)
            background_gray = 41
            result = np.full_like(screenshot_cv, background_gray)
            result[binary_mask == 255] = screenshot_cv[binary_mask == 255]
            screenshot = Image.fromarray(result)
        else:
            screenshot = Image.fromarray(screenshot_cv)

        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Sharpness(screenshot)
        screenshot = enhancer.enhance(2.0)

        if custom_name:
            filename = f"{FOLDER_IMAGE_PATH_XP}/{custom_name}.png"
        else:
            filename = f"{FOLDER_IMAGE_PATH_XP}/xp_{self.screenshot_counter}.png"
            self.screenshot_counter += 1

        screenshot.save(filename)

        if self.debug:
            debug_zone = Rectangle(
                (zone.top_left[0] - 50, zone.top_left[1] - 50),
                (zone.bottom_right[0] + 50, zone.bottom_right[1] + 50),
            )
            debug_screenshot = ImageGrab.grab(bbox=(
                debug_zone.top_left[0], debug_zone.top_left[1],
                debug_zone.bottom_right[0], debug_zone.bottom_right[1],
            ))
            debug_filename = filename.replace(".png", "_debug.png")
            debug_screenshot.save(debug_filename)

        return filename

    @staticmethod
    def detect_number(image_path: str, debug: bool = False) -> Optional[float]:
        """
        Tente de lire un nombre (entier ou décimal) dans une image.
        Retourne None si aucun nombre valide n'est détecté.
        """
        if not os.path.exists(image_path):
            return None
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, binary = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
        scaled = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        raw = pytesseract.image_to_string(
            Image.fromarray(scaled),
            config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=+0123456789',
        )
        if debug:
            print(f"        [OCR brut] '{raw.strip()}' ({image_path})")
        text = re.sub(r'[^\d]', '', raw.strip())
        try:
            return float(text) if text else None
        except ValueError:
            return None

    @staticmethod
    def read_text(image_path: str) -> str:
        """Lit le texte brut dans une image via OCR."""
        if not os.path.exists(image_path):
            return ""
        return pytesseract.image_to_string(
            Image.open(image_path),
            config=r'--oem 3 --psm 6',
            lang='fra',
        ).strip()


# ─── Automatisation principale ───────────────────────────────────────────────

class FamilierXpScrapper:
    """
    Orchestre les 4 phases du scraping XP familier :
      - Phase 2 : Scan des HDV (inventaire, banque, achat).
      - Phase 3 : Récupération des items en banque.
      - Phase 4 : Nourrissage du familier et capture d'XP.
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.processor = ImageProcessor(debug=debug)
        self.hdv_manager = HdvManager()
        self.drive = GoogleDriveJSON(GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE)
        self.items_data: Dict = {}

        # Résultats inter-phases
        self.total_items: int = 0                        # Nb total d'items en entrée (phase 1)
        self.items_for_xp: List[BankItem] = []          # Items disponibles pour Phase 4
        self.items_to_bank: List[BankItem] = []          # Items à récupérer en banque (Phase 3)
        self.xp_results: List[XpResult] = []             # Résultats XP finaux

        # Suivi des échecs par catégorie
        self.failures: Dict[str, List[str]] = {
            "hdv_introuvable":          [],   # Item non trouvé dans la liste HDV
            "prix_indetectable":        [],   # Prix illisible par OCR
            "cout_trop_important":      [],   # Prix > MAX_PRICE_FAMILIER
            "introuvable_en_banque":    [],   # Item non trouvé dans la grille banque
            "introuvable_en_inventaire":[],   # Item non trouvé dans la grille inventaire
            "xp_non_capture":           [],   # XP illisible après nourrissage
        }

        # Chat / coords
        self.chat_zone = Rectangle(COORDINATES_CHAT_TOP_LEFT, COORDINATES_CHAT_BOTTOM_RIGHT)
        self.coords_zone = Rectangle(COORDINATES_COORDS_TOP_LEFT, COORDINATES_COORDS_BOTTOM_RIGHT)

    # ─── Mouvement souris ────────────────────────────────────────────────────

    def smooth_move_and_click(self, rect: Rectangle, nb_click: int = 1) -> None:
        """Déplace la souris en courbe de Bézier et clique dans la zone."""
        start_x, start_y = pyautogui.position()
        end_x = random.randint(rect.top_left[0], rect.bottom_right[0])
        end_y = random.randint(rect.top_left[1], rect.bottom_right[1])

        control_x = start_x + (end_x - start_x) * random.uniform(0.4, 0.6)
        control_y = start_y + (end_y - start_y) * random.uniform(0.2, 0.8)

        duration = random.uniform(0.3, 0.5)
        steps = int(duration * 100)

        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * end_x
            y = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * end_y
            remaining = 1 - t
            noise_x = random.uniform(-2, 2) * remaining
            noise_y = random.uniform(-2, 2) * remaining
            pyautogui.moveTo(x + noise_x, y + noise_y, duration=duration / steps, _pause=False)
            if random.random() < 0.05:
                time.sleep(random.uniform(0.001, 0.003))

        pyautogui.moveTo(end_x, end_y, duration=0.05)
        for _ in range(nb_click):
            if nb_click > 1:
                time.sleep(random.uniform(0.05, 0.15))
            pyautogui.click()

    def smooth_move_to(self, x: int, y: int) -> None:
        """Déplace la souris vers un point précis en courbe de Bézier."""
        start_x, start_y = pyautogui.position()
        control_x = start_x + (x - start_x) * random.uniform(0.4, 0.6)
        control_y = start_y + (y - start_y) * random.uniform(0.2, 0.8)
        duration = random.uniform(0.3, 0.5)
        steps = int(duration * 100)
        for i in range(steps + 1):
            t = i / steps
            px = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * control_x + t ** 2 * x
            py = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * control_y + t ** 2 * y
            pyautogui.moveTo(px, py, duration=duration / steps, _pause=False)
        pyautogui.moveTo(x, y, duration=0.05)

    # ─── Déplacements ────────────────────────────────────────────────────────

    def travel_to(self, map_coords: Tuple[int, int]) -> None:
        """Téléporte le personnage aux coordonnées map données via /travel."""
        self.smooth_move_and_click(self.chat_zone)
        time.sleep(0.5)
        command = f"/travel {map_coords[0]},{map_coords[1]}"
        pyautogui.write(command)
        time.sleep(0.5)
        keyboard.press_and_release('enter')
        time.sleep(1)
        confirm_zone = Rectangle(COORDINATES_CONFIRM_POST_TRAVEL_TOP_LEFT, COORDINATES_CONFIRM_POST_TRAVEL_BOTTOM_RIGHT)
        self.smooth_move_and_click(confirm_zone)
        time.sleep(20)

    def travel_to_hdv(self, hdv_info: HdvInfo) -> None:
        """Voyage vers l'HDV et clique sur le bâtiment pour entrer."""
        print(f"  → /travel vers {hdv_info.type_name} {hdv_info.map_coords}")
        self.travel_to(hdv_info.map_coords)

        if hdv_info.entry_zone is not None:
            print(f"  → Clic sur l'entrée intermédiaire de {hdv_info.type_name}")
            self.smooth_move_and_click(hdv_info.entry_zone)
            time.sleep(10)

        print(f"  → Clic sur le bâtiment HDV")
        self.smooth_move_and_click(hdv_info.building_zone)
        time.sleep(2)

    # ─── Nettoyage / normalisation du texte ─────────────────────────────────

    def clean_item_name(self, text: str) -> str:
        """
        Normalise un nom d'item :
          - supprime tout ce qui suit "Niveau compris" ou "Niveau"
          - strip les espaces/sauts de ligne en début et fin
          - remplace les sauts de ligne internes par des espaces
          - supprime les types d'items en fin de chaîne
          - supprime les accents
          - passe en minuscules
        """
        import re
        text = re.split(r'Niveau compris|Niveau', text, maxsplit=1)[0]
        text = text.strip('\n\r ')
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())
        for item_type in L_TYPES:
            if text.endswith(' ' + item_type):
                text = text[: -len(item_type)].strip()
                break
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        return text.lower()

    # ─── Recherche d'item dans l'HDV (liste déroulante) ─────────────────────

    def search_item_in_hdv(self, item_name: str, item_level: Optional[int] = None,
                           use_equipment_coords: bool = False) -> None:
        """Saisit le nom de l'item dans la barre de recherche de l'HDV."""
        if use_equipment_coords:
            cancel_zone = Rectangle(COORDINATES_CANCEL_SEARCH_EQUIPEMENT_TOP_LEFT, COORDINATES_CANCEL_SEARCH_EQUIPEMENT_BOTTOM_RIGHT)
            search_box = Rectangle(COORDINATES_SEARCH_BOX_EQUIPEMENT_TOP_LEFT, COORDINATES_SEARCH_BOX_EQUIPEMENT_BOTTOM_RIGHT)
        else:
            cancel_zone = Rectangle(COORDINATES_CANCEL_SEARCH_TOP_LEFT, COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT)
            search_box = Rectangle(COORDINATES_SEARCH_BOX_TOP_LEFT, COORDINATES_SEARCH_BOX_BOTTOM_RIGHT)

        if len(item_name) <= 3 and item_level is not None:
            min_zone = Rectangle(COORDINATES_INPUT_MIN_LVL_TOP_LEFT, COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT)
            self.smooth_move_and_click(min_zone)
            time.sleep(0.2)
            keyboard.write(str(item_level))
            time.sleep(0.2)
            max_zone = Rectangle(COORDINATES_INPUT_MAX_LVL_TOP_LEFT, COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT)
            self.smooth_move_and_click(max_zone)
            time.sleep(0.2)
            keyboard.write(str(item_level))
            time.sleep(0.2)

        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.2)
        self.smooth_move_and_click(search_box)
        keyboard.write(item_name)

    def reset_level_filters(self) -> None:
        """Réinitialise les filtres niveau min/max à 0 et 200."""
        min_zone = Rectangle(COORDINATES_INPUT_MIN_LVL_TOP_LEFT, COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT)
        self.smooth_move_and_click(min_zone)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')
        keyboard.write('0')
        time.sleep(0.2)
        max_zone = Rectangle(COORDINATES_INPUT_MAX_LVL_TOP_LEFT, COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT)
        self.smooth_move_and_click(max_zone)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')
        keyboard.write('200')
        time.sleep(0.2)

    def find_item_position_in_hdv(self, target_name: str,
                                   item_id: Optional[str] = None) -> Optional[int]:
        """
        Parcourt jusqu'à 8 lignes de résultats HDV et retourne la position
        (0-based) de l'item dont le nom correspond à target_name.
        Seuil : NAME_MATCH_THRESHOLD.
        """
        target_name = self.clean_item_name(target_name)
        name_zone_base = Rectangle(COORDINATES_RESSOURCE_NAME_TOP_LEFT, COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT)
        best_pos, best_sim, best_text = None, 0.0, ""

        for i in range(8):
            current_zone = Rectangle(
                (name_zone_base.top_left[0], name_zone_base.top_left[1] + i * ITEM_HEIGHT),
                (name_zone_base.bottom_right[0], name_zone_base.bottom_right[1] + i * ITEM_HEIGHT),
            )
            shot_name = f"{item_id}_hdv_pos_{i}" if item_id else None
            path = self.processor.take_screenshot(current_zone, custom_name=shot_name, apply_threshold=True)
            text = self.clean_item_name(self.processor.read_text(path))

            if self.debug:
                print(f"    [HDV pos {i}] '{text}'")

            if text == target_name:
                if self.debug:
                    print(f"    → Correspondance exacte à la position {i} : '{text}'")
                return i

            sim = SequenceMatcher(None, target_name, text).ratio()
            if sim > best_sim:
                best_sim, best_pos, best_text = sim, i, text

        if best_sim >= NAME_MATCH_THRESHOLD:
            if self.debug:
                print(f"    → Meilleure correspondance à la position {best_pos} ({best_sim*100:.1f}%) : '{best_text}'")
            return best_pos

        if self.debug:
            print(f"    → Aucune correspondance (meilleur : '{best_text}' à {best_sim*100:.1f}%)")
        return None

    def click_item_in_hdv(self, position: int) -> None:
        """Clique sur l'item à la position donnée dans la liste HDV."""
        item_zone_base = Rectangle(COORDINATES_RESOURCE_ITEM_TOP_LEFT, COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT)
        adjusted = Rectangle(
            (item_zone_base.top_left[0], item_zone_base.top_left[1] + position * ITEM_HEIGHT),
            (item_zone_base.bottom_right[0], item_zone_base.bottom_right[1] + position * ITEM_HEIGHT),
        )
        self.smooth_move_and_click(adjusted, nb_click=1)

    # ─── Phase 2 : vérification possession et achat ──────────────────────────

    def read_owned_quantity(self, zone: Rectangle, label: str) -> int:
        """
        Lit la quantité affichée dans la zone indiquée (ex : "Possédé : 3").
        Retourne 0 si aucun nombre n'est détecté.
        """
        path = self.processor.take_screenshot(zone, custom_name=f"owned_{label}")
        text = self.processor.read_text(path)
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0

    def check_and_buy(self, item_name: str, item_id: str) -> str:
        """
        Après avoir sélectionné un item dans l'HDV :
          - Capture les quantités possédées (inventaire, banque).
          - Si inventaire >= 1 → retourne "inventory" (déjà disponible).
          - Si banque >= 1     → retourne "bank"      (à récupérer).
          - Sinon, capture le premier prix :
              - Si prix <= MAX_PRICE_FAMILIER → clique Acheter → "bought".
              - Sinon                         → retourne "unavailable".

        Returns:
            "inventory" | "bank" | "bought" | "unavailable"
        """
        # Quantité en inventaire
        inv_zone = Rectangle(COORDINATES_HDV_OWNED_INVENTORY_TOP_LEFT, COORDINATES_HDV_OWNED_INVENTORY_BOTTOM_RIGHT)
        qty_inv = self.read_owned_quantity(inv_zone, f"{item_id}_inv")
        if qty_inv >= 1:
            print(f"    Inventaire : {qty_inv} → ignoré (déjà possédé)")
            return "inventory"

        # Quantité en banque
        bank_zone = Rectangle(COORDINATES_HDV_OWNED_BANK_TOP_LEFT, COORDINATES_HDV_OWNED_BANK_BOTTOM_RIGHT)
        qty_bank = self.read_owned_quantity(bank_zone, f"{item_id}_bank")
        if qty_bank >= 1:
            print(f"    Banque : {qty_bank} → marqué pour récupération")
            return "bank"

        # Lecture du premier prix (x1)
        price_zone = Rectangle(COORDINATES_HDV_FIRST_PRICE_TOP_LEFT, COORDINATES_HDV_FIRST_PRICE_BOTTOM_RIGHT)
        price_path = self.processor.take_screenshot(price_zone, custom_name=f"{item_id}_first_price")
        price = self.processor.detect_number(price_path)

        if price is None:
            print(f"    ❌ Prix non détecté → ignoré")
            self.failures["prix_indetectable"].append(f"{item_id} ({item_name})")
            return "unavailable"

        if price > MAX_PRICE_FAMILIER:
            print(f"    ❌ Prix {price:.0f} > {MAX_PRICE_FAMILIER} → trop cher, ignoré")
            self.failures["cout_trop_important"].append(f"{item_id} ({item_name})")
            return "unavailable"

        # Achat
        print(f"    Prix {price:.0f} ≤ {MAX_PRICE_FAMILIER} → achat")
        buy_zone = Rectangle(COORDINATES_HDV_BUY_BTN_TOP_LEFT, COORDINATES_HDV_BUY_BTN_BOTTOM_RIGHT)
        self.smooth_move_and_click(buy_zone)
        time.sleep(1)
        return "bought"

    def process_hdv_phase(self, resources_by_type: Dict[str, List[str]]) -> None:
        """
        Phase 2 : parcourt chaque HDV et chaque ressource, décide si on
        ignore, marque pour la banque ou achète.
        Remplit self.items_for_xp et self.items_to_bank.
        """
        hdv_count = 0
        total_hdvs = sum(1 for f in resources_by_type if f in self.hdv_manager.hdvs)
        self.total_items = sum(len(v) for v in resources_by_type.values())

        for filename, resources in resources_by_type.items():
            if filename not in self.hdv_manager.hdvs:
                continue

            hdv_count += 1
            hdv_info = self.hdv_manager.hdvs[filename]
            use_equipment_coords = filename in ("equipements.txt", "cosmetiques.txt")

            print(f"\n{'='*60}")
            print(f"📍 HDV {hdv_count}/{total_hdvs} : {hdv_info.type_name}")
            print(f"{'='*60}")

            self.travel_to_hdv(hdv_info)

            for idx, resource_name in enumerate(resources, 1):
                # Récupérer l'ID et le niveau depuis le JSON
                item_id, item_level = None, None
                for iid, idata in self.items_data.items():
                    if idata.get('name') == resource_name:
                        item_id = iid
                        item_level = idata.get('level')
                        break

                print(f"\n  [{idx}/{len(resources)}] {item_id} {resource_name}")

                # Recherche dans l'HDV
                self.search_item_in_hdv(resource_name, item_level, use_equipment_coords)
                time.sleep(1.5)

                position = self.find_item_position_in_hdv(resource_name, item_id)
                if position is None:
                    print(f"    ❌ Non trouvé dans la liste HDV")
                    self.failures["hdv_introuvable"].append(f"{item_id or ''} ({resource_name})")
                    if len(resource_name) <= 3 and item_level:
                        self.reset_level_filters()
                    continue

                self.click_item_in_hdv(position)
                time.sleep(0.6)

                status = self.check_and_buy(resource_name, item_id or resource_name)

                bank_item = BankItem(
                    item_id=item_id or "",
                    item_name=resource_name,
                    hdv_type=hdv_info.type_name,
                )

                if status == "inventory":
                    self.items_for_xp.append(bank_item)
                elif status == "bank":
                    self.items_to_bank.append(bank_item)
                elif status == "bought":
                    self.items_for_xp.append(bank_item)
                # "unavailable" → rien

                if len(resource_name) <= 3 and item_level:
                    self.reset_level_filters()

            # Quitter l'HDV
            quit_zone = Rectangle(COORDINATES_QUIT_HDV_TOP_LEFT, COORDINATES_QUIT_HDV_BOTTOM_RIGHT)
            self.smooth_move_and_click(quit_zone)
            time.sleep(1)

    # ─── Phase 3 : récupération en banque ────────────────────────────────────

    def travel_to_bank(self) -> None:
        """Voyage jusqu'à la banque et entre dans le bâtiment."""
        print(f"\n{'='*60}")
        print(f"🏦 Déplacement vers la banque {COORDINATES_MAP_BANK}")
        print(f"{'='*60}")
        self.travel_to(COORDINATES_MAP_BANK)
        door_zone = Rectangle(COORDINATES_BANK_DOOR_TOP_LEFT, COORDINATES_BANK_DOOR_BOTTOM_RIGHT)
        print("  → Clic sur la porte de la banque")
        self.smooth_move_and_click(door_zone)
        time.sleep(5)

    def open_bank_account(self) -> None:
        """Parle au banquier et sélectionne "Consulter mon compte en banque"."""
        banker_zone = Rectangle(COORDINATES_BANKER_TOP_LEFT, COORDINATES_BANKER_BOTTOM_RIGHT)
        print("  → Clic sur le banquier")
        self.smooth_move_and_click(banker_zone)
        time.sleep(1.5)
        account_zone = Rectangle(COORDINATES_BANK_ACCOUNT_BTN_TOP_LEFT, COORDINATES_BANK_ACCOUNT_BTN_BOTTOM_RIGHT)
        print("  → Clic sur 'Consulter mon compte en banque'")
        self.smooth_move_and_click(account_zone)
        time.sleep(1.5)

    def _cell_center(self, row: int, col: int,
                     first_item_x: int, first_item_y: int,
                     item_w: int, item_h: int, padding: int) -> Tuple[int, int]:
        """
        Calcule le centre de la cellule (row, col) dans une grille d'items.
        row et col sont indexés à 0 (l1c1 → row=0, col=0).

        La coordonnée de départ (first_item_x, first_item_y) correspond au
        coin supérieur gauche de la cellule l1c1.
        Le centre de la cellule l1c1 est donc :
            x = first_item_x + item_w // 2
            y = first_item_y + item_h // 2
        """
        cell_x = first_item_x + col * (item_w + padding) + item_w // 2
        cell_y = first_item_y + row * (item_h + padding) + item_h // 2
        return cell_x, cell_y

    def _hover_name_for_grid(self, hover_zone: Rectangle, shot_name: str) -> str:
        """
        Prend un screenshot de la zone de tooltip après un survol d'item,
        applique le threshold pour ne garder que le texte mis en valeur,
        et retourne le nom normalisé via OCR.
        """
        path = self.processor.take_screenshot(hover_zone, custom_name=shot_name, apply_threshold=True)
        label = self.clean_item_name(self.processor.read_text(path))
        if self.debug:
            print(f"        → libellé détecté : '{label}'")
        return label

    def find_item_in_grid(
        self,
        target_name: str,
        first_item_tl: Tuple[int, int],
        item_w: int,
        item_h: int,
        padding: int,
        hover_zone: Rectangle,
        item_id: Optional[str] = None,
        prefix: str = "grid",
    ) -> Optional[Tuple[int, int]]:
        """
        Parcourt une grille de GRID_ROWS × GRID_COLS items en déplaçant la
        souris sur chaque cellule, capture le tooltip de nom et compare avec
        target_name.

        Position dans la grille : notation lRcC (ligne R, colonne C, base 1).

        Args:
            target_name: Nom normalisé de l'item recherché.
            first_item_tl: Coin supérieur gauche de la cellule l1c1 (pixels).
            item_w, item_h: Dimensions d'une cellule (pixels).
            padding: Espacement entre deux cellules (pixels).
            hover_zone: Zone de capture du tooltip de nom au survol.
            item_id: Pour nommer les screenshots (debug).
            prefix: Préfixe de nommage des screenshots.

        Returns:
            (row, col) indexé à 0 si trouvé, None sinon.
        """
        target_name = self.clean_item_name(target_name)
        best_pos, best_sim = None, 0.0

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                cx, cy = self._cell_center(
                    row, col,
                    first_item_tl[0], first_item_tl[1],
                    item_w, item_h, padding,
                )
                tl_x = cx - item_w // 2
                tl_y = cy - item_h // 2
                br_x = tl_x + item_w
                br_y = tl_y + item_h
                if self.debug:
                    print(f"      l{row+1}c{col+1}  TOP_LEFT=({tl_x} ; {tl_y})  BOTTOM_RIGHT=({br_x} ; {br_y})")
                self.smooth_move_to(cx, cy)
                time.sleep(1.0)   # Attendre l'apparition du tooltip

                shot_name = f"{item_id or 'item'}_{prefix}_l{row+1}c{col+1}"
                detected = self._hover_name_for_grid(hover_zone, shot_name)

                # detected = " bidcacxzaed ce" + detected + "deD ZAdaz"

                if detected == target_name:
                    print(f"      ✓ Trouvé à l{row+1}c{col+1}")
                    return row, col

                sim = SequenceMatcher(None, target_name, detected).ratio()
                if sim > best_sim:
                    best_sim, best_pos = sim, (row, col)

        if best_sim >= NAME_MATCH_THRESHOLD and best_pos is not None:
            r, c = best_pos
            print(f"      ✓ Meilleure correspondance à l{r+1}c{c+1} ({best_sim*100:.1f}%)")
            return best_pos

        print(f"      ❌ '{target_name}' non trouvé dans la grille")
        return None

    def search_item_in_bank(self, item_name: str) -> None:
        """Saisit le nom dans la barre de recherche de la banque."""
        cancel_zone = Rectangle(COORDINATES_BANK_CANCEL_SEARCH_TOP_LEFT, COORDINATES_BANK_CANCEL_SEARCH_BOTTOM_RIGHT)
        search_zone = Rectangle(COORDINATES_BANK_SEARCH_BOX_TOP_LEFT, COORDINATES_BANK_SEARCH_BOX_BOTTOM_RIGHT)
        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.2)
        self.smooth_move_and_click(search_zone)
        keyboard.write(item_name)
        time.sleep(1.0)

    def retrieve_item_from_bank(self, item: BankItem) -> bool:
        """
        Sélectionne l'onglet HDV, cherche l'item dans la grille et double-clique
        dessus pour le transférer en inventaire.

        Returns:
            True si l'item a été trouvé et double-cliqué.
        """
        # Recherche dans la barre de recherche
        self.search_item_in_bank(item.item_name)

        # Localisation dans la grille
        hover_zone = Rectangle(COORDINATES_BANK_HOVER_NAME_TOP_LEFT, COORDINATES_BANK_HOVER_NAME_BOTTOM_RIGHT)
        pos = self.find_item_in_grid(
            item.item_name,
            COORDINATES_BANK_GRID_FIRST_ITEM_TOP_LEFT,
            BANK_ITEM_W, BANK_ITEM_H, BANK_ITEM_PADDING,
            hover_zone,
            item_id=item.item_id or item.item_name,
            prefix="bank",
        )

        if pos is None:
            return False

        # Échap pour fermer tout tooltip/menu parasite avant le double-clic
        keyboard.press_and_release('escape')
        time.sleep(1.0)
        # Double-clic à la position actuelle de la souris (déjà sur la bonne cellule)
        pyautogui.click()
        time.sleep(0.10)
        pyautogui.click()
        time.sleep(0.5)

        # Annuler la recherche
        cancel_zone = Rectangle(COORDINATES_BANK_CANCEL_SEARCH_TOP_LEFT, COORDINATES_BANK_CANCEL_SEARCH_BOTTOM_RIGHT)
        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.3)

        return True

    def process_bank_phase(self) -> None:
        """
        Phase 3 : se rend à la banque et récupère tous les items de
        self.items_to_bank. Les items récupérés sont ajoutés à self.items_for_xp.
        """
        if not self.items_to_bank:
            print("\nPhase 3 : aucun item à récupérer en banque.")
            return

        self.travel_to_bank()
        self.open_bank_account()

        # Regrouper par onglet de catégorie banque
        items_by_tab: Dict[str, List[BankItem]] = {}
        for item in self.items_to_bank:
            tab = HDV_TO_BANK_TAB.get(item.hdv_type, "ressources")
            items_by_tab.setdefault(tab, []).append(item)

        for tab_name, items in items_by_tab.items():
            print(f"\n  Onglet banque : {tab_name} ({len(items)} items)")
            tab_zone = self.hdv_manager.get_bank_tab_zone(items[0].hdv_type)
            if tab_zone:
                self.smooth_move_and_click(tab_zone)
                time.sleep(0.5)
            for idx, item in enumerate(items, 1):
                print(f"  [{idx}/{len(items)}] {item.item_name}")
                success = self.retrieve_item_from_bank(item)
                if success:
                    print(f"    ✅ Récupéré")
                    self.items_for_xp.append(item)
                else:
                    print(f"    ❌ Non trouvé en banque")
                    self.failures["introuvable_en_banque"].append(f"{item.item_id} ({item.item_name})")

        # Fermer la banque
        keyboard.press_and_release('escape')
        time.sleep(0.5)
        keyboard.press_and_release('escape')
        time.sleep(1)
        print("\n  Banque fermée.")

    # ─── Phase 4 : nourrissage du familier ──────────────────────────────────

    def open_pet_feed_interface(self) -> bool:
        """
        Clic droit sur le familier puis clic gauche sur "Nourrir".

        Returns:
            True si le clic a pu être effectué.
        """
        print("  → Ouverture de l'inventaire (touche I)")
        keyboard.press_and_release('i')
        time.sleep(1.0)

        pet_zone = Rectangle(COORDINATES_PET_TOP_LEFT, COORDINATES_PET_BOTTOM_RIGHT)
        cx, cy = pet_zone.center()
        print("  → Clic droit sur le familier")
        pyautogui.rightClick(cx, cy)
        time.sleep(0.5)
        feed_btn = Rectangle(COORDINATES_PET_FEED_BTN_TOP_LEFT, COORDINATES_PET_FEED_BTN_BOTTOM_RIGHT)
        print("  → Clic sur 'Nourrir'")
        self.smooth_move_and_click(feed_btn)
        time.sleep(1.0)
        return True

    def search_item_in_inventory(self, item_name: str) -> None:
        """Saisit le nom dans la barre de recherche de l'inventaire."""
        cancel_zone = Rectangle(COORDINATES_INVENTORY_CANCEL_SEARCH_TOP_LEFT, COORDINATES_INVENTORY_CANCEL_SEARCH_BOTTOM_RIGHT)
        search_zone = Rectangle(COORDINATES_INVENTORY_SEARCH_BOX_TOP_LEFT, COORDINATES_INVENTORY_SEARCH_BOX_BOTTOM_RIGHT)
        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.2)
        self.smooth_move_and_click(search_zone)
        keyboard.write(item_name)
        time.sleep(1.0)

    def drag_item_to_pet_slot(self, item_cx: int, item_cy: int) -> None:
        """
        Effectue un drag & drop depuis la position de l'item (item_cx, item_cy)
        vers le slot de nourriture du familier.
        """
        slot_zone = Rectangle(COORDINATES_PET_FEED_SLOT_TOP_LEFT, COORDINATES_PET_FEED_SLOT_BOTTOM_RIGHT)
        slot_cx, slot_cy = slot_zone.center()

        self.smooth_move_to(item_cx, item_cy)
        time.sleep(0.2)
        pyautogui.mouseDown()
        time.sleep(0.4)
        self.smooth_move_to(slot_cx, slot_cy)
        time.sleep(0.2)
        pyautogui.mouseUp()
        time.sleep(0.5)

    def capture_xp_given(self, item_id: str) -> Optional[float]:
        """
        Capture la zone d'affichage de l'XP donné et de la quantité consommée.
        Retourne l'XP par unité (xp_total / quantité), ou None si non capturé.
        """
        time.sleep(0.3)   # Laisser le temps à l'animation d'apparaître

        xp_zone = Rectangle(COORDINATES_PET_XP_GIVEN_TOP_LEFT, COORDINATES_PET_XP_GIVEN_BOTTOM_RIGHT)
        path_xp = self.processor.take_screenshot(xp_zone, custom_name=f"{item_id}_xp_given")
        xp_total = self.processor.detect_number(path_xp, debug=self.debug)

        qty_zone = Rectangle(COORDINATES_PET_QTY_GIVEN_TOP_LEFT, COORDINATES_PET_QTY_GIVEN_BOTTOM_RIGHT)
        path_qty = self.processor.take_screenshot(qty_zone, custom_name=f"{item_id}_qty_given")
        qty = self.processor.detect_number(path_qty, debug=self.debug)

        if self.debug:
            print(f"    XP total : {xp_total}  |  Quantité donnée : {qty}")

        if xp_total is None:
            return None
        if qty is None or qty <= 0:
            if self.debug:
                print(f"    ⚠️  Quantité non détectée, XP non divisé")
            return round(xp_total, 2)

        xp_per_unit = round(xp_total / qty, 2)
        if self.debug:
            print(f"    XP par unité : {xp_total} / {qty} = {xp_per_unit}")
        return xp_per_unit

    def feed_item_to_pet(self, item: BankItem) -> Optional[float]:
        """
        Dans l'interface de nourrissage (inventaire ouvert) :
          1. Recherche l'item dans la barre de recherche.
          2. Localise l'item dans la grille via hover tooltip.
          3. Drag & drop vers le slot familier.
          4. Capture l'XP affiché.
          6. Annule la recherche.

        Returns:
            Valeur XP ou None si non trouvé / non capturé.
        """
        # Recherche
        self.search_item_in_inventory(item.item_name)

        # Localisation dans la grille inventaire
        hover_zone = Rectangle(COORDINATES_INVENTORY_HOVER_NAME_TOP_LEFT, COORDINATES_INVENTORY_HOVER_NAME_BOTTOM_RIGHT)
        pos = self.find_item_in_grid(
            item.item_name,
            COORDINATES_INVENTORY_GRID_FIRST_ITEM_TOP_LEFT,
            INVENTORY_ITEM_W, INVENTORY_ITEM_H, INVENTORY_ITEM_PADDING,
            hover_zone,
            item_id=item.item_id or item.item_name,
            prefix="inv",
        )

        if pos is None:
            print(f"    ❌ Introuvable en inventaire")
            self.failures["introuvable_en_inventaire"].append(f"{item.item_id} ({item.item_name})")
            cancel_zone = Rectangle(COORDINATES_INVENTORY_CANCEL_SEARCH_TOP_LEFT, COORDINATES_INVENTORY_CANCEL_SEARCH_BOTTOM_RIGHT)
            self.smooth_move_and_click(cancel_zone)
            return None

        row, col = pos
        item_cx, item_cy = self._cell_center(
            row, col,
            COORDINATES_INVENTORY_GRID_FIRST_ITEM_TOP_LEFT[0],
            COORDINATES_INVENTORY_GRID_FIRST_ITEM_TOP_LEFT[1],
            INVENTORY_ITEM_W, INVENTORY_ITEM_H, INVENTORY_ITEM_PADDING,
        )

        # Drag & drop → familier
        self.drag_item_to_pet_slot(item_cx, item_cy)

        # Capture XP (divisé par la quantité donnée)
        xp = self.capture_xp_given(item.item_id or item.item_name)

        # Fermer le résultat de nourrissage avant l'item suivant
        close_zone = Rectangle(COORDINATES_PET_FEED_CLOSE_TOP_LEFT, COORDINATES_PET_FEED_CLOSE_BOTTOM_RIGHT)
        self.smooth_move_and_click(close_zone)
        time.sleep(0.5)

        # Annuler la recherche
        cancel_zone = Rectangle(COORDINATES_INVENTORY_CANCEL_SEARCH_TOP_LEFT, COORDINATES_INVENTORY_CANCEL_SEARCH_BOTTOM_RIGHT)
        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.3)

        return xp

    def process_xp_phase(self) -> None:
        """
        Phase 4 : ouvre l'interface de nourrissage du familier, puis pour
        chaque item disponible, récupère l'XP donné et l'enregistre dans
        self.xp_results.
        """
        if not self.items_for_xp:
            print("\nPhase 4 : aucun item disponible pour le nourrissage.")
            return

        print(f"\n{'='*60}")
        print(f"🐾 Phase 4 : Nourrissage du familier ({len(self.items_for_xp)} items)")
        print(f"{'='*60}")

        self.open_pet_feed_interface()

        # Regrouper par onglet inventaire
        items_by_tab: Dict[str, List[BankItem]] = {}
        for item in self.items_for_xp:
            tab = HDV_TO_BANK_TAB.get(item.hdv_type, "ressources")
            items_by_tab.setdefault(tab, []).append(item)

        for tab_name, items in items_by_tab.items():
            if self.debug:
                print(f"\n  Onglet inventaire : {tab_name} ({len(items)} items)")
            tab_zone = self.hdv_manager.get_inventory_tab_zone(items[0].hdv_type)
            if tab_zone:
                self.smooth_move_and_click(tab_zone)
                time.sleep(0.5)
            for idx, item in enumerate(items, 1):
                if self.debug:
                    print(f"  [{idx}/{len(items)}] {item.item_id} {item.item_name}")
                xp = self.feed_item_to_pet(item)
                if xp is None:
                    print(f"    ❌ XP non capturé")
                    self.failures["xp_non_capture"].append(f"{item.item_id} ({item.item_name})")
                if self.debug:
                    print(f"    → XP unitaire enregistré : {xp}")
                else:
                    status_str = f"{xp} XP" if xp is not None else "❌ XP non capturé"
                    print(f"  [{idx}/{len(items)}] {item.item_id} {item.item_name} → {status_str}")
                self.xp_results.append(XpResult(
                    item_id=item.item_id,
                    item_name=item.item_name,
                    xp=xp,
                    hdv_type=item.hdv_type,
                ))

        # Fermer l'inventaire
        keyboard.press_and_release('escape')
        time.sleep(0.5)
        print("\n  Inventaire fermé.")

    # ─── Récapitulatif ───────────────────────────────────────────────────────

    def print_recap(self) -> None:
        """Affiche le récapitulatif final : succès, échecs par catégorie."""
        xp_ok = sum(1 for r in self.xp_results if r.xp is not None)
        print(f"\n{'='*60}")
        print(f"📊 RÉCAPITULATIF")
        print(f"{'='*60}")
        print(f"  XP obtenus : {xp_ok} / {self.total_items} items")

        failure_labels = {
            "hdv_introuvable":           "Introuvable à l'HDV",
            "prix_indetectable":         "Prix indétectable",
            "cout_trop_important":       f"Coût trop important (>{MAX_PRICE_FAMILIER})",
            "introuvable_en_banque":     "Introuvable en banque",
            "introuvable_en_inventaire": "Introuvable en inventaire",
            "xp_non_capture":            "XP non capturé",
        }

        any_failure = any(self.failures.values())
        if not any_failure:
            print("  ✅ Aucun échec !")
        else:
            for key, label in failure_labels.items():
                items = self.failures[key]
                if items:
                    print(f"\n  ❌ {label} ({len(items)}) :")
                    for entry in items:
                        print(f"      - {entry}")
        print(f"{'='*60}")

    # ─── Sauvegarde des résultats ────────────────────────────────────────────

    def save_results(self) -> None:
        """
        Sauvegarde les résultats XP dans data/xp_familiers/scrapper_<date>.csv.
        Format : Ressources;XP;ID  (compatible avec 7_update_xp_familier.py).
        """
        if not self.xp_results:
            print("\nAucun résultat XP à sauvegarder.")
            return

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, "data", "xp_familiers")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "xp_scraper.csv")

        now = datetime.now().strftime("%Y-%m-%dT%H:%M")
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["ID", "Ressources", "XP", "last_maj"])
            for result in self.xp_results:
                if result.xp is not None:
                    writer.writerow([result.item_id, result.item_name, result.xp, now])

        valid_count = sum(1 for r in self.xp_results if r.xp is not None)
        print(f"\n✅ {valid_count} résultats XP sauvegardés dans :")
        print(f"   {output_path}")

    # ─── Point d'entrée ─────────────────────────────────────────────────────

    def run(self) -> None:
        """Lance les 4 phases du scraping XP familier."""
        # Chargement des données JSON (Google Drive)
        print("📥 Chargement des données depuis Google Drive...")
        try:
            self.items_data = self.drive.read()
            print(f"   ✅ {len(self.items_data)} items chargés\n")
        except Exception as e:
            print(f"   ❌ Erreur : {e}")
            return

        # Récupération des items organisés par HDV
        try:
            from utils import get_scrapper_items_by_hdv
            items_by_hdv = get_scrapper_items_by_hdv(self.items_data)
        except Exception as e:
            print(f"❌ Impossible de charger les items du scrapper : {e}")
            return

        if not items_by_hdv:
            print("⚠️  Aucun item à traiter. Vérifiez que des items sont ajoutés dans le scrapper.")
            return

        # Conversion au format attendu (filename.txt → liste de noms)
        resources_by_type = {f"{hdv}.txt": names for hdv, names in items_by_hdv.items()}

        total = sum(len(v) for v in resources_by_type.values())
        print(f"📋 {total} items à traiter dans {len(resources_by_type)} HDV(s)\n")

        try:
            # ── Phase 2 : scan des HDV ───────────────────────────────────────
            print(f"\n{'='*60}")
            print("PHASE 2 — Scan des HDV")
            print(f"{'='*60}")
            self.process_hdv_phase(resources_by_type)
            print(f"\n  → {len(self.items_for_xp)} items disponibles directement")
            print(f"  → {len(self.items_to_bank)} items à récupérer en banque")

            # ── Phase 3 : récupération en banque ─────────────────────────────
            print(f"\n{'='*60}")
            print("PHASE 3 — Récupération en banque")
            print(f"{'='*60}")
            self.process_bank_phase()

            # ── Phase 4 : nourrissage du familier ────────────────────────────
            self.process_xp_phase()

        except pyautogui.FailSafeException:
            print("\n\n⚠️  FAILSAFE déclenché : souris en haut à gauche de l'écran")
            raise
        except KeyboardInterrupt:
            print("\n\n⚠️  Programme interrompu par l'utilisateur (Ctrl+C)")
            raise
        except Exception as e:
            print(f"\n❌ Erreur critique : {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.save_results()
            self.print_recap()


# ─── Redirection stdout (mode debug) ────────────────────────────────────────

class _Tee:
    """Redirige les écritures vers stdout ET un fichier simultanément."""

    def __init__(self, filepath: str):
        self._stdout = sys.stdout
        self._file = open(filepath, "w", encoding="utf-8")

    def write(self, data: str):
        self._stdout.write(data)
        self._file.write(data)

    def flush(self):
        self._stdout.flush()
        self._file.flush()

    def close(self):
        sys.stdout = self._stdout
        self._file.close()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrapper Dofus — XP Familier")
    parser.add_argument("--debug", action="store_true",
                        help="Active le mode debug (screenshots élargis + log)")
    args = parser.parse_args()

    os.makedirs(FOLDER_IMAGE_PATH_XP, exist_ok=True)

    log_path = os.path.join(FOLDER_IMAGE_PATH_XP, "xp_familier.txt")
    tee = _Tee(log_path)
    sys.stdout = tee
    if args.debug:
        print("🔧 Mode DEBUG activé")
    print(f"📄 Log : {os.path.abspath(log_path)}")

    scrapper = FamilierXpScrapper(debug=args.debug)

    print(f"⏳ Démarrage dans {TIME_BEFORE_SCRAPING} secondes...")
    time.sleep(TIME_BEFORE_SCRAPING)

    try:
        debut = time.time()
        scrapper.run()
        fin = time.time()
        print(f"\n{'='*60}")
        print(f"✅ TERMINÉ en {fin - debut:.2f} secondes")
        print(f"{'='*60}")

    except pyautogui.FailSafeException:
        print("\n👋 Programme arrêté via failsafe")
    except KeyboardInterrupt:
        print("\n👋 Programme arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Une erreur est survenue : {e}")
        import traceback
        traceback.print_exc()
    finally:
        if tee:
            tee.close()


if __name__ == "__main__":
    main()
