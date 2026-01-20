"""
Script de débogage pour comprendre le calcul de la Pièce du Trésor du Badoul
"""
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages'))

from prices import calculate_optimal_price

# Prix de la Pièce du Trésor du Badoul
prix_dict = {'1': 29, '10': 447, '100': 4870, '1000': None}
target_quantity = 100

print("=" * 60)
print("DEBUG: Pièce du Trésor du Badoul")
print("=" * 60)
print(f"\nPrix disponibles: {prix_dict}")
print(f"Quantité cible: {target_quantity}")

# Tester manuellement les combinaisons
available = [(1, 29), (10, 447), (100, 4870)]

print("\n--- Combinaisons testées manuellement ---")

# Option 1: Prix flat direct
if 100 >= target_quantity:
    print(f"1× x100 = {4870}K")

# Option 2: Multiples simples
print(f"10× x10 = {10 * 447}K")
print(f"100× x1 = {100 * 29}K (mais > 99 achats)")

# Option 3: Combinaisons
print("\nCombinaisons possibles:")
# Combinaisons avec x100
print(f"1× x100 + 0× x10 + 0× x1 = {1*4870 + 0*447 + 0*29}K")

# Combinaisons avec x10
for n_x10 in range(0, min(100, 10) + 1):
    remaining = 100 - n_x10 * 10
    if remaining <= 99:  # On peut acheter jusqu'à 99× x1
        cost = n_x10 * 447 + remaining * 29
        print(f"{n_x10}× x10 + {remaining}× x1 = {cost}K")

# Calculer avec la vraie fonction
print("\n--- Résultat de calculate_optimal_price ---")
result = calculate_optimal_price(prix_dict, target_quantity)
print(f"Résultat: {result}K")
