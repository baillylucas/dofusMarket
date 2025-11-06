import json

with open('data/dofus_items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

types = set()
for item in data.values():
    if 'type' in item:
        types.add(item['type'])

print("types uniques :")
for type in sorted(types):
    print(f"  - {type}")

print(f"\nTotal : {len(types)} types")