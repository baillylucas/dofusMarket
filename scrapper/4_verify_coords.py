"""
Outil de vérification visuelle des coordonnées.
Affiche un overlay transparent avec les rectangles correspondant
aux coordonnées définies dans user_config.py.

Les coordonnées des bâtiments HDV ne sont PAS affichées.

Commandes :
- Échap : quitter
- Clic gauche : afficher les coordonnées du clic dans la console
"""

import argparse
import pygame
import sys
import os
import pyautogui
import win32gui
import win32con
import win32api
from pynput import keyboard

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_config import (
    COORDINATES_SEARCH_BOX_TOP_LEFT,
    COORDINATES_SEARCH_BOX_BOTTOM_RIGHT,
    COORDINATES_SEARCH_BOX_EQUIPEMENT_TOP_LEFT,
    COORDINATES_SEARCH_BOX_EQUIPEMENT_BOTTOM_RIGHT,
    COORDINATES_INPUT_MIN_LVL_TOP_LEFT,
    COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT,
    COORDINATES_INPUT_MAX_LVL_TOP_LEFT,
    COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT,
    COORDINATES_RESSOURCE_NAME_TOP_LEFT,
    COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT,
    COORDINATES_RESOURCE_ITEM_TOP_LEFT,
    COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT,
    COORDINATES_LABEL_PRIX_TOP_LEFT,
    COORDINATES_LABEL_PRIX_BOTTOM_RIGHT,
    COORDINATES_PRICE_ONLY_EQUIPEMENT_TOP_LEFT,
    COORDINATES_PRICE_ONLY_EQUIPEMENT_BOTTOM_RIGHT,
    COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_TOP_LEFT,
    COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_BOTTOM_RIGHT,
    COORDINATES_PRICE_ONLY_NO_PRIX_TOP_LEFT,
    COORDINATES_PRICE_ONLY_NO_PRIX_BOTTOM_RIGHT,
    COORDINATES_LABEL_PANOPLIE_TOP_LEFT,
    COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT,
    COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT,
    COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT,
    COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT,
    COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT,
    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT,
    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT,
    COORDINATES_CANCEL_SEARCH_TOP_LEFT,
    COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT,
    COORDINATES_CANCEL_SEARCH_EQUIPEMENT_TOP_LEFT,
    COORDINATES_CANCEL_SEARCH_EQUIPEMENT_BOTTOM_RIGHT,
    COORDINATES_CHAT_TOP_LEFT,
    COORDINATES_CHAT_BOTTOM_RIGHT,
    COORDINATES_MSG_POST_TRAVEL_TOP_LEFT,
    COORDINATES_MSG_POST_TRAVEL_BOTTOM_RIGHT,
    COORDINATES_CONFIRM_POST_TRAVEL_TOP_LEFT,
    COORDINATES_CONFIRM_POST_TRAVEL_BOTTOM_RIGHT,
    COORDINATES_COORDS_TOP_LEFT,
    COORDINATES_COORDS_BOTTOM_RIGHT,
    COORDINATES_QUIT_HDV_TOP_LEFT,
    COORDINATES_QUIT_HDV_BOTTOM_RIGHT,
    ITEM_HEIGHT,
    PRICE_LINE_HEIGHT,
    PRIX_Y_OFFSET,
)

# Couleurs (R, G, B, Alpha)
COLOR_SEARCH = (0, 255, 0, 180)         # Vert - barres de recherche
COLOR_LEVEL = (255, 255, 0, 180)        # Jaune - filtres niveau
COLOR_ITEM = (0, 200, 255, 180)         # Cyan - zone item / nom
COLOR_PRIX_LABEL = (255, 0, 255, 180)   # Magenta - labels (Prix, Panoplie)
COLOR_QUANTITY = (255, 165, 0, 180)     # Orange - quantités
COLOR_PRICE = (255, 80, 80, 180)        # Rouge clair - prix
COLOR_CANCEL = (200, 200, 200, 180)     # Gris - boutons annuler
COLOR_NAVIGATION = (100, 200, 100, 180) # Vert clair - navigation (chat, travel, coords, quit)

