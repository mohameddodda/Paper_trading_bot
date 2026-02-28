import os
root = 'd:/playground/Paper_Trading_Bot'
items = sorted(os.listdir(root))
print("=== ROOT DIRECTORY CONTENTS ===")
print(f"Total items: {len(items)}")
print()
for item in items:
    item_path = os.path.join(root, item)
    if os.path.isfile(item_path):
        size = os.path.getsize(item_path)
        print(f"FILE: {item} ({size} bytes)")
    elif os.path.isdir(item_path):
        print(f"DIR:  {item}/")
print("=== END ===")
