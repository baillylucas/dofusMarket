import json

def get_latest_price_date(item_data: dict) -> str:
    """Retourne la date la plus récente entre prix_hdv et cout_craft."""
    latest_date = None
    
    # Vérifier les dates dans prix_hdv
    if item_data.get('prix_hdv'):
        prix_dates = item_data['prix_hdv'].keys()
        if prix_dates:
            latest_prix = max(prix_dates)
            latest_date = latest_prix
    
    # Vérifier les dates dans cout_craft
    if item_data.get('cout_craft'):
        craft_dates = item_data['cout_craft'].keys()
        if craft_dates:
            latest_craft = max(craft_dates)
            if not latest_date or latest_craft > latest_date:
                latest_date = latest_craft
    
    return latest_date

def get_optimal_price_for_quantity(item_data: dict, quantity: int, latest_date: str, debug_info: dict = None) -> int:
    """
    Calcule le prix optimal pour une quantité donnée en utilisant uniquement prix_hdv.
    Retourne un entier (le prix total) ou -1 si impossible à calculer.
    """
    # Récupérer uniquement les prix HDV
    prix_hdv = item_data.get('prix_hdv', {}).get(latest_date, {})
    
    # Créer un dictionnaire des prix totaux pour chaque quantité disponible
    prices = {}
    for qty in ['1', '10', '100', '1000']:
        # Vérifier que le prix existe ET n'est pas None
        if qty in prix_hdv and prix_hdv[qty] is not None:
            prices[int(qty)] = prix_hdv[qty]  # Garder le prix total en entier
    
    if debug_info is not None:
        debug_info['available_prices'] = prices.copy()
    
    if not prices:
        if debug_info is not None:
            debug_info['error'] = 'Aucun prix HDV disponible'
        return -1
    
    # Calculer le coût optimal
    total_cost = 0
    remaining_qty = quantity
    
    # Utiliser d'abord les plus grandes quantités si on en a besoin ET si c'est avantageux
    for qty in sorted(prices.keys(), reverse=True):
        # Vérifier si on a besoin d'au moins cette quantité
        if remaining_qty >= qty:
            # Récupérer les prix des quantités inférieures
            lower_prices = [prices.get(k, float('inf')) for k in prices if k < qty]
            
            # Si pas de prix inférieurs disponibles, utiliser ce prix
            if not lower_prices or prices[qty] <= min(lower_prices):
                # Combien de fois peut-on utiliser cette quantité ?
                use_count = remaining_qty // qty
                if use_count > 0:
                    total_cost += prices[qty] * qty * use_count
                    remaining_qty -= qty * use_count
    
    # Utiliser les plus petites quantités pour le reste
    if remaining_qty > 0:
        # Trouver la plus petite quantité disponible qui peut couvrir le reste
        available_quantities = sorted(prices.keys())
        
        # Chercher la quantité minimale qui couvre remaining_qty
        best_option = None
        best_cost = float('inf')
        
        for qty in available_quantities:
            # Coût si on achète cette quantité (même si c'est plus que nécessaire)
            cost = prices[qty] * qty
            if cost < best_cost:
                best_cost = cost
                best_option = qty
        
        if best_option is not None:
            total_cost += best_cost
        else:
            if debug_info is not None:
                debug_info['error'] = 'Aucune option disponible pour le reste'
            return float('inf')
    
    return total_cost