# Liste des rectangles : (label, top_left, bottom_right, color, mode, offsetable)
# mode       : "ressources" | "equipements" | "commun" (affiché dans les deux cas)
# offsetable : True si Tab doit décaler les coordonnées Y de PRIX_Y_OFFSET
ALL_RECTANGLES = [
    # --- Barres de recherche ---
    ("Recherche HDV",    COORDINATES_SEARCH_BOX_TOP_LEFT,            COORDINATES_SEARCH_BOX_BOTTOM_RIGHT,            COLOR_SEARCH,      "ressources",  False),
    ("Recherche Equip",  COORDINATES_SEARCH_BOX_EQUIPEMENT_TOP_LEFT, COORDINATES_SEARCH_BOX_EQUIPEMENT_BOTTOM_RIGHT, COLOR_SEARCH,      "equipements", False),

    # --- Filtres niveau (communs) ---
    ("Niveau min",       COORDINATES_INPUT_MIN_LVL_TOP_LEFT,         COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT,         COLOR_LEVEL,       "commun",      False),
    ("Niveau max",       COORDINATES_INPUT_MAX_LVL_TOP_LEFT,         COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT,         COLOR_LEVEL,       "commun",      False),

    # --- Zone nom / item (communs) ---
    ("Nom ressource",    COORDINATES_RESSOURCE_NAME_TOP_LEFT,        COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT,        COLOR_ITEM,        "commun",      False),
    ("Zone item",        COORDINATES_RESOURCE_ITEM_TOP_LEFT,         COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT,         COLOR_ITEM,        "commun",      False),

    # --- Label Prix (détection présence/absence) ---
    ("Label Prix",       COORDINATES_LABEL_PRIX_TOP_LEFT,            COORDINATES_LABEL_PRIX_BOTTOM_RIGHT,            COLOR_PRIX_LABEL,  "ressources",  False),

    # --- Cas 2 : Ressources (base, + offset si Prix présent) ---
    ("Qte Ress (no px)", COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_TOP_LEFT, COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_BOTTOM_RIGHT, COLOR_QUANTITY, "ressources", True),
    ("Prix (no prix)",   COORDINATES_PRICE_ONLY_NO_PRIX_TOP_LEFT,   COORDINATES_PRICE_ONLY_NO_PRIX_BOTTOM_RIGHT,    COLOR_PRICE,       "ressources",  True),

    # --- Cas 3 : Equipement (hors panoplie) ---
    ("Label Panoplie",   COORDINATES_LABEL_PANOPLIE_TOP_LEFT,           COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT,           COLOR_PRIX_LABEL,  "equipements", True),
    ("Qte Equip",        COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT,      COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT,      COLOR_QUANTITY,    "equipements", True),
    ("Prix Equip",       COORDINATES_PRICE_ONLY_EQUIPEMENT_TOP_LEFT,    COORDINATES_PRICE_ONLY_EQUIPEMENT_BOTTOM_RIGHT,    COLOR_PRICE,       "equipements", True),

    # --- Cas 4 : Equipement (panoplie) ---
    ("Qte Panoplie",     COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT,     COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT,     COLOR_QUANTITY,    "equipements", True),
    ("Prix Panoplie",    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT, COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT, COLOR_PRICE,   "equipements", True),

    # --- Boutons annuler ---
    ("Annuler recherche",    COORDINATES_CANCEL_SEARCH_TOP_LEFT,           COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT,           COLOR_CANCEL,      "ressources",  False),
    ("Annuler rech. equip",  COORDINATES_CANCEL_SEARCH_EQUIPEMENT_TOP_LEFT, COORDINATES_CANCEL_SEARCH_EQUIPEMENT_BOTTOM_RIGHT, COLOR_CANCEL,     "equipements", False),

    # --- Navigation (communs) ---
    ("Chat",             COORDINATES_CHAT_TOP_LEFT,                  COORDINATES_CHAT_BOTTOM_RIGHT,                  COLOR_NAVIGATION,  "commun",      False),
    ("Msg post travel",  COORDINATES_MSG_POST_TRAVEL_TOP_LEFT,       COORDINATES_MSG_POST_TRAVEL_BOTTOM_RIGHT,       COLOR_NAVIGATION,  "commun",      False),
    ("Confirm travel",   COORDINATES_CONFIRM_POST_TRAVEL_TOP_LEFT,   COORDINATES_CONFIRM_POST_TRAVEL_BOTTOM_RIGHT,   COLOR_NAVIGATION,  "commun",      False),
    ("Coords in-game",   COORDINATES_COORDS_TOP_LEFT,                COORDINATES_COORDS_BOTTOM_RIGHT,               COLOR_NAVIGATION,  "commun",      False),
    ("Quitter HDV",      COORDINATES_QUIT_HDV_TOP_LEFT,              COORDINATES_QUIT_HDV_BOTTOM_RIGHT,             COLOR_NAVIGATION,  "commun",      False),
]


