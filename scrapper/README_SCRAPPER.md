# 🤖 Scrapper Automatique Dofus

## Vue d'ensemble

Le scrapper automatique récupère maintenant les items directement depuis l'interface Streamlit au lieu des fichiers texte. Les items et ingrédients ajoutés dans la page "Scrapper" sont automatiquement organisés par HDV et utilisés pour le scraping.

## Modifications apportées

### 1. **Nouvelle fonction dans `utils.py`**

```python
get_scrapper_items_by_hdv(data)
```

Cette fonction :
- Récupère les items et ingrédients du fichier `data/items_scrap.json`
- Combine les deux listes (items choisis + ingrédients nécessaires)
- Organise les items par HDV en fonction de leur attribut `hdv`
- Retourne un dictionnaire `{nom_hdv: [liste de noms d'items]}`

### 2. **Modification de `4_dofus_scrapper.py`**

La méthode `load_all_resources()` a été modifiée pour :
- Charger les items depuis le scrapper via `get_scrapper_items_by_hdv()`
- Ne plus dépendre des fichiers `.txt` dans le dossier `data/`
- Afficher un résumé des items chargés par HDV

### 3. **Nouveau bouton dans `pages/scrapper.py`**

Un bouton **"🤖 Lancer le scraping automatique"** a été ajouté qui :
- Affiche un résumé des items à scraper organisés par HDV
- Fournit les instructions pour lancer le script
- Indique la commande à exécuter

## Utilisation

### Étape 1 : Ajouter des items au scrapper

1. Allez sur la page **"📊 Prix des items"**
2. Sélectionnez les items que vous souhaitez scraper
3. Cliquez sur **"➕ Scrapper"**
4. Les ingrédients nécessaires seront automatiquement ajoutés

### Étape 2 : Vérifier les items à scraper

1. Allez sur la page **"🔍 Scrapper"**
2. Vérifiez les deux tableaux :
   - **Items choisis par l'utilisateur**
   - **Ingrédients nécessaires pour les crafts**
3. Cliquez sur **"🤖 Lancer le scraping automatique"** pour voir le résumé

### Étape 3 : Lancer le scraping

1. Ouvrez Dofus et connectez-vous
2. Placez votre personnage dans une zone accessible aux HDV
3. Ouvrez un terminal et exécutez :

```bash
cd scrapper
python 4_dofus_scrapper.py
```

## Organisation des HDV

Les items sont automatiquement organisés dans les catégories suivantes :

| HDV dans la BDD | Nom du fichier (ancien) | Catégorie |
|----------------|------------------------|-----------|
| Hôtel de vente de ressources | `ressources.txt` | ressources |
| Hôtel de vente d'équipements | `equipements.txt` | equipements |
| Hôtel de vente de consommables | `consommables.txt` | consommables |
| Hôtel de vente des forgemagies | `forgemagies.txt` | forgemagies |
| Hôtel de vente de créatures | `creatures.txt` | creatures |
| Hôtel de vente des cosmétiques | `cosmetiques.txt` | cosmetiques |
| Hôtel de vente des âmes | `ames.txt` | ames |

## Structure du fichier `items_scrap.json`

```json
{
  "items": [44, 49],
  "ingredients": [303, 377, 1673, 16512]
}
```

- **items** : IDs des items choisis manuellement par l'utilisateur
- **ingredients** : IDs des ingrédients nécessaires pour crafter les items (générés automatiquement)

## Avantages de cette approche

✅ **Plus besoin de fichiers texte** : Tout est géré via l'interface Streamlit

✅ **Extraction automatique des ingrédients** : Les ingrédients nécessaires sont automatiquement détectés de manière récursive

✅ **Organisation automatique par HDV** : Les items sont classés selon leur HDV de vente

✅ **Interface conviviale** : Visualisation claire des items à scraper avec filtres et tableaux

✅ **Liste unique** : Pas de doublons, chaque item n'est scrapé qu'une fois

## Notes techniques

- La fonction `load_resources()` dans `4_dofus_scrapper.py` est marquée comme **DEPRECATED** mais conservée pour compatibilité
- Les fichiers `.txt` dans `data/` ne sont plus utilisés mais peuvent être conservés comme backup
- Le scraping fonctionne de la même manière qu'avant, seule la source des données change
