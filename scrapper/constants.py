import os
import sys

# Ajouter le dossier parent au path pour importer user_config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des configurations utilisateur depuis user_config.py
from user_config import (
    TESSERAT_PATH,
    COORDINATES_SEARCH_BOX_TOP_LEFT,
    COORDINATES_SEARCH_BOX_BOTTOM_RIGHT,
    COORDINATES_INPUT_MIN_LVL_TOP_LEFT,
    COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT,
    COORDINATES_INPUT_MAX_LVL_TOP_LEFT,
    COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT,
    COORDINATES_RESSOURCE_NAME_TOP_LEFT,
    COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT,
    COORDINATES_RESOURCE_ITEM_TOP_LEFT,
    COORDINATES_RESOURCE_ITEM_BOTTOM_RIGHT,
    COORDINATES_SCREENSHOT_ZONE_TOP_LEFT,
    COORDINATES_SCREENSHOT_ZONE_BOTTOM_RIGHT,
    COORDINATES_SCREENSHOT_ZONE_PRICE_ONLY_TOP_LEFT,
    COORDINATES_SCREENSHOT_ZONE_PRICE_ONLY_BOTTOM_RIGHT,
    COORDINATES_QUANTITY_RESSOURCES_TOP_LEFT,
    COORDINATES_QUANTITY_RESSOURCES_BOTTOM_RIGHT,
    COORDINATES_LABEL_PANOPLIE_TOP_LEFT,
    COORDINATES_LABEL_PANOPLIE_BOTTOM_RIGHT,
    COORDINATES_QUANTITY_EQUIPEMENT_TOP_LEFT,
    COORDINATES_QUANTITY_EQUIPEMENT_BOTTOM_RIGHT,
    COORDINATES_PRICE_ONLY_TOP_LEFT,
    COORDINATES_PRICE_ONLY_BOTTOM_RIGHT,
    COORDINATES_QUANTITY_PANOPLIE_TOP_LEFT,
    COORDINATES_QUANTITY_PANOPLIE_BOTTOM_RIGHT,
    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT,
    COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT,
    COORDINATES_CANCEL_SEARCH_TOP_LEFT,
    COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT,
    COORDINATES_CHAT_TOP_LEFT,
    COORDINATES_CHAT_BOTTOM_RIGHT,
    COORDINATES_HDV_RESSOURCES_TOP_LEFT,
    COORDINATES_HDV_RESSOURCES_BOTTOM_RIGHT,
    COORDINATES_HDV_EQUIPEMENT_TOP_LEFT,
    COORDINATES_HDV_EQUIPEMENT_BOTTOM_RIGHT,
    COORDINATES_HDV_CONSOMMABLES_TOP_LEFT,
    COORDINATES_HDV_CONSOMMABLES_BOTTOM_RIGHT,
    COORDINATES_HDV_FORGEMAGIE_TOP_LEFT,
    COORDINATES_HDV_FORGEMAGIE_BOTTOM_RIGHT,
    COORDINATES_HDV_CREATURES_TOP_LEFT,
    COORDINATES_HDV_CREATURES_BOTTOM_RIGHT,
    COORDINATES_HDV_COSMETIQUES_TOP_LEFT,
    COORDINATES_HDV_COSMETIQUES_BOTTOM_RIGHT,
    COORDINATES_HDV_AMES_TOP_LEFT,
    COORDINATES_HDV_AMES_BOTTOM_RIGHT,
    COORDINATES_MSG_POST_TRAVEL_TOP_LEFT,
    COORDINATES_MSG_POST_TRAVEL_BOTTOM_RIGHT,
    COORDINATES_COORDS_TOP_LEFT,
    COORDINATES_COORDS_BOTTOM_RIGHT,
    COORDINATES_CONFIRM_TOP_LEFT,
    COORDINATES_CONFIRM_BOTTOM_RIGHT,
    COORDINATES_QUIT_HDV_TOP_LEFT,
    COORDINATES_QUIT_HDV_BOTTOM_RIGHT,
)

# Configuration Google Drive
GOOGLE_DRIVE_FILE_ID = '1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu'
# Chemin absolu vers le fichier Service Account (depuis la racine du projet)
GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'credentials',
    'service_account.json'
)

