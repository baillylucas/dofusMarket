
import pyautogui
import random
import time
from PIL import ImageGrab, Image, ImageEnhance
import pytesseract
import cv2
from dataclasses import asdict, dataclass
from typing import Tuple, Dict, List, Optional
import os
import json
from datetime import datetime
import unicodedata
import re
import numpy as np
# import win32api
# import win32con
import keyboard
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from googleDriveJSON import GoogleDriveJSON
from constants import *
from difflib import SequenceMatcher

# Configuration Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = TESSERAT_PATH

# Configuration PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

@dataclass
class Rectangle:
    """Rectangle représentant une zone de l'écran avec des coordonnées de coins supérieur gauche et inférieur droit."""
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]

@dataclass
class PriceInfo:
    """Information sur une ressource contenant sa quantité et son prix."""
    quantity: int
    price: int

@dataclass
class ResourceResult:
    """Liste de toutes les ressources avec leur nom et leurs prix associés."""
    name: str
    prices: List[PriceInfo]

@dataclass
class HdvInfo:
    """Information sur un HDV avec ses coordonnées et positions associées."""
    file_name: str
    map_coords: Tuple[int, int]
    building_zone: Rectangle
    type_name: str
    entry_zone: Optional[Rectangle] = None


class HdvManager:
    """Gestionnaire des différents HDVs et leurs informations."""
    
    def __init__(self):
        self.hdvs = {
            "ressources.txt": HdvInfo(
                "ressources.txt",
                COORDINATES_MAP_HDV_RESSOURCES,
                Rectangle(COORDINATES_HDV_RESSOURCES_TOP_LEFT, COORDINATES_HDV_RESSOURCES_BOTTOM_RIGHT),
                "ressources"
            ),
            "equipements.txt": HdvInfo(
                "equipements.txt",
                COORDINATES_MAP_HDV_EQUIPEMENT,
                Rectangle(COORDINATES_HDV_EQUIPEMENT_TOP_LEFT, COORDINATES_HDV_EQUIPEMENT_BOTTOM_RIGHT),
                "equipements"
            ),
            "consommables.txt": HdvInfo(
                "consommables.txt",
                COORDINATES_MAP_HDV_CONSOMMABLES,
                Rectangle(COORDINATES_HDV_CONSOMMABLES_TOP_LEFT, COORDINATES_HDV_CONSOMMABLES_BOTTOM_RIGHT),
                "consommables"
            ),
            "forgemagies.txt": HdvInfo(
                "forgemagies.txt",
                COORDINATES_MAP_HDV_FORGEMAGIE,
                Rectangle(COORDINATES_HDV_FORGEMAGIE_TOP_LEFT, COORDINATES_HDV_FORGEMAGIE_BOTTOM_RIGHT),
                "forgemagies"
            ),
            
            "creatures.txt": HdvInfo(
                "creatures.txt",
                COORDINATES_MAP_HDV_CREATURES,
                Rectangle(COORDINATES_HDV_CREATURES_TOP_LEFT, COORDINATES_HDV_CREATURES_BOTTOM_RIGHT),
                "creatures"
            ),
            "cosmetiques.txt": HdvInfo(
                "cosmetiques.txt",
                COORDINATES_MAP_HDV_COSMETIQUES,
                Rectangle(COORDINATES_HDV_COSMETIQUES_TOP_LEFT, COORDINATES_HDV_COSMETIQUES_BOTTOM_RIGHT),
                "cosmetiques",
                Rectangle(COORDINATES_ENTRY_COSMETIQUES_TOP_LEFT, COORDINATES_ENTRY_COSMETIQUES_BOTTOM_RIGHT)
            ),
            "ames.txt": HdvInfo(
                "ames.txt",
                COORDINATES_MAP_HDV_AMES,
                Rectangle(COORDINATES_HDV_AMES_TOP_LEFT, COORDINATES_HDV_AMES_BOTTOM_RIGHT),
                "ames",
                Rectangle(COORDINATES_ENTRY_AMES_TOP_LEFT, COORDINATES_ENTRY_AMES_BOTTOM_RIGHT)
            )
        }

