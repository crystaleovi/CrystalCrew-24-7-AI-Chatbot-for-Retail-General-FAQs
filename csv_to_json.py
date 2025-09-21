import csv
import json
import os

# Absolute path to your CSVs (inside WSL)
CSV_FOLDER = "/mnt/c/Users/NAJWA/Downloads/StyleCo Data/StyleCo Data"
JSON_FOLDER = "/mnt/c/Users/NAJWA/aws hackathon/json_files"

os.makedirs(JSON_FOLDER, exist_ok=True)

table_mapping = {
    "Customers": "Customers.csv",
    "Products": "Products.csv",
    "Sales": "Sales.csv",
    "Shops": "ShopInfo.csv",
    "Suppliers": "Suppliers.csv"
}

def csv_to_json(csv_file, json_file):
    data = []
    with open(csv_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    with open(json_file, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

for table, csv_filename in table_mapping.items():
    csv_path = os.path.join(CSV_FOLDER, csv_filename)
    json_path = os.path.join(JSON_FOLDER, f"{table}.json")

    if os.path.exists(csv_path):
        print(f"Converting {csv_filename} → {json_path}")
        csv_to_json(csv_path, json_path)
    else:
        print(f"⚠️ Warning: {csv_filename} not found in {CSV_FOLDER}, skipping...")
