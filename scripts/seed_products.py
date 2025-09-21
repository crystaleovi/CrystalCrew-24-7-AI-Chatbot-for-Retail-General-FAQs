import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('prod-shop-catalog')

# Sample product catalog for retail store
products = [
    {
        'productId': 'TECH001',
        'name': 'Wireless Bluetooth Headphones',
        'category': 'Electronics',
        'price': Decimal('89.99'),
        'description': 'Premium noise-canceling wireless headphones with 30-hour battery life',
        'inStock': True,
        'stockQuantity': 45,
        'brand': 'TechSound',
        'rating': Decimal('4.5'),
        'tags': ['wireless', 'bluetooth', 'headphones', 'music']
    },
    {
        'productId': 'FASH001',
        'name': 'Designer Leather Handbag',
        'category': 'Fashion',
        'price': Decimal('199.99'),
        'description': 'Elegant genuine leather handbag perfect for work or casual outings',
        'inStock': True,
        'stockQuantity': 23,
        'brand': 'StyleCraft',
        'rating': Decimal('4.8'),
        'tags': ['handbag', 'leather', 'fashion', 'accessories']
    },
    {
        'productId': 'HOME001',
        'name': 'Smart LED Table Lamp',
        'category': 'Home',
        'price': Decimal('45.99'),
        'description': 'WiFi-enabled smart lamp with adjustable brightness and color temperature',
        'inStock': True,
        'stockQuantity': 67,
        'brand': 'SmartHome',
        'rating': Decimal('4.3'),
        'tags': ['smart', 'lamp', 'led', 'home', 'lighting']
    },
    {
        'productId': 'BOOK001',
        'name': 'The Art of Mindfulness',
        'category': 'Books',
        'price': Decimal('24.99'),
        'description': 'A comprehensive guide to meditation and mindful living',
        'inStock': True,
        'stockQuantity': 89,
        'brand': 'Wisdom Press',
        'rating': Decimal('4.7'),
        'tags': ['book', 'mindfulness', 'meditation', 'self-help']
    },
    {
        'productId': 'SPORT001',
        'name': 'Yoga Mat Premium',
        'category': 'Sports',
        'price': Decimal('39.99'),
        'description': 'Non-slip eco-friendly yoga mat with alignment guides',
        'inStock': True,
        'stockQuantity': 34,
        'brand': 'ZenFit',
        'rating': Decimal('4.6'),
        'tags': ['yoga', 'mat', 'fitness', 'exercise', 'eco-friendly']
    },
    {
        'productId': 'GIFT001',
        'name': 'Luxury Candle Set',
        'category': 'Gifts',
        'price': Decimal('59.99'),
        'description': 'Set of 3 premium scented candles in elegant glass containers',
        'inStock': True,
        'stockQuantity': 56,
        'brand': 'Aromatherapy Co',
        'rating': Decimal('4.4'),
        'tags': ['candles', 'gift', 'scented', 'luxury', 'aromatherapy']
    },
    {
        'productId': 'TECH002',
        'name': 'Smartphone Wireless Charger',
        'category': 'Electronics',
        'price': Decimal('29.99'),
        'description': 'Fast wireless charging pad compatible with all Qi-enabled devices',
        'inStock': True,
        'stockQuantity': 78,
        'brand': 'ChargeTech',
        'rating': Decimal('4.2'),
        'tags': ['wireless', 'charger', 'smartphone', 'fast-charging']
    },
    {
        'productId': 'FASH002',
        'name': 'Casual Cotton T-Shirt',
        'category': 'Fashion',
        'price': Decimal('19.99'),
        'description': 'Comfortable 100% organic cotton t-shirt available in multiple colors',
        'inStock': True,
        'stockQuantity': 120,
        'brand': 'EcoWear',
        'rating': Decimal('4.1'),
        'tags': ['t-shirt', 'cotton', 'casual', 'organic', 'comfortable']
    },
    {
        'productId': 'HOME002',
        'name': 'Coffee Maker Deluxe',
        'category': 'Home',
        'price': Decimal('129.99'),
        'description': 'Programmable coffee maker with built-in grinder and thermal carafe',
        'inStock': False,
        'stockQuantity': 0,
        'brand': 'BrewMaster',
        'rating': Decimal('4.9'),
        'tags': ['coffee', 'maker', 'programmable', 'grinder', 'thermal']
    },
    {
        'productId': 'GIFT002',
        'name': 'Personalized Photo Frame',
        'category': 'Gifts',
        'price': Decimal('34.99'),
        'description': 'Custom engraved wooden photo frame perfect for special memories',
        'inStock': True,
        'stockQuantity': 42,
        'brand': 'MemoryKeepers',
        'rating': Decimal('4.8'),
        'tags': ['photo', 'frame', 'personalized', 'wooden', 'custom', 'gift']
    }
]

def seed_products():
    """Seed product catalog into DynamoDB"""
    try:
        with table.batch_writer() as batch:
            for product in products:
                batch.put_item(Item=product)
        
        print(f"Successfully seeded {len(products)} products into catalog")
        
        # Display summary
        categories = {}
        for product in products:
            cat = product['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nProduct Categories:")
        for category, count in categories.items():
            print(f"  {category}: {count} items")
            
    except Exception as e:
        print(f"Error seeding product data: {e}")

if __name__ == "__main__":
    seed_products()