def update_crafting_costs(data: dict, debug_items: set = None, processed_items=None) -> None:
    """Met à jour les coûts de craft de manière récursive."""
    if processed_items is None:
        processed_items = set()
    
    # Compteurs pour les statistiques (uniquement pour les items à debugger)
    items_updated = 0
    items_skipped = 0
    items_with_missing_ingredients = []
    
    # Nouvelles quantités à calculer
    MULTIPLIERS = [1, 2, 5, 10, 20, 50, 100]
    
    def process_item(item_id):
        nonlocal items_updated, items_skipped
        
        if item_id in processed_items:
            return
        
        item_data = data[str(item_id)]
        item_name = item_data.get('name', 'Sans nom')
        is_debug_item = debug_items and item_name in debug_items
        
        if not item_data.get('is_craft') or not item_data.get('ingredients'):
            processed_items.add(item_id)
            return
        
        # Traiter d'abord tous les ingrédients
        missing_prices = False
        missing_ingredients_list = []
        latest_date = None  # Pour stocker la date la plus récente parmi tous les ingrédients
        
        for ingredient in item_data['ingredients']:
            ing_id = ingredient['id']
            if ing_id not in processed_items and str(ing_id) in data:
                process_item(ing_id)
            
            # Vérifier si l'ingrédient existe
            ing_data = data.get(str(ing_id))
            if not ing_data:
                missing_prices = True
                if is_debug_item:
                    missing_ingredients_list.append(f"ID {ing_id} (non trouvé)")
                continue
            
            # Mettre à jour la date la plus récente
            ing_latest = get_latest_price_date(ing_data)
            if ing_latest:
                if not latest_date or ing_latest > latest_date:
                    latest_date = ing_latest
            else:
                # On ne bloque plus si un ingrédient n'a pas de prix
                # On continuera avec les autres ingrédients
                if is_debug_item:
                    missing_ingredients_list.append(f"ID {ing_id} - {ing_data.get('name', 'Sans nom')} (pas de prix)")
        
        # On ne skip plus automatiquement si missing_prices
        # On essaie quand même de calculer avec ce qu'on a
        
        if latest_date:
            # Calculer les coûts pour différentes quantités
            costs = {}
            failed_multipliers = []
            
            # DEBUG: Détails pour comprendre les échecs
            debug_details = {}
            
            for multiplier in MULTIPLIERS:
                total_cost = 0
                multiplier_debug = {
                    'multiplier': multiplier,
                    'ingredients': []
                }
                
                for ingredient in item_data['ingredients']:
                    ing_id = str(ingredient['id'])
                    ing_data = data[ing_id]
                    ing_name = ing_data.get('name', 'Sans nom')
                    
                    qty_needed = ingredient['quantity'] * multiplier
                    # Utiliser la date la plus récente de chaque ingrédient individuellement
                    ing_latest = get_latest_price_date(ing_data)
                    
                    ingredient_debug = {
                        'id': ing_id,
                        'name': ing_name,
                        'qty_needed': qty_needed,
                        'has_date': ing_latest is not None
                    }
                    
                    if not ing_latest:
                        # Si pas de date pour cet ingrédient, on ne peut pas calculer
                        ingredient_debug['error'] = 'Pas de date de prix'
                        total_cost = float('inf')
                        multiplier_debug['ingredients'].append(ingredient_debug)
                        break
                    
                    ingredient_debug['latest_date'] = ing_latest
                    price_debug = {}
                    ing_cost = get_optimal_price_for_quantity(ing_data, qty_needed, ing_latest, price_debug)
                    ingredient_debug['price_calculation'] = price_debug
                    ingredient_debug['cost'] = ing_cost
                    
                    if ing_cost == float('inf'):
                        ingredient_debug['error'] = 'Coût infini'
                        total_cost = float('inf')
                        multiplier_debug['ingredients'].append(ingredient_debug)
                        break
                    
                    total_cost += ing_cost
                    multiplier_debug['ingredients'].append(ingredient_debug)
                
                multiplier_debug['total_cost'] = total_cost
                multiplier_debug['success'] = total_cost != float('inf')
                debug_details[multiplier] = multiplier_debug
                
                if total_cost != float('inf'):
                    costs[str(multiplier)] = int(total_cost)  # Conversion en entier
                else:
                    failed_multipliers.append(multiplier)
            
            # Mettre à jour cout_craft avec les coûts calculés (même si incomplets)
            if costs:  # Au moins un coût a été calculé
                item_data.setdefault('cout_craft', {})
                item_data['cout_craft'][latest_date] = costs
                item_data['last_maj'] = latest_date
                if is_debug_item:
                    items_updated += 1
                    if failed_multipliers:
                        missing_ingredients_list.append(f"Multiplicateurs échoués: {failed_multipliers}")
            else:
                if is_debug_item:
                    items_skipped += 1
                    missing_ingredients_list.append('Aucun coût n\'a pu être calculé')
                    
                    # NOUVEAU: Afficher les détails du debug
                    print(f"\n{'='*80}")
                    print(f"DEBUG DÉTAILLÉ - Item [{item_id}] {item_name}")
                    print(f"{'='*80}")
                    print(f"Date utilisée: {latest_date}")
                    print(f"\nTentative de calcul pour chaque multiplicateur:")
                    
                    for mult, details in debug_details.items():
                        print(f"\n  Multiplicateur x{mult}:")
                        print(f"    Succès: {details['success']}")
                        print(f"    Coût total: {details['total_cost']}")
                        print(f"    Détails des ingrédients:")
                        
                        for ing in details['ingredients']:
                            print(f"      - [{ing['id']}] {ing['name']}")
                            print(f"        Quantité nécessaire: {ing['qty_needed']}")
                            print(f"        A une date de prix: {ing['has_date']}")
                            
                            if 'latest_date' in ing:
                                print(f"        Date de prix: {ing['latest_date']}")
                            
                            if 'price_calculation' in ing:
                                calc = ing['price_calculation']
                                if 'available_prices' in calc:
                                    print(f"        Prix disponibles: {calc['available_prices']}")
                                if 'error' in calc:
                                    print(f"        ⚠ Erreur: {calc['error']}")
                            
                            if 'cost' in ing:
                                print(f"        Coût calculé: {ing['cost']}")
                            
                            if 'error' in ing:
                                print(f"        ❌ ERREUR: {ing['error']}")
                    
                    print(f"\n{'='*80}\n")
            
            # Ajouter aux items avec problèmes si nécessaire
            if is_debug_item and missing_ingredients_list:
                items_with_missing_ingredients.append({
                    'id': item_id,
                    'name': item_name,
                    'missing': missing_ingredients_list
                })
        else:
            # Vraiment aucune date disponible
            if is_debug_item:
                items_skipped += 1
                items_with_missing_ingredients.append({
                    'id': item_id,
                    'name': item_name,
                    'missing': ['Aucune date disponible pour les ingrédients']
                })
        
        processed_items.add(item_id)
    
    # Traiter tous les items craftables
    if debug_items:
        print("=== DÉBUT DU CALCUL DES COÛTS DE CRAFT ===")
        print(f"Mode debug activé pour {len(debug_items)} items")
        print(f"Calcul des coûts pour les quantités: {MULTIPLIERS}\n")
    
    for item_id in data:
        if data[item_id].get('is_craft'):
            process_item(item_id)
    
    # Afficher les statistiques uniquement si mode debug
    if debug_items:
        print("\n=== RÉSUMÉ (items de equipements.txt uniquement) ===")
        print(f"Items mis à jour avec succès: {items_updated}")
        print(f"Items non calculés complètement: {items_skipped}")
        
        # Afficher les détails des items avec problèmes
        if items_with_missing_ingredients:
            print("\n=== RÉSUMÉ DES ITEMS AVEC PROBLÈMES ===")
            for item in items_with_missing_ingredients:
                print(f"\n[{item['id']}] {item['name']}")
                print(f"  Problèmes détectés:")
                for missing in item['missing']:
                    print(f"    - {missing}")


if __name__ == "__main__":
    # Charger la liste des equipements à debugger
    debug_items = set()
    try:
        with open('data/equipements.txt', 'r', encoding='utf-8') as f:
            debug_items = set(line.strip() for line in f if line.strip())
        print(f"Chargement de {len(debug_items)} items depuis equipements.txt")
    except FileNotFoundError:
        print("Fichier data/equipements.txt non trouvé, mode debug désactivé")
        debug_items = None

    with open('data/dofus_items.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    update_crafting_costs(data, debug_items)

    with open('data/dofus_items.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    if debug_items:
        print("\n=== FICHIER SAUVEGARDÉ ===")