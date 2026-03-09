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

# Coordonnée barre de recherche de l'HDV (pour HDV Ressources, Consommables, etc.)
COORDINATES_SEARCH_BOX_TOP_LEFT = (700, 318) # (x ; y)
COORDINATES_SEARCH_BOX_BOTTOM_RIGHT = (899, 338)

# Coordonnée barre de recherche pour HDV Équipements et HDV Cosmétiques
COORDINATES_SEARCH_BOX_EQUIPEMENT_TOP_LEFT = (700, 318)  # (x ; y) - À CALIBRER
COORDINATES_SEARCH_BOX_EQUIPEMENT_BOTTOM_RIGHT = (899, 338)  # À CALIBRER

# Coordonnées du filtre niveau minimum
COORDINATES_INPUT_MIN_LVL_TOP_LEFT = (736, 398)
COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT = (788, 422)

# Coordonnées du filtre niveau maximum
COORDINATES_INPUT_MAX_LVL_TOP_LEFT = (835, 400)
COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT = (887, 422)

# Coordonnée du nom de la ressource
COORDINATES_RESSOURCE_NAME_TOP_LEFT = (1047, 358)
COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT = (1295, 435)

# Coordonnée de la zone de l'item (clique dessous pour l'ouvrir et voir le prix des items) de l'HDV
COORDINATES_RESOURCE_ITEM_TOP_LEFT = (993, 358)
COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT = (1527, 435)

# ============================================================================
# COORDONNÉES DES QUANTITÉS ET PRIX (3 CAS SELON LE TYPE D'HDV)
# ============================================================================
# La logique est unifiée : coordonnées de base (libellé "Prix" absent) +
# décalage Y de PRIX_Y_OFFSET si le libellé "Prix" est détecté à l'écran.
# - Cas 1 : HDV Ressources (coords NO_PRIX + offset si Prix présent)
# - Cas 2 : HDV Équipement hors panoplie (+ offset si Prix présent)
# - Cas 3 : HDV Équipement panoplie (+ offset si Prix présent)

# ────────────────────────────────────────────────────────────────────────────
# DÉTECTION DU LIBELLÉ "PRIX"
# ────────────────────────────────────────────────────────────────────────────

# Zone de détection du libellé "Prix" (commun à tous les HDV)
COORDINATES_LABEL_PRIX_TOP_LEFT = (364, 339)
COORDINATES_LABEL_PRIX_BOTTOM_RIGHT = (404, 361)

# ────────────────────────────────────────────────────────────────────────────
# CAS 1 : HDV RESSOURCES / CONSOMMABLES / ETC.
# ────────────────────────────────────────────────────────────────────────────

# Zone de la quantité (x1, x10, x100, x1000) — coordonnées de base
# Si libellé "Prix" présent : ajouter PRIX_Y_OFFSET aux coordonnées Y
# Décalage vertical : + PRICE_LINE_HEIGHT px par position (0, 1, 2, 3)
COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_TOP_LEFT = (322, 476)
COORDINATES_QUANTITY_RESSOURCES_NO_PRIX_BOTTOM_RIGHT = (387, 498)

# Zone du prix — coordonnées de base
# Si libellé "Prix" présent : ajouter PRIX_Y_OFFSET aux coordonnées Y
# Décalage vertical : + PRICE_LINE_HEIGHT px par position (0, 1, 2, 3)
COORDINATES_PRICE_ONLY_NO_PRIX_TOP_LEFT = (409, 472)
COORDINATES_PRICE_ONLY_NO_PRIX_BOTTOM_RIGHT = (597, 503)


# ────────────────────────────────────────────────────────────────────────────
# CAS 2 : HDV ÉQUIPEMENT (HORS PANOPLIE)
# Si libellé "Prix" présent : ajouter PRIX_Y_OFFSET aux coordonnées Y
# ────────────────────────────────────────────────────────────────────────────

# Zone de détection du libellé "Panoplie"
COORDINATES_LABEL_PANOPLIE_TOP_LEFT = (316, 395)
COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT = (717, 420)

# Zone de la quantité pour équipement hors panoplie (toujours x1, position 0)
COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT = (275, 465)
COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT = (342, 490)

# Zone du prix pour équipement hors panoplie (position 0 uniquement)
COORDINATES_PRICE_ONLY_EQUIPEMENT_TOP_LEFT = (409, 472)   # À CALIBRER
COORDINATES_PRICE_ONLY_EQUIPEMENT_BOTTOM_RIGHT = (597, 503)  # À CALIBRER


# ────────────────────────────────────────────────────────────────────────────
# CAS 3 : HDV ÉQUIPEMENT (PANOPLIE)
# Si libellé "Prix" présent : ajouter PRIX_Y_OFFSET aux coordonnées Y
# ────────────────────────────────────────────────────────────────────────────

