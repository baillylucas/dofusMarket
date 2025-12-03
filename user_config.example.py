"""
Configuration utilisateur - TEMPLATE
====================================

Ce fichier est un template de configuration utilisateur.
Pour l'utiliser :
1. Copiez ce fichier et renommez-le en "user_config.py"
2. Modifiez les valeurs selon votre configuration personnelle
3. Le fichier user_config.py ne sera pas commité (ignoré par git)

"""

# ===========================
# Configuration Utilisateur
# ===========================

# Nom d'utilisateur actuel - À modifier selon votre pseudo Dofus
CURRENT_USER = "KeTaBi"


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

# Coordonnées obsolètes (non utilisées, conservées pour compatibilité)
COORDINATES_SCREENSHOT_ZONE_TOP_LEFT = (175, 326)
COORDINATES_SCREENSHOT_ZONE_BOTTOM_RIGHT = (403, 361)
COORDINATES_SCREENSHOT_ZONE_PRICE_ONLY_TOP_LEFT = (264, 346)
COORDINATES_SCREENSHOT_ZONE_PRICE_ONLY_BOTTOM_RIGHT = (402, 380)


# ============================================================================
# COORDONNÉES DES QUANTITÉS ET PRIX (4 CAS SELON LE TYPE D'HDV)
# ============================================================================
# Il existe 4 cas différents selon le type d'HDV et le contexte :
# - Cas 1 : HDV Ressources avec libellé "Prix" présent
# - Cas 2 : HDV Ressources avec libellé "Prix" absent
# - Cas 3 : HDV Équipement hors panoplie
# - Cas 4 : HDV Équipement panoplie


# ────────────────────────────────────────────────────────────────────────────
# CAS 1 : HDV RESSOURCES / CONSOMMABLES / ETC. (LIBELLÉ "PRIX" PRÉSENT)
# ────────────────────────────────────────────────────────────────────────────

# Libellé "Prix" - Zone pour détecter la présence du libellé "Prix"
COORDINATES_LABEL_PRIX_TOP_LEFT = (211, 238)
COORDINATES_LABEL_PRIX_BOTTOM_RIGHT = (246, 256)

# Quantité - Zone de la quantité (x1, x10, x100, x1000)
# Note : +40 pixels verticalement pour chaque position (0, 1, 2, 3)
COORDINATES_QUANTITY_RESSOURCES_TOP_LEFT = (177, 333)
COORDINATES_QUANTITY_RESSOURCES_BOTTOM_RIGHT = (235, 356)

# Prix - Zone du prix (utilisée quand "Prix" est présent)
# Note : +40 pixels verticalement pour chaque position (0, 1, 2, 3)
COORDINATES_PRICE_ONLY_TOP_LEFT = (239, 326)
COORDINATES_PRICE_ONLY_BOTTOM_RIGHT = (401, 361)


# ────────────────────────────────────────────────────────────────────────────
# CAS 2 : HDV RESSOURCES / CONSOMMABLES / ETC. (LIBELLÉ "PRIX" ABSENT)
# ────────────────────────────────────────────────────────────────────────────

# Quantité - Zone de la quantité quand "Prix" n'est pas présent
# Note : +40 pixels verticalement pour chaque position (0, 1, 2, 3)
COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_TOP_LEFT = (176, 352)
COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_BOTTOM_RIGHT = (234, 376)

# Prix - Zone du prix quand "Prix" n'est pas présent
# Note : +40 pixels verticalement pour chaque position (0, 1, 2, 3)
COORDINATES_PRICE_ONLY_NO_PRIX_TOP_LEFT = (239, 346)
COORDINATES_PRICE_ONLY_NO_PRIX_BOTTOM_RIGHT = (402, 380)


# ────────────────────────────────────────────────────────────────────────────
# CAS 3 : HDV ÉQUIPEMENT (HORS PANOPLIE)
# ────────────────────────────────────────────────────────────────────────────

# Libellé "Panoplie" - Zone pour détecter si l'équipement est une panoplie
COORDINATES_LABEL_PANOPLIE_TOP_LEFT = (210, 278)
COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT = (283, 304)

# Quantité - Zone de la quantité pour équipement hors panoplie (doit être x1)
# Note : Position 0 uniquement (pas de décalage)
COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT = (177, 332)
COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT = (234, 355)

# Prix - Zone du prix pour équipement hors panoplie
# Note : Position 0 uniquement (pas de décalage)
# ⚠️ PARTAGE avec le Cas 1 (même coordonnées que COORDINATES_PRICE_ONLY_TOP_LEFT)
# COORDINATES_PRICE_ONLY_TOP_LEFT = (263, 326)
# COORDINATES_PRICE_ONLY_BOTTOM_RIGHT = (401, 361)


# ────────────────────────────────────────────────────────────────────────────
# CAS 4 : HDV ÉQUIPEMENT (PANOPLIE)
# ────────────────────────────────────────────────────────────────────────────

# Quantité - Zone de la quantité pour équipement panoplie (doit être x1)
# Note : Position 0 uniquement (pas de décalage)
COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT = (204, 354)
COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT = (234, 376)

# Prix - Zone du prix pour équipement panoplie
# Note : Position 0 uniquement (pas de décalage)
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
