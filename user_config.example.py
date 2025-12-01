"""
Configuration utilisateur - TEMPLATE
====================================

Ce fichier est un template de configuration utilisateur.
Pour l'utiliser :
1. Copiez ce fichier et renommez-le en "user_config.py"
2. Modifiez les valeurs selon votre configuration personnelle
3. Le fichier user_config.py ne sera pas commité (ignoré par git)

IMPORTANT : Ne commitez jamais user_config.py, seulement ce template !
"""

# ===========================
# Configuration Utilisateur
# ===========================

# Nom d'utilisateur actuel - À modifier selon votre pseudo Dofus
CURRENT_USER = "VotrePseudo"


# ===========================
# Configuration Tesseract-OCR
# ===========================

# Chemin vers l'exécutable Tesseract-OCR sur votre machine
# Windows par défaut : r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Mac : "/usr/local/bin/tesseract" ou "/opt/homebrew/bin/tesseract"
# Linux : "/usr/bin/tesseract"
TESSERAT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ===========================
# Coordonnées Spécifiques à Votre Écran
# ===========================
# IMPORTANT : Ces coordonnées dépendent de la résolution de votre écran et de la position
# de la fenêtre Dofus. Vous devez les calibrer selon votre configuration.
#
# Pour calibrer ces coordonnées :
# 1. Ouvrez Dofus en plein écran
# 2. Ouvrez un HDV
# 3. Utilisez un outil de capture d'écran pour noter les coordonnées (x, y)
# 4. Modifiez les valeurs ci-dessous

# Coordonnée barre de recherche de l'HDV
COORDINATES_SEARCH_BOX_TOP_LEFT = (580, 241)  # (x ; y)
COORDINATES_SEARCH_BOX_BOTTOM_RIGHT = (756, 265)

# Coordonnées du filtre niveau minimum
COORDINATES_INPUT_MIN_LVL_TOP_LEFT = (617, 317)
COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT = (663, 339)

# Coordonnées du filtre niveau maximum
COORDINATES_INPUT_MAX_LVL_TOP_LEFT = (706, 319)
COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT = (752, 339)

# Coordonnée du nom de la ressource
COORDINATES_RESSOURCE_NAME_TOP_LEFT = (893, 282)
COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT = (1111, 349)

# Coordonnée de la zone de l'item (clique dessous pour l'ouvrir et voir le prix des items) de l'HDV
COORDINATES_RESOURCE_ITEM_TOP_LEFT = (844, 280)
COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT = (1331, 349)

# Coordonnée de la zone de screen (uniquement le prix sur une seule ligne) de l'HDV
COORDINATES_SCREENSHOT_ZONE_TOP_LEFT = (175, 326)
COORDINATES_SCREENSHOT_ZONE_BOTTOM_RIGHT = (403, 361)

# Coordonnée de la zone de screen (uniquement le prix) de l'HDV
COORDINATES_SCREENSHOT_ZONE_PRICE_ONLY_TOP_LEFT = (264, 346)
COORDINATES_SCREENSHOT_ZONE_PRICE_ONLY_BOTTOM_RIGHT = (402, 380)

# Coordonnée de l'indication "panoplie" dans l'hdv equipement
COORDINATES_LABEL_PANOPLIE_TOP_LEFT = (210, 278)
COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT = (283, 304)

# Coordonnée de la zone de screen (uniquement le prix) pour les équipements ne faisant pas partie d'une panoplie, dans l'HDV equipement
COORDINATES_PRICE_ONLY_TOP_LEFT = (263, 326)
COORDINATES_PRICE_ONLY_BOTTOM_RIGHT = (401, 361)

# Coordonnée de la zone de screen (uniquement le prix) pour les équipements faisant partie d'une panoplie, dans l'HDV equipement
COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT = (266, 347)
COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT = (401, 381)

# Bouton pour annuler la recherche
COORDINATES_CANCEL_SEARCH_TOP_LEFT = (737, 246)
COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT = (747, 256)

# Coordonnées de l'input du tchat textuel
COORDINATES_CHAT_TOP_LEFT = (35, 1054)
COORDINATES_CHAT_BOTTOM_RIGHT = (288, 1073)

# Coordonnées des bâtiments HDV (spécifiques à votre position dans le jeu)
COORDINATES_HDV_RESSOURCES_TOP_LEFT = (470, 520)
COORDINATES_HDV_RESSOURCES_BOTTOM_RIGHT = (560, 561)

COORDINATES_HDV_EQUIPEMENT_TOP_LEFT = (561, 614)
COORDINATES_HDV_EQUIPEMENT_BOTTOM_RIGHT = (662, 668)

COORDINATES_HDV_CONSOMMABLES_TOP_LEFT = (1378, 401)
COORDINATES_HDV_CONSOMMABLES_BOTTOM_RIGHT = (1466, 466)

COORDINATES_HDV_FORGEMAGIE_TOP_LEFT = (582, 160)
COORDINATES_HDV_FORGEMAGIE_BOTTOM_RIGHT = (673, 222)

COORDINATES_HDV_CREATURES_TOP_LEFT = (1210, 348)
COORDINATES_HDV_CREATURES_BOTTOM_RIGHT = (1320, 488)

COORDINATES_HDV_COSMETIQUES_TOP_LEFT = (882, 322)
COORDINATES_HDV_COSMETIQUES_BOTTOM_RIGHT = (941, 402)

COORDINATES_HDV_AMES_TOP_LEFT = (0, 0)
COORDINATES_HDV_AMES_BOTTOM_RIGHT = (0, 0)

# Coordonnées du premier mot du message post /travel
COORDINATES_MSG_POST_TRAVEL_TOP_LEFT = (723, 505)
COORDINATES_MSG_POST_TRAVEL_BOTTOM_RIGHT = (743, 521)

# Coordonnées de l'affichage des coordonnées in game
COORDINATES_COORDS_TOP_LEFT = (0, 70)
COORDINATES_COORDS_BOTTOM_RIGHT = (80, 100)

# Coordonnées du Bouton de Confirmation d'un /travel
COORDINATES_CONFIRM_TOP_LEFT = (800, 585)
COORDINATES_CONFIRM_BOTTOM_RIGHT = (940, 593)

# Coordonnées du Bouton pour quitter l'HDV
COORDINATES_QUIT_HDV_TOP_LEFT = (1327, 153)
COORDINATES_QUIT_HDV_BOTTOM_RIGHT = (1340, 164)
