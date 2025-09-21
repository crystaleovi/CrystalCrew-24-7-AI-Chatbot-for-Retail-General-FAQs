import boto3

session = boto3.Session(
    profile_name="awsisb_IsbUsersPS-162343471173",
    region_name="ap-southeast-1"
)

dynamodb = session.client("dynamodb")

tables = {
    "Customers": {
        "KeySchema": [{"AttributeName": "CustomerID", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "CustomerID", "AttributeType": "S"}],
    },
    "Products": {
        "KeySchema": [{"AttributeName": "ProductID", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "ProductID", "AttributeType": "S"}],
    },
    "Sales": {
        "KeySchema": [{"AttributeName": "SaleID", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "SaleID", "AttributeType": "S"}],
    },
    "Shops": {
        "KeySchema": [{"AttributeName": "ShopID", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "ShopID", "AttributeType": "S"}],
    },
    "Suppliers": {
        "KeySchema": [{"AttributeName": "SupplierID", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "SupplierID", "AttributeType": "S"}],
    },
}

for name, schema in tables.items():
    try:
        table = dynamodb.create_table(
            TableName=name,
            KeySchema=schema["KeySchema"],
            AttributeDefinitions=schema["AttributeDefinitions"],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print(f"✅ Creating {name}... status: {table['TableDescription']['TableStatus']}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"⚠️ {name} already exists, skipping...")