# Zone de la quantité pour équipement panoplie (toujours x1, position 0)
COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT = (274, 486)
COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT = (342, 510)

# Zone du prix pour équipement panoplie (position 0 uniquement)
COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT = (377, 476)
COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT = (552, 519)

# Bouton pour annuler la recherche (pour HDV Ressources, Consommables, etc.)
COORDINATES_CANCEL_SEARCH_TOP_LEFT = (917, 320)
COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT = (928, 329)

# Bouton pour annuler la recherche pour HDV Équipements et HDV Cosmétiques
COORDINATES_CANCEL_SEARCH_EQUIPEMENT_TOP_LEFT = (917, 320)  # À CALIBRER
COORDINATES_CANCEL_SEARCH_EQUIPEMENT_BOTTOM_RIGHT = (928, 329)  # À CALIBRER

# Coordonnées de l'input du tchat textuel
COORDINATES_CHAT_TOP_LEFT = (56, 1410)
COORDINATES_CHAT_BOTTOM_RIGHT = (334, 1433)

# Coordonnées des bâtiments HDV (spécifiques à votre position dans le jeu)
COORDINATES_HDV_EQUIPEMENT_TOP_LEFT = (1451, 828)
COORDINATES_HDV_EQUIPEMENT_BOTTOM_RIGHT = (1617, 954)

COORDINATES_HDV_RESSOURCES_TOP_LEFT = (1582, 335)
COORDINATES_HDV_RESSOURCES_BOTTOM_RIGHT = (1714, 416)

COORDINATES_HDV_CONSOMMABLES_TOP_LEFT = (1519, 729)
COORDINATES_HDV_CONSOMMABLES_BOTTOM_RIGHT = (1660, 831)

COORDINATES_HDV_FORGEMAGIE_TOP_LEFT = (1187, 433)
COORDINATES_HDV_FORGEMAGIE_BOTTOM_RIGHT = (1325, 622)

COORDINATES_HDV_CREATURES_TOP_LEFT = (1199, 329)
COORDINATES_HDV_CREATURES_BOTTOM_RIGHT = (1335, 425)

COORDINATES_HDV_COSMETIQUES_TOP_LEFT = (0, 0)
COORDINATES_HDV_COSMETIQUES_BOTTOM_RIGHT = (0, 0)

COORDINATES_HDV_AMES_TOP_LEFT = (0, 0)
COORDINATES_HDV_AMES_BOTTOM_RIGHT = (0, 0)

# Coordonnées du premier mot du message post /travel (pour détecter "Un" ou autre)
COORDINATES_MSG_POST_TRAVEL_TOP_LEFT = (900, 600)
COORDINATES_MSG_POST_TRAVEL_BOTTOM_RIGHT = (1100, 800)

# Coordonnées de l'affichage des coordonnées in game
COORDINATES_COORDS_TOP_LEFT = (0, 0)
COORDINATES_COORDS_BOTTOM_RIGHT = (0, 0)

# Coordonnées du Bouton pour quitter l'HDV
COORDINATES_QUIT_HDV_TOP_LEFT = (1677, 234)
COORDINATES_QUIT_HDV_BOTTOM_RIGHT = (1691, 247)


# ===========================
# Hauteurs des éléments de l'interface
# ===========================

# Hauteur d'un item dans la liste de l'HDV (pour passer d'un item au suivant)
ITEM_HEIGHT = 73

# Hauteur entre deux lignes de prix/quantité (x1 → x10 → x100 → x1000)
PRICE_LINE_HEIGHT = 40

# Décalage vertical appliqué quand le libellé "Prix" est présent dans l'interface HDV
PRIX_Y_OFFSET = 10  # À CALIBRER


# # Coordonnées sur la map dofus des HDVs (Pandala)
# COORDINATES_MAP_HDV_RESSOURCES = (21, -28)
# COORDINATES_MAP_HDV_EQUIPEMENT = (19, -29)
# COORDINATES_MAP_HDV_CONSOMMABLES = (21, -29)
# COORDINATES_MAP_HDV_FORGEMAGIE = (17, -29)
# COORDINATES_MAP_HDV_CREATURES = (18, -29)
# COORDINATES_MAP_HDV_COSMETIQUES = (19, -27)
# COORDINATES_MAP_HDV_AMES = (0, 0)


# Coordonnées sur la map dofus des HDVs (Brakmar)
COORDINATES_MAP_HDV_RESSOURCES = (-26, 33)
COORDINATES_MAP_HDV_EQUIPEMENT = (-28, 35)
COORDINATES_MAP_HDV_CONSOMMABLES = (-23, 36)
COORDINATES_MAP_HDV_FORGEMAGIE = (-26, 38)
COORDINATES_MAP_HDV_CREATURES = (-25, 38)
COORDINATES_MAP_HDV_COSMETIQUES = (-29, 38)
COORDINATES_MAP_HDV_AMES = (-25, 36)