def get_rectangles(mode):
    """Filtre les rectangles selon le mode choisi."""
    if mode is None:
        return [(label, tl, br, color, offsetable) for label, tl, br, color, _, offsetable in ALL_RECTANGLES]
    return [(label, tl, br, color, offsetable) for label, tl, br, color, m, offsetable in ALL_RECTANGLES if m in (mode, "commun")]


class CoordsVerifier:
    def __init__(self, rectangles):
        self.rectangles = rectangles
        pygame.init()

        self.screen_width, self.screen_height = pyautogui.size()

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.NOFRAME
        )
        pygame.display.set_caption("Verify Coords")

        # Rendre la fenetre semi-transparente et click-through
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            | win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT,
        )
        win32gui.SetLayeredWindowAttributes(
            hwnd, win32api.RGB(0, 0, 0), 128, win32con.LWA_ALPHA
        )
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )

        self.surface = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        self.font = pygame.font.SysFont("consolas", 12)
        self.running = True
        self.show_offset = False
        self.needs_redraw = False

        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.running = False
            return False
        if key == keyboard.Key.tab:
            self.show_offset = not self.show_offset
            self.needs_redraw = True
            label = f"+{PRIX_Y_OFFSET}px (avec Prix)" if self.show_offset else "base (sans offset)"
            print(f"[Tab] Mode : {label}")

    def draw_rect(self, label, top_left, bottom_right, color):
        """Dessine un rectangle avec son label."""
        x1, y1 = top_left
        x2, y2 = bottom_right
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

        # Remplissage semi-transparent
        fill_color = (color[0], color[1], color[2], 40)
        pygame.draw.rect(self.surface, fill_color, rect)

        # Bordure
        pygame.draw.rect(self.surface, color, rect, 2)

        # Label au-dessus du rectangle
        text_surface = self.font.render(label, True, (255, 255, 255, 255))
        text_x = min(x1, x2)
        text_y = min(y1, y2) - 14
        if text_y < 0:
            text_y = max(y1, y2) + 2

        # Fond noir derriere le texte pour la lisibilite
        bg_rect = text_surface.get_rect(topleft=(text_x, text_y))
        bg_rect.inflate_ip(4, 2)
        pygame.draw.rect(self.surface, (0, 0, 0, 200), bg_rect)
        self.surface.blit(text_surface, (text_x, text_y))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.surface.fill((0, 0, 0, 0))

        for label, top_left, bottom_right, color, offsetable in self.rectangles:
            if self.show_offset and offsetable:
                top_left = (top_left[0], top_left[1] + PRIX_Y_OFFSET)
                bottom_right = (bottom_right[0], bottom_right[1] + PRIX_Y_OFFSET)
                label = f"{label} +{PRIX_Y_OFFSET}"
            self.draw_rect(label, top_left, bottom_right, color)

        self.screen.blit(self.surface, (0, 0))
        pygame.display.flip()

    def run(self):
        self.keyboard_listener.start()

        print("=== Verification des coordonnees ===")
        print(f"{len(self.rectangles)} rectangles affiches")
        print("Appuyez sur Echap pour quitter.")
        print("Appuyez sur Tab pour basculer l'offset Y (PRIX_Y_OFFSET).")
        print()

        # Legende
        color_labels = {
            "Vert": "Barres de recherche",
            "Jaune": "Filtres niveau",
            "Cyan": "Zone item / nom",
            "Magenta": "Labels (Prix, Panoplie)",
            "Orange": "Quantites",
            "Rouge": "Prix",
            "Gris": "Boutons annuler",
            "Vert clair": "Navigation (chat, travel, coords, quit)",
        }
        print("Legende des couleurs :")
        for color_name, description in color_labels.items():
            print(f"  {color_name:12s} : {description}")
        print()

        self.draw()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            if self.needs_redraw:
                self.needs_redraw = False
                self.draw()
            pygame.time.wait(50)

        self.keyboard_listener.stop()
        pygame.quit()
        print("Overlay ferme.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vérification visuelle des coordonnées")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["ressources", "equipements"],
        help="Afficher uniquement les coordonnées HDV ressources ou équipements (défaut : tout afficher)",
    )
    args = parser.parse_args()

    rectangles = get_rectangles(args.mode)
    if args.mode:
        print(f"Mode : {args.mode}")
    verifier = CoordsVerifier(rectangles)
    verifier.run()
