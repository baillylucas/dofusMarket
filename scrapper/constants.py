import os

# Configuration Google Drive
GOOGLE_DRIVE_FILE_ID = '1WyWt7GAiJWg7HRJAN1wxY9ivNO9A_0Wu'
# Chemin absolu vers le fichier Service Account (depuis la racine du projet)
GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'credentials',
    'service_account.json'
)

# Configuration Tesseract-OCR
TESSERAT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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

# Coordonnée barre de recherche de l'HDV
COORDINATES_SEARCH_BOX_TOP_LEFT =  (580, 241) # (x ; y)
COORDINATES_SEARCH_BOX_BOTTOM_RIGHT = (756, 265)

# Coordonnées du filtre niveau minimum
COORDINATES_INPUT_MIN_LVL_TOP_LEFT = (617, 317)
COORDINATES_INPUT_MIN_LVL_BOTTOM_RIGHT = (663, 339)

# Coordonnées du filtre niveau maximum
COORDINATES_INPUT_MAX_LVL_TOP_LEFT = (706, 319)
COORDINATES_INPUT_MAX_LVL_BOTTOM_RIGHT = (752, 339)

# Coordonnée du nom de la ressource
COORDINATES_RESSOURCE_NAME_TOP_LEFT =  (893, 282)
COORDINATES_RESSOURCE_NAME_BOTTOM_RIGHT =  (1111, 349)

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

# Coordonnée de la zone de screen (uniquement le prix) pour les équipempents ne faisant pas parti d'une panoplie, dans l'HDV equipement
COORDINATES_PRICE_ONLY_TOP_LEFT = (263, 326)
COORDINATES_PRICE_ONLY_BOTTOM_RIGHT = (401, 361)

# Coordonnée de la zone de screen (uniquement le prix) pour les équipempents faisant parti d'une panoplie, dans l'HDV equipement
COORDINATES_PRICE_ONLY_FOR_PANOPLIE_TOP_LEFT = (266, 347)
COORDINATES_PRICE_ONLY_FOR_PANOPLIE_BOTTOM_RIGHT = (401, 381)

# # Coordonnées de la zone de prix pour les items de l'HDV equipement (même emplacement pour tout hdv depuis récente maj)
# COORDINATES_SCREENSHOT_EQUIPEMENT_ZONE_TOP_LEFT = (176, 321)
# COORDINATES_SCREENSHOT_EQUIPEMENT_ZONE_BOTTOM_RIGHT = (401, 349)

COORDINATES_CANCEL_SEARCH_TOP_LEFT = (737, 246)
COORDINATES_CANCEL_SEARCH_BOTTOM_RIGHT = (747, 256)

# Coordonnées de l'input du tchat textuel 
COORDINATES_CHAT_TOP_LEFT = (35, 1054)
COORDINATES_CHAT_BOTTOM_RIGHT = (288, 1073)

# Coordonnées des batiments HDVGumizes
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

# Coordonnées sur la map dofus des HDVs (Pandala)
COORDINATES_MAP_HDV_RESSOURCES = (21, -28)
COORDINATES_MAP_HDV_EQUIPEMENT = (19, -29)
COORDINATES_MAP_HDV_CONSOMMABLES = (21, -29)
COORDINATES_MAP_HDV_FORGEMAGIE = (17, -29)
COORDINATES_MAP_HDV_CREATURES = (18, -29)
COORDINATES_MAP_HDV_COSMETIQUES = (19, -27)
COORDINATES_MAP_HDV_AMES = (0, 0)

# Coordonnées du Bouton de Confirmation d'un /travel
COORDINATES_CONFIRM_TOP_LEFT = (800, 585)
COORDINATES_CONFIRM_BOTTOM_RIGHT = (940, 593)

# Coordonnées du Bouton pour quitte l'HDV
COORDINATES_QUIT_HDV_TOP_LEFT = (1327, 153) 
COORDINATES_QUIT_HDV_BOTTOM_RIGHT =  (1340, 164)


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
    "Épée",
    "Dague",
    "Marteau",
    "Pelle",
    "Hache",
    "Faux",
    "Pioche",
    "Lance"
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