# Path : resources.txt
LIST_RESOURCES_PATH = "data/ressources.txt"

# Path : prices.json
PRICES_PATH = "Scraping_HDV/prices.json"

# Path : dossier contenant les screen
# FOLDER_IMAGE_PATH = "../screenshoots_tmp/"

FOLDER_IMAGE_PATH = os.path.join("screenshoots_tmp")


# Configuration PyAutoGUI
PYAUTOGUI_FAILSAFE = True   # Sécurité : déplacer la souris dans le coin supérieur gauche arrêtera le script (donc éviter de mettre sur FALSE)
PYAUTOGUI_PAUSE = 0.1       # Petit délai entre les actions

# NOTE : Toutes les coordonnées spécifiques à l'utilisateur sont maintenant importées depuis user_config.py
# Voir les imports en haut du fichier

# Coordonnées sur la map dofus des HDVs (Pandala)
COORDINATES_MAP_HDV_RESSOURCES = (21, -28)
COORDINATES_MAP_HDV_EQUIPEMENT = (19, -29)
COORDINATES_MAP_HDV_CONSOMMABLES = (21, -29)
COORDINATES_MAP_HDV_FORGEMAGIE = (17, -29)
COORDINATES_MAP_HDV_CREATURES = (18, -29)
COORDINATES_MAP_HDV_COSMETIQUES = (19, -27)
COORDINATES_MAP_HDV_AMES = (0, 0)

# NOTE : COORDINATES_CONFIRM_* et COORDINATES_QUIT_HDV_* sont importés depuis user_config.py


# Liste par défaut à la création du fichier contenant les ressources
LIST_DEFAULT_RESOURCES = [
    "# Liste des ressources à analyser",
    "# Une ressource par ligne",
    "# Les lignes commençant par # sont ignorées",
    "",
    "Pic de Malepik",
    "Artefact Pandawushu Vent",
    "Rouge à lèvres de Belladone",
]

# Caractère de commentaire dans le fichier contenant les ressources
RESOURCES_FILE_COMMENT_CHARACTER = '#'

# Temps avant le lancement du scraping
TIME_BEFORE_SCRAPING = 3

# TODO : ajouter tout les temps d'attente entre les actions

# TODO : ajouter les paramètres de déplacement de la souris (antibot)

# --- Ressources --- #
L_SUPERTYPES_RESSOURCES = [
    "Ressource"
]
L_TYPES_RESSOURCES = [
    "Aile", "Alliage", "Bois", "Bourgeon", "Carapace", "Carte", "Champignon", "Clef",
    "Coquille", "Cuir", "Céréale", "Essence de gardien de donjon", "Fleur", "Fragment de carte",
    "Fruit", "Galet", "Gelée", "Graine", "Huile", "Laine", "Liquide", "Légume",
    "Matériel d'alchimie", "Matériel d'exploration", "Minerai", "Métaria", "Nowel",
    "Os", "Patte", "Peau", "Pierre brute", "Pierre précieuse", "Planche",
    "Plante", "Plume", "Poil", "Poudre", "Queue", "Racine", "Ressource de Percepteur",
    "Ressource de combat", "Ressource des Anomalies Temporelles", "Préparation",
    "Ressource des Songes", "Ressource diverse", "Oreille", "Poisson",
    "Sève", "Substrat", "Teinture", "Viande", "Écorce", "Étoffe", "Œil", "Œuf", "Vêtement"
]

# --- Équipement --- #
L_SUPERTYPES_EQUIPEMENTS = [
    "Arme", "Amulette", "Anneau", "Bottes", "Ceinture", "Chapeau", "Cape", "Dofus / Trophée",
    "Bouclier", "Compagnon", "Équipement de percepteur"
]
L_TYPES_EQUIPEMENTS = [
    "Amulette", "Anneau", "Arc", "Baguette", "Bottes", "Bouclier",
    "Cape", "Ceinture", "Chapeau", "Dague", "Épée", "Hache",
    "Lance", "Marteau", "Pelle", "Bâton", "Poignards de Percepteur", 
    "Cuirasses de Percepteur", "Tunique de Percepteur", 
    "Coffres de Percepteur", "Sacoches de Percepteur", "Trophée", "Prysmaradite", 
    "Fers de Percepteur", "Bannière de Percepteur",
]
L_TYPES_FORGERON = [
    "Dague",
    "Épée",
    "Faux",
    "Hache",
    "Lance",
    "Marteau",
    "Pelle",
    "Pioche",
    
    
]
L_TYPES_TAILLEUR = [
    "Cape",
    "Chapeau"
]

