
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
                "cosmetiques"
            ),
            "ames.txt": HdvInfo(
                "ames.txt",
                COORDINATES_MAP_HDV_AMES,
                Rectangle(COORDINATES_HDV_AMES_TOP_LEFT, COORDINATES_HDV_AMES_BOTTOM_RIGHT),
                "ames"
            )
        }

class AutomationConfig:
    """Configuration de l'automatisation contenant les zones d'écran et les ressources à analyser."""
    
    def __init__(self):
        self.search_box = Rectangle(COORDINATES_SEARCH_BOX_TOP_LEFT, COORDINATES_SEARCH_BOX_BOTTOM_RIGHT)
        self.resource_item = Rectangle(COORDINATES_RESOURCE_ITEM_TOP_LEFT, COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT)
        self.screenshot_zone = Rectangle(COORDINATES_SCREENSHOT_ZONE_TOP_LEFT, COORDINATES_SCREENSHOT_ZONE_BOTTOM_RIGHT)
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
    
    def __init__(self):
        """Initialise le processeur d'image avec un compteur d'images."""
        self.screenshot_counter = 0

    def take_screenshot(self, zone: Rectangle) -> str:
        """Capture une zone de l'écran et sauvegarde l'image."""
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
        
        # Appliquer un seuil pour ne garder que le texte très clair (texte principal)
        # Ajustez la valeur 180 selon vos tests (entre 150-200 généralement)
        threshold_value = 190
        _, binary_mask = cv2.threshold(screenshot_cv, threshold_value, 255, cv2.THRESH_BINARY)
        
        # Créer une image avec fond uniforme
        background_gray = 41  # Couleur grise du fond #292C4D en niveaux de gris
        result = np.full_like(screenshot_cv, background_gray)
        
        # Copier uniquement les pixels clairs (texte principal)
        result[binary_mask == 255] = screenshot_cv[binary_mask == 255]
        
        # Convertir de retour en PIL Image
        screenshot = Image.fromarray(result)
        
        # Preprocessing supplémentaire pour améliorer l'OCR
        # Améliorer le contraste
        enhancer = ImageEnhance.Contrast(screenshot)
        screenshot = enhancer.enhance(2.0)
        
        # Améliorer la netteté
        enhancer = ImageEnhance.Sharpness(screenshot)
        screenshot = enhancer.enhance(2.0)
        
        filename = f"{FOLDER_IMAGE_PATH}/test_{self.screenshot_counter}.png"
        screenshot.save(filename)
        self.screenshot_counter += 1
        return filename
    
    @staticmethod
    def detect_single_price(image_path: str) -> Optional[int]:
        """Détecte un prix unique dans une image sans quantité."""
        # print(f"image_path : {image_path}")

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
        text = re.sub(r'\s+', '', text)
        if text and text.isdigit():
            return int(text)
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
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.processor = ImageProcessor()
        self.items_data = {}  # Cache pour les données JSON
        self.drive = GoogleDriveJSON(GOOGLE_DRIVE_FILE_ID, GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE)

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

    def travel_to_hdv(self, hdv_info: HdvInfo) -> None:
        """Se déplace vers l'HDV spécifié."""
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
        time.sleep(1)  # Attendre que le dialogue de confirmation apparaisse
        
        # Cliquer sur le bouton de confirmation
        confirm_zone = Rectangle(COORDINATES_CONFIRM_TOP_LEFT, COORDINATES_CONFIRM_BOTTOM_RIGHT)
        self.smooth_move_and_click(confirm_zone)

        time.sleep(20)
                   
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

    def smooth_move_and_click(self, rect: Rectangle, nb_click: int = 1) -> None:
        start_x, start_y = pyautogui.position()
        end_x = random.randint(rect.top_left[0], rect.bottom_right[0])
        end_y = random.randint(rect.top_left[1], rect.bottom_right[1])
        
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

    def search_item(self, item_name: str, item_level: Optional[int] = None) -> None:
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
        
        # Cliquer sur le bouton d'annulation de recherche
        cancel_zone = Rectangle(COORDINATES_CANCEL_SEARCH_TOP_LEFT, COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT)
        self.smooth_move_and_click(cancel_zone)
        time.sleep(0.2)

        # Cliquer sur la boîte de recherche et écrire le nom de l'item
        self.smooth_move_and_click(self.config.search_box)
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

    def find_item_position(self, target_name: str, is_equipment: bool = False) -> Optional[int]:
        """
        Cherche la position de l'item dans la liste de l'HDV.
        Retourne le nombre d'itérations nécessaires (0-11) ou None si non trouvé.
        Si aucune correspondance exacte, retourne la position de l'item avec 
        la plus haute similarité (minimum 80%).
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
                (name_zone.top_left[0], name_zone.top_left[1] + i * 73),
                (name_zone.bottom_right[0], name_zone.bottom_right[1] + i * 73)
            )
            
            screenshot_path = self.processor.take_screenshot(current_name_zone)
            
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

    def is_panoplie(self, item_position: int) -> bool:
        """
        Détecte si l'item sélectionné est une panoplie en analysant le label.
        Retourne True si le texte détecté correspond à "Panoplie" à au moins 90%.
        """
        label_zone = Rectangle(
            (COORDINATES_LABEL_PANOPLIE_TOP_LEFT[0],
            COORDINATES_LABEL_PANOPLIE_TOP_LEFT[1]),
            (COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT[0],
            COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT[1])
        )
        
        screenshot_path = self.processor.take_screenshot(label_zone)
        
        text = pytesseract.image_to_string(
            Image.open(screenshot_path),
            config=r'--oem 3 --psm 6',
            lang='fra'
        ).strip()
        
        # Nettoyer le texte détecté
        text = self.clean_item_name(text)
        target = self.clean_item_name("Panoplie")
        
        # Calculer la similarité
        similarity = SequenceMatcher(None, text, target).ratio()
        
        # print(f"Détection panoplie: '{text}' vs '{target}' - Similarité: {similarity*100:.1f}%")
        
        return similarity >= 0.90

    def process_item(self, item_name: str, is_equipment: bool = False, item_level: Optional[int] = None) -> Optional[ResourceResult]:
        """Traite un item et retourne ses prix. Lève une exception en cas d'erreur."""
        self.clear_search()
        time.sleep(0.1)
        
        # Passer le niveau à search_item
        self.search_item(item_name, item_level)
        time.sleep(1.5)

        item_position = self.find_item_position(item_name, is_equipment)
        
        if item_position is None:
            print(f"Item {item_name} non trouvé dans la liste")
            # Réinitialiser les filtres avant de retourner None
            if len(item_name) <= 3 and item_level is not None:
                self.reset_level_filters()
            return None
        else:
            print(f"Item {item_name} trouvé à la position : {item_position}")

        # Si l'item n'est pas en première position, ajuster les coordonnées
        if item_position > 0:
            adjusted_resource_zone = Rectangle(
                (self.config.resource_item.top_left[0], 
                self.config.resource_item.top_left[1] + item_position * 73),
                (self.config.resource_item.bottom_right[0], 
                self.config.resource_item.bottom_right[1] + item_position * 73)
            )
            self.smooth_move_and_click(adjusted_resource_zone, nb_click=1)
        else:
            self.smooth_move_and_click(self.config.resource_item, nb_click=1)
        
        time.sleep(0.6)
        
        # Traitement pour les équipements
        if is_equipment:
            # Détecter si c'est une panoplie
            panoplie = self.is_panoplie(item_position)
            
            if panoplie:
                screenshot_zone = Rectangle(
                    (COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT[0],
                    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT[1]),
                    (COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT[0],
                    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT[1])
                )
            else:
                screenshot_zone = Rectangle(
                    (COORDINATES_PRICE_ONLY_TOP_LEFT[0],
                    COORDINATES_PRICE_ONLY_TOP_LEFT[1]),
                    (COORDINATES_PRICE_ONLY_BOTTOM_RIGHT[0],
                    COORDINATES_PRICE_ONLY_BOTTOM_RIGHT[1])
                )
            
            screenshot_path = self.processor.take_screenshot(screenshot_zone)
            price = self.processor.detect_single_price(screenshot_path)
            
            # Réinitialiser les filtres avant de retourner le résultat
            if len(item_name) <= 3 and item_level is not None:
                self.reset_level_filters()
            
            if price:
                ressourceResult = ResourceResult(name=item_name, prices=[PriceInfo(quantity=1, price=price)])
                print(f"{ressourceResult}\n")
                return ressourceResult
            print(f"{item_name} is None\n")
            return None
        
        # Traitement pour les ressources (non-équipements)
        else:
            detected_prices = []
            
            # Récupérer les 4 prix aux positions 0, 1, 2, 3
            for position in range(4):
                screenshot_zone = Rectangle(
                    (COORDINATES_PRICE_ONLY_TOP_LEFT[0],
                    COORDINATES_PRICE_ONLY_TOP_LEFT[1] + position * 40),
                    (COORDINATES_PRICE_ONLY_BOTTOM_RIGHT[0],
                    COORDINATES_PRICE_ONLY_BOTTOM_RIGHT[1] + position * 40)
                )
                
                screenshot_path = self.processor.take_screenshot(screenshot_zone)
                price = self.processor.detect_single_price(screenshot_path)
                
                if price:
                    detected_prices.append(price)
                else:
                    detected_prices.append(None)
            
            # Réinitialiser les filtres avant de créer le résultat
            if len(item_name) <= 3 and item_level is not None:
                self.reset_level_filters()
            
            # Créer la liste finale de 4 PriceInfo avec les quantités attendues
            expected_quantities = [1, 10, 100, 1000]
            final_prices = []
            
            for i, expected_qty in enumerate(expected_quantities):
                if i < len(detected_prices) and detected_prices[i] is not None:
                    final_prices.append(PriceInfo(quantity=expected_qty, price=detected_prices[i]))
                else:
                    final_prices.append(PriceInfo(quantity=expected_qty, price=None))
            
            ressourceResult = ResourceResult(name=item_name, prices=final_prices)
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

        try:
            for filename, resources in self.config.resources_by_type.items():
                if filename not in self.config.hdv_manager.hdvs:
                    continue

                hdv_count += 1
                hdv_info = self.config.hdv_manager.hdvs[filename]
                is_equipment = (filename == "equipements.txt")
                
                print(f"{'='*60}")
                print(f"📍 HDV {hdv_count}/{total_hdvs} : {hdv_info.type_name}")
                print(f"{'='*60}\n")
                
                self.travel_to_hdv(hdv_info)

                resource_count = 0
                for resource in resources:
                    resource_count += 1
                    print(f"[{resource_count}/{len(resources)}] Traitement de : {resource}")
                    
                    # Récupérer le niveau de l'item
                    item_level = None
                    for item_id, item_data in self.items_data.items():
                        if item_data['name'] == resource:
                            item_level = item_data.get('level', None)
                            break
                    
                    result = self.process_item(resource, is_equipment=is_equipment, item_level=item_level)
                    
                    if result and result.prices:
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

def main():
    if not os.path.exists(FOLDER_IMAGE_PATH):
        os.makedirs(FOLDER_IMAGE_PATH)

    config = AutomationConfig()
    automator = Automator(config)
    
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

if __name__ == "__main__":
    main()
