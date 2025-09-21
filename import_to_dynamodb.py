import boto3
import json
import os
import uuid

# Folder where JSON files are stored
JSON_FOLDER = "json_files"

# DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-1")

# Mapping of local JSON filenames → DynamoDB table names and their primary key
tables = {
    "Customers": {"file": "Customers.json", "key": "CustomerID"},
    "StyleCoProducts": {"file": "Products.json", "key": "product_id"},
    "Sales": {"file": "Sales.json", "key": "SaleID", "alt_key": "TransactionIDD"},  # Fix mismatched key
    "Shops": {"file": "Shops.json", "key": "ShopID"},
    "Suppliers": {"file": "Suppliers.json", "key": "SupplierID"}
}

def import_data(table_name, json_file, primary_key, alt_key=None):
    table = dynamodb.Table(table_name)

    with open(json_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"📥 Importing {len(items)} items into {table_name}...")

    with table.batch_writer() as batch:
        for item in items:
            # Fix mismatched key name if needed
            if alt_key and alt_key in item:
                item[primary_key] = item.pop(alt_key)
            
            # Generate key if missing (for tables like Shops)
            if primary_key not in item:
                item[primary_key] = str(uuid.uuid4())  # Generate a unique ID

            batch.put_item(Item=item)

    print(f"✅ Finished importing {table_name}")

# Loop through tables and import data
for table_name, info in tables.items():
    json_path = os.path.join(JSON_FOLDER, info["file"])
    if os.path.exists(json_path):
        import_data(
            table_name,
            json_path,
            primary_key=info["key"],
            alt_key=info.get("alt_key")
        )
    else:
        print(f"⚠️ Warning: {info['file']} not found in {JSON_FOLDER}, skipping...")