class AutomationConfig:
    """Configuration de l'automatisation contenant les zones d'écran et les ressources à analyser."""

    def __init__(self):
        # Coordonnées par défaut (pour HDV Ressources, Consommables, etc.)
        self.search_box = Rectangle(COORDINATES_SEARCH_BOX_TOP_LEFT, COORDINATES_SEARCH_BOX_BOTTOM_RIGHT)
        self.search_box_equipement = Rectangle(COORDINATES_SEARCH_BOX_EQUIPEMENT_TOP_LEFT, COORDINATES_SEARCH_BOX_EQUIPEMENT_BOTTOM_RIGHT)

        self.resource_item = Rectangle(COORDINATES_RESOURCE_ITEM_TOP_LEFT, COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT)
        self.coords_zone = Rectangle(COORDINATES_COORDS_TOP_LEFT, COORDINATES_COORDS_BOTTOM_RIGHT)
        self.chat_zone = Rectangle(COORDINATES_CHAT_TOP_LEFT, COORDINATES_CHAT_BOTTOM_RIGHT)

        self.hdv_manager = HdvManager()
        self.resources_by_type = self.load_all_resources()
    
    def load_resources(self, filename: str) -> List[str]:
        """
        DEPRECATED: Charge la liste des ressources depuis un fichier texte.
        Cette fonction est conservée pour compatibilité mais n'est plus utilisée.
        Utilisez load_all_resources() qui charge depuis le scrapper.
        """
        resources = []
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        resources.append(line)

            if not resources:
                print(f"Attention: Aucune ressource trouvée dans {filename}")
                return []
            return resources

        except Exception as e:
            print(f"Erreur lors de la lecture du fichier {filename}: {e}")
            return []

    def load_all_resources(self) -> Dict[str, List[str]]:
        """
        Charge les ressources depuis le scrapper (items + ingrédients) organisés par HDV.

        Returns:
            Dict[str, List[str]]: Format {hdv_name + ".txt": [liste de noms d'items]}
        """
        try:
            from utils import get_scrapper_items_by_hdv
            from googleDriveJSON import GoogleDriveJSON
            from constants import GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE

            # Charger les données depuis Google Drive
            drive = GoogleDriveJSON(GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE)
            data = drive.read()

            # Récupérer les items organisés par HDV
            items_by_hdv = get_scrapper_items_by_hdv(data)

            # Convertir au format attendu par le reste du code (ajouter .txt)
            resources_dict = {}
            for hdv_name, items in items_by_hdv.items():
                filename = f"{hdv_name}.txt"
                resources_dict[filename] = items
                print(f"✅ {filename}: {len(items)} items chargés depuis le scrapper")

            if not resources_dict:
                print("⚠️ Aucun item trouvé dans le scrapper. Vérifiez que des items sont ajoutés.")

            return resources_dict

        except Exception as e:
            print(f"❌ Erreur lors du chargement des items depuis le scrapper: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
class ImageProcessor:
    """Classe gérant le traitement des images et la détection de texte."""

    def __init__(self, debug: bool = False):
        """Initialise le processeur d'image avec un compteur d'images."""
        self.screenshot_counter = 0
        self.current_item_id = None  # ID de l'item en cours de traitement
        self.current_quantity = None  # Quantité en cours de capture
        self.debug = debug  # Mode debug pour screenshots élargis

    def take_screenshot(self, zone: Rectangle, custom_name: Optional[str] = None, apply_threshold: bool = False) -> str:
        """
        Capture une zone de l'écran et sauvegarde l'image.

        Args:
            zone: Zone de l'écran à capturer
            custom_name: Nom personnalisé pour le fichier (ex: "12345_x10")
            apply_threshold: Si True, applique un seuillage pour ne garder que le texte très clair (pour les libellés)
        """
        screenshot = ImageGrab.grab(bbox=(
            zone.top_left[0],
            zone.top_left[1],
            zone.bottom_right[0],
            zone.bottom_right[1]
        ))

        # Convertir PIL Image en array numpy
        screenshot_array = np.array(screenshot)

        # Convertir en niveaux de gris avec OpenCV
        screenshot_cv = cv2.cvtColor(screenshot_array, cv2.COLOR_RGB2GRAY)

        # Analyser la distribution des valeurs pour ajuster le seuil
        # (optionnel - pour debug)
        # print(f"Luminosité min: {screenshot_cv.min()}, max: {screenshot_cv.max()}, moyenne: {screenshot_cv.mean():.1f}")

        # Appliquer un seuil UNIQUEMENT si demandé (pour les libellés "Prix", "Panoplie", etc.)
        if apply_threshold:
            # Appliquer un seuil pour ne garder que le texte très clair (texte principal)
            # Ajustez la valeur 190 selon vos tests (entre 150-200 généralement)
            threshold_value = 190
            _, binary_mask = cv2.threshold(screenshot_cv, threshold_value, 255, cv2.THRESH_BINARY)

            # Créer une image avec fond uniforme
            background_gray = 41  # Couleur grise du fond #292C4D en niveaux de gris
            result = np.full_like(screenshot_cv, background_gray)

            # Copier uniquement les pixels clairs (texte principal)
            result[binary_mask == 255] = screenshot_cv[binary_mask == 255]

            # Convertir de retour en PIL Image
            screenshot = Image.fromarray(result)
        else:
            # Pas de seuillage, convertir directement en PIL Image
            screenshot = Image.fromarray(screenshot_cv)

        # Preprocessing supplémentaire pour améliorer l'OCR
        # Améliorer le contraste
        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(2.0)

        # Améliorer la netteté
        enhancer = ImageEnhance.Sharpness(screenshot)
        screenshot = enhancer.enhance(2.0)

        # Utiliser le nom personnalisé si fourni, sinon utiliser le compteur
        if custom_name:
            filename = f"{FOLDER_IMAGE_PATH}/{custom_name}.png"
        else:
            filename = f"{FOLDER_IMAGE_PATH}/test_{self.screenshot_counter}.png"
            self.screenshot_counter += 1

        screenshot.save(filename)

        # Si mode debug activé, prendre un deuxième screenshot élargi
        if self.debug:
            # Élargir la zone de 50 pixels de chaque côté
            debug_zone_top_left = (zone.top_left[0] - 50, zone.top_left[1] - 50)
            debug_zone_bottom_right = (zone.bottom_right[0] + 50, zone.bottom_right[1] + 50)

            # Capturer la zone élargie
            debug_screenshot = ImageGrab.grab(bbox=(
                debug_zone_top_left[0],
                debug_zone_top_left[1],
                debug_zone_bottom_right[0],
                debug_zone_bottom_right[1]
            ))

            # Sauvegarder avec le suffixe _debug
            if custom_name:
                debug_filename = f"{FOLDER_IMAGE_PATH}/{custom_name}_debug.png"
            else:
                debug_filename = f"{FOLDER_IMAGE_PATH}/test_{self.screenshot_counter - 1}_debug.png"

            debug_screenshot.save(debug_filename)

        return filename
    
    @staticmethod
    def detect_single_price(image_path: str, debug: bool = False) -> Optional[int]:
        """Détecte un prix unique dans une image sans quantité."""
        # Vérifier que l'image existe et est lisible
        if not os.path.exists(image_path):
            print(f"ERREUR: Image non trouvée : {image_path}")
            return None

        text = pytesseract.image_to_string(
            Image.open(image_path),
            config=r'--oem 3 --psm 6',
            lang='fra'
        )

        # Nettoyer et extraire le nombre
        raw_text = text
        text = re.sub(r'\s+', '', text)
        if text and text.isdigit():
            result = int(text)
            if debug:
                print(f"    [DEBUG prix] OCR brut: {repr(raw_text.strip())} → {result}")
            return result
        if debug:
            print(f"    [DEBUG prix] OCR brut: {repr(raw_text.strip())} → None (non numérique)")
        return None
    
    @staticmethod
    def clean_quantity(quantity_str: str) -> Optional[int]:
        """Nettoie et convertit la quantité en entier."""
        try:
            # Supprimer le 'x' au début
            quantity_str = quantity_str.lstrip('x')
            # Ne garder que les chiffres
            quantity_str = re.sub(r'\D', '', quantity_str)
            if quantity_str:
                return int(quantity_str)
        except (ValueError, AttributeError):
            pass
        return None

    def detect_quantity(self, zone: Rectangle, item_id: Optional[int] = None, position: int = 0) -> Optional[int]:
        """
        Capture et détecte la quantité dans une zone spécifique de l'écran.
        Valide que la quantité est dans [1, 10, 100, 1000].

        Args:
            zone: Zone de l'écran à capturer
            item_id: ID de l'item pour nommer le screenshot
            position: Position dans la liste (0-3)

        Returns:
            La quantité détectée si elle est valide (1, 10, 100, 1000), None sinon
        """
        # Générer le nom du screenshot
        custom_name = f"{item_id}_quantity_pos_{position}" if item_id else f"quantity_pos_{position}"

        # Capturer la zone de quantité
        screenshot_path = self.take_screenshot(zone, custom_name=custom_name)

        # Utiliser pytesseract pour détecter le texte
        text = pytesseract.image_to_string(
            Image.open(screenshot_path),
            config=r'--oem 3 --psm 6',
            lang='fra'
        )

        # Nettoyer le texte détecté
        raw_text = text.strip()
        text = raw_text.replace(" ", "").lower()

        # Extraire la quantité (format attendu: "x1", "x10", "x100", "x1000")
        quantity = self.clean_quantity(text)

        # Valider que la quantité est dans les valeurs acceptables
        VALID_QUANTITIES = {1, 10, 100, 1000}

        if quantity in VALID_QUANTITIES:
            if self.debug:
                print(f"    [DEBUG qté pos{position}] OCR brut: {repr(raw_text)} → x{quantity}")
            return quantity
        else:
            if self.debug:
                print(f"    [DEBUG qté pos{position}] OCR brut: {repr(raw_text)} → None (invalide: {quantity})")
            return None

    @staticmethod
    def clean_price(price_str: str) -> Optional[int]:
        """Nettoie et convertit le prix en entier en supprimant tous les caractères non numériques."""
        try:
            # Ne garder que les chiffres
            price_str = re.sub(r'\D', '', price_str)
            if price_str:
                return int(price_str)
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def process_quantities(clean_texts: List[str]) -> List[str]:
        processed_texts = []
        for i in range(len(clean_texts)):
            processed_texts.append(clean_texts[i])
            if (i < len(clean_texts) - 1 and 
                clean_texts[i].startswith('x') and 
                clean_texts[i + 1].startswith('x')):
                processed_texts.append('?')
        return processed_texts

    @staticmethod
    def process_detected_text(texts: List[str]) -> List[PriceInfo]:
        processed_results = []
        clean_texts = []
        for text in texts:
            text = text.strip().replace(" ", "")
            if text:
                clean_texts.append(text)

        clean_texts = ImageProcessor.process_quantities(clean_texts)
                
        for i in range(0, len(clean_texts) - 1, 2):
            if i + 1 < len(clean_texts):
                quantity_str = clean_texts[i]
                price_str = re.sub(r'^[^\d?]+|[^\d?]+$', '', clean_texts[i + 1])
                
                # Nettoyer et convertir la quantité
                quantity = ImageProcessor.clean_quantity(quantity_str)
                
                # Nettoyer et convertir le prix
                price = ImageProcessor.clean_price(price_str)
                
                # Ajouter seulement si les deux conversions ont réussi
                if quantity is not None and price is not None:
                    processed_results.append(PriceInfo(quantity=quantity, price=price))
                
        return processed_results

    @staticmethod
    def detect_text(image_path: str) -> List[PriceInfo]:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        display_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        detected_texts = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            roi = image[y:y+h, x:x+w]
            roi_resized = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            text = pytesseract.image_to_string(roi_resized, config=r'--psm 6')
            
            if text.strip():
                if text.startswith("x"):
                    text = text.replace(" ", "")
                detected_texts.append({
                    'text': text.strip(),
                    'position': (x, y, w, h)
                })
            
            cv2.rectangle(display_image, (x, y), (x + w, y + h), (255, 0, 0), 1)
        
        # debug_image_path = image_path.replace('.png', '_debug.png')
        # cv2.imwrite(debug_image_path, display_image)

        texts = [item['text'] for item in detected_texts]
        texts.reverse()

        return ImageProcessor.process_detected_text(texts)

class Automator:
    def __init__(self, config: AutomationConfig, debug: bool = False):
        self.config = config
        self.processor = ImageProcessor(debug=debug)
        self.items_data = {}  # Cache pour les données JSON
        self.drive = GoogleDriveJSON(GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE)
        self.debug = debug

    def save_json_data(self, reason: str = ""):
        """Sauvegarde les données JSON sur Google Drive."""
        try:
            if reason:
                print(f"\n💾 Sauvegarde d'urgence des données ({reason})...")
            else:
                print("\n💾 Sauvegarde des données...")

            self.drive.write(self.items_data)

            print("✅ Sauvegarde réussie sur Google Drive")

        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde : {e}")

    def get_current_position(self) -> Tuple[int, int]:
        """Détecte la position actuelle du joueur."""
        screenshot_path = self.processor.take_screenshot(self.config.coords_zone)
        
        # Charger l'image en niveaux de gris
        image = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        
        # Appliquer un seuillage pour améliorer la lisibilité des chiffres
        _, binary = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
        
        # Agrandir l'image pour améliorer la détection OCR
        scaled = cv2.resize(binary, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Améliorer les paramètres OCR pour la détection des chiffres
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=-0123456789,'
        text = pytesseract.image_to_string(scaled, config=custom_config)
        
        # Sauvegarder l'image traitée pour le debug
        debug_path = screenshot_path.replace('.png', '_debug.png')
        cv2.imwrite(debug_path, scaled)
        
        # print(f"Texte détecté: '{text}'")  # Debug
        
        # Recherche des coordonnées avec un pattern plus flexible
        matches = re.findall(r'(-?\d+)\s*,\s*(-?\d+)', text)
        if matches:
            x, y = map(int, matches[0])
            print(f"Coordonnées détectées : ({x}, {y})")  # Debug
            return (x, y)
            
        raise ValueError(f"Format de coordonnées non reconnu dans le texte: '{text}'")

    def travel_to_hdv(self, hdv_info: HdvInfo) -> bool:
        """
        Se déplace vers l'HDV spécifié.

        Returns:
            bool: True si le travel a réussi, False sinon
        """
        target_pos = hdv_info.map_coords

        # Focus sur le chat
        self.smooth_move_and_click(self.config.chat_zone)
        time.sleep(0.5)

        # Écrire la commande
        command = f"/travel {target_pos[0]},{target_pos[1]}"
        pyautogui.write(command)
        time.sleep(0.5)

        # Envoyer enter
        keyboard.press_and_release('enter')
        time.sleep(20)  # Attendre la téléportation

        # Si un point d'entrée est défini (pour cosmétiques et âmes), cliquer dessus d'abord
        if hdv_info.entry_zone is not None:
            print(f"Clic sur l'entrée de l'HDV {hdv_info.type_name}...")
            self.smooth_move_and_click(hdv_info.entry_zone)
            time.sleep(10)  # Attendre 10 secondes après le clic d'entrée

        # D'abord déplacer la souris vers le bâtiment
        start_x, start_y = pyautogui.position()
        end_x = random.randint(hdv_info.building_zone.top_left[0], hdv_info.building_zone.bottom_right[0])
        end_y = random.randint(hdv_info.building_zone.top_left[1], hdv_info.building_zone.bottom_right[1])
        
        # Utiliser le mouvement smooth existant
        control_x = start_x + (end_x - start_x) * random.uniform(0.4, 0.6)
        control_y = start_y + (end_y - start_y) * random.uniform(0.2, 0.8)
        
        duration = random.uniform(0.3, 0.5)
        steps = int(duration * 100)
        noise_amplitude = 2
        
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
            
            remaining_path = 1 - t
            noise_x = random.uniform(-noise_amplitude, noise_amplitude) * remaining_path
            noise_y = random.uniform(-noise_amplitude, noise_amplitude) * remaining_path
            
            pyautogui.moveTo(
                x + noise_x,
                y + noise_y,
                duration=duration/steps,
                _pause=False
            )
        
        # S'assurer que la souris est exactement à la position finale
        pyautogui.moveTo(end_x, end_y, duration=0.05)
        
        # Faire le clic maintenu
        time.sleep(0.2)
        pyautogui.mouseDown()
        time.sleep(0.3)
        pyautogui.mouseUp()
        time.sleep(1)

        return True  # Travel réussi

    def smooth_move_and_click(self, rect: Rectangle, nb_click: int = 1) -> None:
        start_x, start_y = pyautogui.position()

        # Réduire la zone cliquable de 10px de chaque côté pour éviter les clics en bordure
        MARGIN = 10
        tl_x = rect.top_left[0] + MARGIN
        tl_y = rect.top_left[1] + MARGIN
        br_x = rect.bottom_right[0] - MARGIN
        br_y = rect.bottom_right[1] - MARGIN
        # Si la marge rend la zone invalide, utiliser la zone d'origine
        if tl_x >= br_x or tl_y >= br_y:
            tl_x, tl_y = rect.top_left
            br_x, br_y = rect.bottom_right

        end_x = random.randint(tl_x, br_x)
        end_y = random.randint(tl_y, br_y)
        
        control_x = start_x + (end_x - start_x) * random.uniform(0.4, 0.6)
        control_y = start_y + (end_y - start_y) * random.uniform(0.2, 0.8)
        
        duration = random.uniform(0.3, 0.5)
        steps = int(duration * 100)
        noise_amplitude = 2
        
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
            
            remaining_path = 1 - t
            noise_x = random.uniform(-noise_amplitude, noise_amplitude) * remaining_path
            noise_y = random.uniform(-noise_amplitude, noise_amplitude) * remaining_path
            
            pyautogui.moveTo(
                x + noise_x,
                y + noise_y,
                duration=duration/steps,
                _pause=False
            )
            
            if random.random() < 0.05:
                time.sleep(random.uniform(0.001, 0.003))
        
        pyautogui.moveTo(end_x, end_y, duration=0.05)
        
        for _ in range(nb_click):
            if nb_click > 1:
                time.sleep(random.uniform(0.05, 0.15))
            pyautogui.click()

    def search_item(self, item_name: str, item_level: Optional[int] = None, use_equipment_coords: bool = False) -> None:
        # Si le nom est court (≤ 3 caractères) et qu'on a un niveau, appliquer le filtre
        if len(item_name) <= 3 and item_level is not None:
            # Cliquer sur le champ de niveau minimum
            min_level_zone = Rectangle(COORDINATES_INPUT_MIN_LVL_TOP_LEFT, COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT)
            self.smooth_move_and_click(min_level_zone)
            time.sleep(0.2)

            # Écrire le niveau
            keyboard.write(str(item_level))
            time.sleep(0.2)

            # Cliquer sur le champ de niveau maximum
            max_level_zone = Rectangle(COORDINATES_INPUT_MAX_LVL_TOP_LEFT, COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT)
            self.smooth_move_and_click(max_level_zone)
            time.sleep(0.2)

            # Écrire le niveau
            keyboard.write(str(item_level))
            time.sleep(0.2)

        # Choisir les bonnes coordonnées selon le type d'HDV
        if use_equipment_coords:
            cancel_zone = Rectangle(COORDINATES_CANCEL_SEARCH_EQUIPEMENT_TOP_LEFT, COORDINATES_CANCEL_SEARCH_EQUIPEMENT_BOTTOM_RIGHT)
            search_box = self.config.search_box_equipement
        else:
            cancel_zone = Rectangle(COORDINATES_CANCEL_SEARCH_TOP_LEFT, COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT)
            search_box = self.config.search_box

        # Cliquer sur le bouton d'annulation de recherche
        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.2)

        # Cliquer sur la boîte de recherche et écrire le nom de l'item
        self.smooth_move_and_click(search_box)
        keyboard.write(item_name)

    def reset_level_filters(self) -> None:
        """Réinitialise les filtres de niveau à 0 et 200."""
        # Réinitialiser le niveau minimum à 0
        min_level_zone = Rectangle(COORDINATES_INPUT_MIN_LVL_TOP_LEFT, COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT)
        self.smooth_move_and_click(min_level_zone)
        time.sleep(0.2)
        
        # Sélectionner tout et effacer
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        keyboard.write('0')
        time.sleep(0.2)
        
        # Réinitialiser le niveau maximum à 200
        max_level_zone = Rectangle(COORDINATES_INPUT_MAX_LVL_TOP_LEFT, COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT)
        self.smooth_move_and_click(max_level_zone)
        time.sleep(0.2)
        
        # Sélectionner tout et effacer
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        keyboard.write('200')
        time.sleep(0.2)

    def clear_search(self) -> None:
        self.smooth_move_and_click(self.config.search_box)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('backspace')
    
    def clean_item_name(self, text: str) -> str:
        """
        Nettoie le nom de l'item en remplaçant les sauts de ligne par des espaces,
        en supprimant le type de l'item s'il apparaît en fin de chaîne,
        en supprimant les accents et en convertissant en minuscules.
        """
        # Remplacer les sauts de ligne par des espaces
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Supprimer les espaces multiples
        text = ' '.join(text.split())
        
        # Supprimer le type s'il apparaît en fin de chaîne
        for item_type in L_TYPES:
            if text.endswith(' ' + item_type):
                text = text[:-len(item_type)].strip()
                break
        
        # Supprimer les accents
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Convertir en minuscules
        text = text.lower()
        
        return text

    def find_item_position(self, target_name: str, item_id: Optional[str] = None, is_equipment: bool = False) -> Optional[int]:
        """
        Cherche la position de l'item dans la liste de l'HDV.
        Retourne le nombre d'itérations nécessaires (0-11) ou None si non trouvé.
        Si aucune correspondance exacte, retourne la position de l'item avec
        la plus haute similarité (minimum 80%).

        Args:
            target_name: Nom de l'item à chercher
            item_id: ID de l'item (pour le nommage des screenshots)
            is_equipment: True si c'est un équipement
        """
        target_name = self.clean_item_name(target_name)

        name_zone = Rectangle(
            COORDINATES_RESSOURCE_NAME_TOP_LEFT,
            COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT
        )

        best_match_position = None
        best_similarity = 0.0

        for i in range(8):  # Maximum 8 tentatives
            current_name_zone = Rectangle(
                (name_zone.top_left[0], name_zone.top_left[1] + i * ITEM_HEIGHT),
                (name_zone.bottom_right[0], name_zone.bottom_right[1] + i * ITEM_HEIGHT)
            )

            # Nom du screenshot avec ID et position
            screenshot_name = f"{item_id}_position_{i}" if item_id else None
            screenshot_path = self.processor.take_screenshot(current_name_zone, custom_name=screenshot_name, apply_threshold=True)

            text = pytesseract.image_to_string(
                Image.open(screenshot_path),
                config=r'--oem 3 --psm 6',
                lang='fra'
            ).strip()

            # Nettoyage du texte
            text = self.clean_item_name(text)

            # Correspondance exacte
            if text == target_name:
                return i

            # Calculer la similarité
            similarity = SequenceMatcher(None, target_name.lower(), text.lower()).ratio()

            # print(f"Position {i}: '{text}' vs '{target_name}' - Similarité: {similarity*100:.1f}%")

            # Suivre le meilleur match
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_position = i

        # Si le meilleur match atteint au moins 80%, le retourner
        if best_similarity >= 0.80:
            # print(f"Meilleure correspondance trouvée à la position {best_match_position} avec {best_similarity*100:.1f}% de similarité")
            return best_match_position

        # print(f"Aucune correspondance suffisante trouvée (meilleur: {best_similarity*100:.1f}%)")
        return None

    def is_panoplie(self, item_position: int, y_offset: int = 0) -> bool:
        """
        Détecte si l'item sélectionné est une panoplie en analysant le label.
        Retourne True si du texte (peu importe lequel) est détecté, False si vide.
        y_offset : décalage vertical appliqué quand le libellé "Prix" est présent.
        """
        label_zone = Rectangle(
            (COORDINATES_LABEL_PANOPLIE_TOP_LEFT[0],
            COORDINATES_LABEL_PANOPLIE_TOP_LEFT[1] + y_offset),
            (COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT[0],
            COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT[1] + y_offset)
        )

        screenshot_path = self.processor.take_screenshot(label_zone)

        text = pytesseract.image_to_string(
            Image.open(screenshot_path),
            config=r'--oem 3 --psm 6',
            lang='fra'
        ).strip()

        # Nettoyer le texte détecté
        text = self.clean_item_name(text)

        # print(f"Détection panoplie: texte détecté = '{text}' -> {'Panoplie' if text else 'Pas panoplie'}")

        # Si du texte est détecté (non vide), c'est une panoplie
        return bool(text)

    def is_prix_label_present(self) -> bool:
        """
        Détecte si le libellé "Prix" est présent dans l'HDV ressources.
        Retourne True si le texte détecté correspond à "Prix" à au moins 90%.
        """
        label_zone = Rectangle(
            (COORDINATES_LABEL_PRIX_TOP_LEFT[0],
            COORDINATES_LABEL_PRIX_TOP_LEFT[1]),
            (COORDINATES_LABEL_PRIX_BOTTOM_RIGHT[0],
            COORDINATES_LABEL_PRIX_BOTTOM_RIGHT[1])
        )

        screenshot_path = self.processor.take_screenshot(label_zone)

        text = pytesseract.image_to_string(
            Image.open(screenshot_path),
            config=r'--oem 3 --psm 6',
            lang='fra'
        ).strip()

        # Nettoyer le texte détecté
        text = self.clean_item_name(text)
        target = self.clean_item_name("Prix")

        # Calculer la similarité
        similarity = SequenceMatcher(None, text, target).ratio()

        # print(f"Détection Prix: '{text}' vs '{target}' - Similarité: {similarity*100:.1f}%")

        return similarity >= 0.90

    def process_item(self, item_name: str, item_id: Optional[str] = None, is_equipment: bool = False, item_level: Optional[int] = None, use_equipment_coords: bool = False) -> Optional[ResourceResult]:
        """
        Traite un item et retourne ses prix. Lève une exception en cas d'erreur.

        Args:
            item_name: Nom de l'item à traiter
            item_id: ID de l'item (pour le nommage des screenshots)
            is_equipment: True si c'est un équipement
            item_level: Niveau de l'item pour le filtrage
            use_equipment_coords: True pour utiliser les coordonnées HDV équipements/cosmétiques
        """
        self.clear_search()
        time.sleep(0.1)

        # Passer le niveau et les coordonnées à search_item
        self.search_item(item_name, item_level, use_equipment_coords)
        time.sleep(1.5)

        item_position = self.find_item_position(item_name, item_id=item_id, is_equipment=is_equipment)

        if item_position is None:
            if item_id:
                print(f"❌ {item_name} (ID: {item_id}) - Non trouvé")
            else:
                print(f"❌ {item_name} - Non trouvé")
            # Réinitialiser les filtres avant de retourner None
            if len(item_name) <= 3 and item_level is not None:
                self.reset_level_filters()
            return None

        # Afficher le nom, l'ID et la position sur une seule ligne
        if item_id:
            print(f"✓ {item_name} (ID: {item_id}, pos: {item_position})")
        else:
            print(f"✓ {item_name} (pos: {item_position})")

        # Si l'item n'est pas en première position, ajuster les coordonnées
        if item_position > 0:
            adjusted_resource_zone = Rectangle(
                (self.config.resource_item.top_left[0],
                self.config.resource_item.top_left[1] + item_position * ITEM_HEIGHT),
                (self.config.resource_item.bottom_right[0],
                self.config.resource_item.bottom_right[1] + item_position * ITEM_HEIGHT)
            )
            self.smooth_move_and_click(adjusted_resource_zone, nb_click=1)
        else:
            self.smooth_move_and_click(self.config.resource_item, nb_click=1)
        
        time.sleep(0.6)

        # Détecter si le libellé "Prix" est présent (commun équipements et ressources)
        prix_label_present = self.is_prix_label_present()
        y_offset = PRIX_Y_OFFSET if prix_label_present else 0
        if self.processor.debug:
            print(f"    [DEBUG prix label] {'présent' if prix_label_present else 'absent'} → y_offset={y_offset}px")

        # Traitement pour les équipements
        if is_equipment:
            # Détecter si c'est une panoplie (avec offset si Prix présent)
            panoplie = self.is_panoplie(item_position, y_offset=y_offset)

            # Choisir les bonnes coordonnées selon panoplie ou non, avec offset Y
            if panoplie:
                quantity_coords_top_left = (COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT[0], COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT[1] + y_offset)
                quantity_coords_bottom_right = (COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT[0], COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT[1] + y_offset)
                price_coords_top_left = (COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT[0], COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT[1] + y_offset)
                price_coords_bottom_right = (COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT[0], COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT[1] + y_offset)
            else:
                quantity_coords_top_left = (COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT[0], COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT[1] + y_offset)
                quantity_coords_bottom_right = (COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT[0], COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT[1] + y_offset)
                price_coords_top_left = (COORDINATES_PRICE_ONLY_EQUIPEMENT_TOP_LEFT[0], COORDINATES_PRICE_ONLY_EQUIPEMENT_TOP_LEFT[1] + y_offset)
                price_coords_bottom_right = (COORDINATES_PRICE_ONLY_EQUIPEMENT_BOTTOM_RIGHT[0], COORDINATES_PRICE_ONLY_EQUIPEMENT_BOTTOM_RIGHT[1] + y_offset)

            # 1. Valider la quantité (doit être x1 pour les équipements)
            quantity_zone = Rectangle(
                quantity_coords_top_left,
                quantity_coords_bottom_right
            )

            detected_quantity = self.processor.detect_quantity(quantity_zone, item_id=item_id, position=0)

            # Si la quantité n'est pas x1, c'est anormal pour un équipement
            if detected_quantity is None or detected_quantity != 1:
                if item_id:
                    print(f"⚠️  Quantité invalide pour équipement {item_name} (ID: {item_id}): attendu x1, détecté: {detected_quantity}")
                else:
                    print(f"⚠️  Quantité invalide pour équipement {item_name}: attendu x1, détecté: {detected_quantity}")

                # Réinitialiser les filtres avant de retourner None
                if len(item_name) <= 3 and item_level is not None:
                    self.reset_level_filters()
                return None

            # 2. Capturer le prix
            screenshot_zone = Rectangle(
                price_coords_top_left,
                price_coords_bottom_right
            )

            # Nom du screenshot avec ID et quantité détectée
            screenshot_name = f"{item_id}_x{detected_quantity}" if item_id else None
            screenshot_path = self.processor.take_screenshot(screenshot_zone, custom_name=screenshot_name)
            price = self.processor.detect_single_price(screenshot_path, debug=self.processor.debug)

            # Réinitialiser les filtres avant de retourner le résultat
            if len(item_name) <= 3 and item_level is not None:
                self.reset_level_filters()

            if price:
                ressourceResult = ResourceResult(name=item_name, prices=[PriceInfo(quantity=detected_quantity, price=price)])
                if item_id:
                    print(f"{ressourceResult} (ID: {item_id})\n")
                else:
                    print(f"{ressourceResult}\n")
                return ressourceResult
            if item_id:
                print(f"{item_name} (ID: {item_id}) is None\n")
            else:
                print(f"{item_name} is None\n")
            return None
        
        # Traitement pour les ressources (non-équipements)
        else:
            detected_data = []  # Liste de tuples (quantity, price)

            # Coordonnées de base (libellé "Prix" absent) + offset Y si "Prix" présent
            quantity_coords_top_left = (COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_TOP_LEFT[0], COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_TOP_LEFT[1] + y_offset)
            quantity_coords_bottom_right = (COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_BOTTOM_RIGHT[0], COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_BOTTOM_RIGHT[1] + y_offset)
            price_coords_top_left = (COORDINATES_PRICE_ONLY_NO_PRIX_TOP_LEFT[0], COORDINATES_PRICE_ONLY_NO_PRIX_TOP_LEFT[1] + y_offset)
            price_coords_bottom_right = (COORDINATES_PRICE_ONLY_NO_PRIX_BOTTOM_RIGHT[0], COORDINATES_PRICE_ONLY_NO_PRIX_BOTTOM_RIGHT[1] + y_offset)

            # Récupérer les prix aux positions 0, 1, 2, 3 en validant d'abord les quantités
            for position in range(4):
                # 1. D'abord, capturer et valider la quantité
                quantity_zone = Rectangle(
                    (quantity_coords_top_left[0],
                    quantity_coords_top_left[1] + position * PRICE_LINE_HEIGHT),
                    (quantity_coords_bottom_right[0],
                    quantity_coords_bottom_right[1] + position * PRICE_LINE_HEIGHT)
                )

                detected_quantity = self.processor.detect_quantity(quantity_zone, item_id=item_id, position=position)

                # Si la quantité n'est pas valide, on arrête le scrapping de cet item
                # et on passe au prochain item en sauvegardant ce qu'on a déjà capturé
                if detected_quantity is None:
                    break  # Sortir de la boucle for et passer à la suite

                # 2. Si la quantité est valide, capturer le prix
                price_zone = Rectangle(
                    (price_coords_top_left[0],
                    price_coords_top_left[1] + position * PRICE_LINE_HEIGHT),
                    (price_coords_bottom_right[0],
                    price_coords_bottom_right[1] + position * PRICE_LINE_HEIGHT)
                )

                # Nom du screenshot avec ID et quantité détectée
                screenshot_name = f"{item_id}_x{detected_quantity}" if item_id else None
                screenshot_path = self.processor.take_screenshot(price_zone, custom_name=screenshot_name)
                price = self.processor.detect_single_price(screenshot_path, debug=self.processor.debug)

                # Stocker la quantité détectée et le prix associé
                detected_data.append((detected_quantity, price))

            # Afficher les quantités détectées
            if detected_data:
                quantities_str = ", ".join([f"x{qty}" for qty, _ in detected_data])
                if item_id:
                    print(f"    Quantités détectées : {quantities_str} (ID: {item_id})")
                else:
                    print(f"    Quantités détectées : {quantities_str}")

            # Réinitialiser les filtres avant de créer le résultat
            if len(item_name) <= 3 and item_level is not None:
                self.reset_level_filters()

            # Créer la liste finale avec les quantités et prix détectés
            # Toujours retourner 4 PriceInfo avec les quantités attendues
            expected_quantities = [1, 10, 100, 1000]
            final_prices = []

            for expected_qty in expected_quantities:
                # Chercher si cette quantité a été détectée
                found = False
                for detected_qty, detected_price in detected_data:
                    if detected_qty == expected_qty:
                        final_prices.append(PriceInfo(quantity=expected_qty, price=detected_price))
                        found = True
                        break

                # Si la quantité n'a pas été trouvée, ajouter None
                if not found:
                    final_prices.append(PriceInfo(quantity=expected_qty, price=None))

            ressourceResult = ResourceResult(name=item_name, prices=final_prices)
            if item_id:
                print(f"{ressourceResult} (ID: {item_id})\n")
            else:
                print(f"{ressourceResult}\n")
            return ressourceResult

    def process_all_resources(self) -> None:
        # Charger le JSON depuis Google Drive
        try:
            self.items_data = self.drive.read()
            print("✅ JSON chargé depuis Google Drive avec succès\n")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du JSON depuis Google Drive: {e}")
            return

        hdv_count = 0
        total_hdvs = len([f for f in self.config.resources_by_type.keys()
                         if f in self.config.hdv_manager.hdvs])
        no_price_items = []  # (item_name, item_id, raison)

        try:
            for filename, resources in self.config.resources_by_type.items():
                if filename not in self.config.hdv_manager.hdvs:
                    continue

                hdv_count += 1
                hdv_info = self.config.hdv_manager.hdvs[filename]
                is_equipment = (filename == "equipements.txt")
                # Pour les coordonnées de search box et cancel, équipements et cosmétiques utilisent les mêmes
                use_equipment_coords = (filename in ["equipements.txt", "cosmetiques.txt"])

                print(f"{'='*60}")
                print(f"📍 HDV {hdv_count}/{total_hdvs} : {hdv_info.type_name}")
                print(f"{'='*60}\n")

                # Tenter le travel vers l'HDV
                travel_success = self.travel_to_hdv(hdv_info)
                if not travel_success:
                    print(f"⚠️  Impossible de voyager vers l'HDV {hdv_info.type_name}. Passage à l'HDV suivant.\n")
                    continue

                resource_count = 0
                for resource in resources:
                    resource_count += 1
                    print(f"[{resource_count}/{len(resources)}] Traitement de : {resource}")

                    # Récupérer l'ID et le niveau de l'item
                    item_id = None
                    item_level = None
                    for current_id, item_data in self.items_data.items():
                        if item_data['name'] == resource:
                            item_id = current_id
                            item_level = item_data.get('level', None)
                            break

                    result = self.process_item(resource, item_id=item_id, is_equipment=is_equipment, item_level=item_level, use_equipment_coords=use_equipment_coords)

                    if result and result.prices:
                        # Vérifier si tous les prix sont None
                        all_none = all(p.price is None for p in result.prices)
                        if all_none:
                            no_price_items.append((resource, item_id, "trouvé mais tous les prix sont None"))
                        # Mettre à jour les données en mémoire
                        for item_id, item_data in self.items_data.items():
                            if item_data['name'] == result.name:
                                prices_dict = {}
                                for price_info in result.prices:
                                    prices_dict[str(price_info.quantity)] = price_info.price

                                now = datetime.now().strftime("%Y-%m-%dT%H:%M")
                                item_data['prix_hdv'][now] = prices_dict
                                item_data['last_maj'] = now
                                break
                    else:
                        no_price_items.append((resource, item_id, "non trouvé dans l'HDV"))

                # Quitter l'HDV
                quit_zone = Rectangle(COORDINATES_QUIT_HDV_TOP_LEFT, COORDINATES_QUIT_HDV_BOTTOM_RIGHT)
                self.smooth_move_and_click(quit_zone)
                time.sleep(1)

        except pyautogui.FailSafeException:
            print("\n\n⚠️  FAILSAFE déclenché : souris en haut à gauche de l'écran")
            self.save_json_data("failsafe - souris en haut à gauche")
            raise
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Programme interrompu par l'utilisateur (Ctrl+C)")
            self.save_json_data("interruption clavier")
            raise
        
        except Exception as e:
            print(f"\n❌ Erreur critique dans process_all_resources: {e}")
            self.save_json_data("erreur critique")
            raise
        
        finally:
            # Sauvegarde finale
            print("\n💾 Sauvegarde finale...")
            self.save_json_data("fin du programme")

            # Résumé des items sans prix
            if no_price_items:
                print(f"\n{'='*60}")
                print(f"⚠️  RÉSUMÉ — {len(no_price_items)} item(s) sans prix détecté :")
                print(f"{'='*60}")
                for name, iid, reason in no_price_items:
                    id_str = f" (ID: {iid})" if iid else ""
                    print(f"  • {name}{id_str} → {reason}")
                print(f"{'='*60}")
            else:
                print("\n✅ Tous les items ont au moins un prix détecté.")

class _Tee:
    """Redirige les écritures vers stdout ET un fichier simultanément."""

    def __init__(self, filepath):
        self._stdout = sys.stdout
        self._file = open(filepath, "w", encoding="utf-8")

    def write(self, data):
        self._stdout.write(data)
        self._file.write(data)

    def flush(self):
        self._stdout.flush()
        self._file.flush()

    def close(self):
        sys.stdout = self._stdout
        self._file.close()


def main():
    import argparse

    # Parser les arguments CLI
    parser = argparse.ArgumentParser(description="Scrapper Dofus HDV")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug avec screenshots élargis")
    args = parser.parse_args()

    tee = None
    if args.debug:
        if not os.path.exists(FOLDER_IMAGE_PATH):
            os.makedirs(FOLDER_IMAGE_PATH)
        debug_log_path = os.path.join(FOLDER_IMAGE_PATH, "debug.txt")
        tee = _Tee(debug_log_path)
        sys.stdout = tee
        print(f"🔧 Mode DEBUG activé - Screenshots élargis seront générés")
        print(f"📄 Log debug : {os.path.abspath(debug_log_path)}")

    if not os.path.exists(FOLDER_IMAGE_PATH):
        os.makedirs(FOLDER_IMAGE_PATH)

    config = AutomationConfig()
    automator = Automator(config, debug=args.debug)

    print(f"⏳ Le programme commencera dans {TIME_BEFORE_SCRAPING} secondes...")
    time.sleep(TIME_BEFORE_SCRAPING)
    
    try:
        debut = time.time()
        automator.process_all_resources()
        fin = time.time()
        
        total_resources = sum(len(resources) for resources in config.resources_by_type.values())
        print(f"\n{'='*60}")
        print(f"✅ TERMINÉ")
        print(f"⏱️  Temps d'exécution pour {total_resources} ressources = {fin - debut:.2f} secondes")
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