L_TYPES_CORDONNIER = [
    "Bottes",
    "Ceinture"
]



# --- Créatures --- #
L_SUPERTYPES_CREATURES = [
    "Certificat de monture",
    "Equipement de monture",
    "Familier"
]
L_TYPES_CREATURES = [
    "Familier", "Certificat de Dragodinde", "Objet d'élevage", "Caution",
    "Nourriture pour familier", "Harnachements de Muldo"
]

# --- Forgemagie --- #
L_TYPES_FORGEMAGIE = [
    "Gravure de forgemagie", "Potion de forgemagie", "Rune astrale",
    "Rune de forgemagie", "Rune de transcendance", "Orbe de forgemagie"
]

# --- Consommables --- #
L_SUPERTYPES_CONSOMMABLES = [
    "Consommable",
    "Consommables de combat"
]
L_TYPES_CONSOMMABLES = [
    "Bière", "Boisson", "Cadeau", "Pain", "Poisson comestible",
    "Potion", "Potion de téléportation", "Potion de conquête",
    "Friandise", "Viande comestible", "Fée d'artifice",
    "Filet de capture", "Objet utilisable", "Prisme", "Éklâme"
]

# --- Cosmétiques --- #
L_SUPERTYPES_COSMETIQUES = [
    "Cosmétiques",
    "Costume"
]
L_TYPES_COSMETIQUES = [
    "Bouclier d'apparat", "Chapeau d'apparat", "Cape d'apparat", 
    "Épaulières", "Costume"
]

# --- âmes --- #
L_TYPES_AMES = [
    "Pierre d'âme", "Pierre d'âme spéciale non transformée"
]

# ---  items de de quêtes --- #
L_TYPES_QUETES = [
    "Alignement", "Archipel de Valonia", "Astrub", "Atoll des Possédés", "Bonta & Brakmar",
    "Cania", "Dimensions Divines", "Eliocalypse", "Incarnam", "Krosmoz", "Pandala", 
    "Quêtes principales", "Royaume d'Amakna", "Sufokia", "Événements", "Île de Frigost",
    "Île de Moon", "Île de Nowel", "Île de Pwâk", "Îles des Wabbits", "Pierre d'âme spéciale",
    "Idoles de Quêtes"
]






# data["type"]["name"]["fr"]
# https://api.dofusdb.fr/items?id=44&id=55

L_SUPERTYPES = ["Arme", "Amulette", "Anneau", "Bottes", "Ceinture", "Ressource", "Consommable",
"Consommables de combat", "Chapeau", "Cape", "Dofus / Trophée",
"Objet de quête", "Cosmétiques", "Familier", "Mutation", "Nourriture",
"Bénédiction", "Malédiction", "Bonus de jeu de rôle", "Suiveur", "Bouclier",
"Fantôme de familier", "Compagnon", "Equipement de monture", "Costume",
"Certificat", "Équipement de percepteur"]

L_TYPES = ["Épée", "Amulette", "Arc", "Dague", "Anneau", "Bottes", "Baguette", "Bâton",
 "Marteau", "Pelle", "Ceinture", "Pierre brute", "Ressources diverses",
 "Friandise", "Potion", "Poudre", "Graine", "Céréale", "Champignon", "Poil",
 "Plume", "Bois", "Cuir", "Os", "Fleur", "Aile", "Coquille", "Liquide", "Minerai",
 "Pierre précieuse", "Bière", "Oreille", "Légume", "Peau", "Patte", "Œuf",
 "Gelée", "Vêtement", "Plante", "Fruit", "Laine", "Ressources obsolètes",
 "Huile", "Étoffe", "Ressource de combat", "Racine", "Queue", "Hache", "Pain",
 "Potion de téléportation", "Filet de capture", "Poisson", "Chapeau", "Cape",
 "Parchemin d'expérience", "Parchemin de caractéristique", "Bourse", "Dofus",
 "Parchemin de sortilège", "Alliage", "Faux", "Forêt Maléfique", "Divers",
 "Îles des Wabbits", "Clef", "Île de Moon", "Chapeau d'apparat",
 "Potion de forgemagie", "Lance", "Pioche", "Matériel d'alchimie",
 "Préparation", "Outil", "Document", "Rune de forgemagie", "Métaria", "Écorce",
 "Bourgeon", "Parchemin d'attitude", "Teinture", "Familier",
 "Objet de Mutation", "Nourriture boost", "Bénédiction", "Malédiction",
 "Alignement", "Objet de dons", "Cania", "Poisson comestible",
 "Viande primitive", "Œil", "Roleplay Buffs", "Personnage suiveur",
 "Objet de mission", "Fée d'artifice", "Carapace", "Cape d'apparat",
 "Substrat", "Peluche", "Viande comestible", "Astrub", "Boisson",
 "Quêtes principales", "Cadeau", "Pierre d'âme pleine", "Pandala", "Bouclier",
 "Objet d'élevage", "Objet utilisable", "Certificat de Dragodinde",
 "Montagne des Koalaks", "Sac de ressources", "Objet d'apparat divers",
 "Familier d'apparat", "Ballon", "Royaume d'Amakna",
 "Camps des Bworks et des Gobelins", "Arme d'apparat", "Prisme",
 "Objet vivant", "Île de Nowel", "Bouclier d'apparat", "Pierre d'âme",
 "Île d'Otomaï", "Jetons", "Coffre", "Krosmoz", "Événements", "Île de Frigost",
 "Archipel de Vulkania", "Montilier", "Souvenir", "Trophée", "Galet",
 "Incarnam", "Nowel", "Emballage", "Sufokia", "Almanax", "Figurine",
 "Rabmablague", "Potion de conquête", "Mimibiote", "Justiciers",
 "Essence de gardien de donjon", "Compagnon", "Dimensions Divines", "Carte",
 "Fragment de carte", "Boîte de fragments", "Montilier d'apparat", "Planche",
 "Viande", "Pierre magique", "Conteneur", "Sève", "Parchemin d'émoticônes",
 "Orbe de forgemagie", "Harnachements de Dragodinde", "Certificat de Muldo",
 "Matériel d'exploration", "Parchemin de titre", "Caution",
 "Harnachements de Muldo", "Saharach", "Costume", "Nimotopia", "Sidimote",
 "Objet invisible", "Tours de la Fratrie", "Certificat de Volkorne",
 "Harnachements de Volkorne", "Nourriture pour familier",
 "Rune de transcendance", "Ressources des Songes", "Potion d'attitude",
 "Île de Pwâk", "Ressources des Anomalies Temporelles",
 "Archipel des Écailles", "Prysmaradite", "Popoche de Havre-Sac",
 "Épaulières", "Rune astrale", "Eliocalypse", "Parchemin d'ornement",
 "Temporis", "Haïku", "Mots de haïku", "Ressources de Temporis",
 "Ailes d'apparat", "Objet utilisable de Temporis", "Atoll des Possédés",
 "Cauchemar des Ravageurs", "Bonta & Brakmar", "Bouataklône",
 "Gravure de forgemagie", "Archipel de Valonia", "Expéditions",
 "Ressources de Percepteur", "Fers de Percepteur", "Tunique de Percepteur",
 "Bannière de Percepteur", "Poignards de Percepteur",
 "Cuirasses de Percepteur", "Coffres de Percepteur",
 "Sacoches de Percepteur", "Potion de monture", "Idoles de Quêtes",
 "Foire du Trool", "Monture domptée", "Tatouage de la Foire du Trool",
 "Panoplie d'apparat", "Pierre d'âme spéciale",
 "Pierre d'âme spéciale pleine", "Pierre d'âme spéciale non transformée"]

"https://api.dofusdb.fr/recipes?result.isSaleable=true&result.type.name.fr=Bois"
"https://api.dofusdb.fr/recipes?result.isSaleable=true"