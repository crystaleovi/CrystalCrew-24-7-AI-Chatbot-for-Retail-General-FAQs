import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('prod-chatbot-faq')

# Comprehensive retail FAQs
comprehensive_faq = [
    # General Store Information
    {
        'category': 'general',
        'question': 'What are your store opening and closing hours?',
        'answer': 'Our store is open Monday-Saturday 9AM-9PM, Sunday 10AM-6PM. Holiday hours may vary.'
    },
    {
        'category': 'general',
        'question': 'Where is your store located?',
        'answer': 'We have multiple locations. Please visit our store locator on our website or call us for the nearest location to you.'
    },
    {
        'category': 'general',
        'question': 'Do you have parking available for customers?',
        'answer': 'Yes! We offer free customer parking at all our locations. Some stores have valet parking available.'
    },
    {
        'category': 'general',
        'question': 'Do you offer online shopping as well as in-store shopping?',
        'answer': 'Absolutely! You can shop online 24/7 at our website or visit any of our physical store locations.'
    },
    {
        'category': 'general',
        'question': 'Can I check product availability before visiting the store?',
        'answer': 'Yes! Use our website or call the store directly to check if an item is in stock before your visit.'
    },
    
    # Products & Services
    {
        'category': 'products',
        'question': 'Do you restock sold-out items? If yes, how often?',
        'answer': 'Yes, we restock popular items regularly. Most items are restocked weekly. Sign up for restock notifications on our website.'
    },
    {
        'category': 'products',
        'question': 'Do you provide product warranties or guarantees?',
        'answer': 'Yes! All our products come with manufacturer warranties. We also offer extended warranty options for electronics and appliances.'
    },
    {
        'category': 'products',
        'question': 'Can I request a product that isn\'t available in your store?',
        'answer': 'Absolutely! We can special order items for you. Speak with any team member or contact customer service for assistance.'
    },
    {
        'category': 'products',
        'question': 'Do you offer gift cards or vouchers?',
        'answer': 'Yes! We offer both physical and digital gift cards in various denominations. Perfect for any occasion!'
    },
    {
        'category': 'products',
        'question': 'Do you provide personal shopping or styling assistance?',
        'answer': 'Yes! Our personal shopping service is complimentary. Book an appointment online or call your local store.'
    },
    
    # Payments
    {
        'category': 'payment',
        'question': 'What payment methods do you accept?',
        'answer': 'We accept cash, all major credit/debit cards, PayPal, Apple Pay, Google Pay, and popular e-wallets.'
    },
    {
        'category': 'payment',
        'question': 'Can I use multiple payment methods in a single transaction?',
        'answer': 'Yes! You can split payments between different methods like cash and card, or multiple cards.'
    },
    {
        'category': 'payment',
        'question': 'Do you offer instalment or Buy Now, Pay Later options?',
        'answer': 'Yes! We partner with Klarna, Afterpay, and offer our own 0% interest payment plans for qualifying purchases.'
    },
    
    # Returns & Exchanges
    {
        'category': 'returns',
        'question': 'What is your return and exchange policy?',
        'answer': 'We accept returns within 30 days of purchase with original receipt and tags attached. Items must be in original condition.'
    },
    {
        'category': 'returns',
        'question': 'How long do I have to return or exchange a product?',
        'answer': 'You have 30 days from the purchase date to return or exchange items. Extended holiday return periods apply in December.'
    },
    {
        'category': 'returns',
        'question': 'Can I return an item I bought online to the physical store?',
        'answer': 'Yes! Online purchases can be returned to any of our physical store locations with your order confirmation.'
    },
    {
        'category': 'returns',
        'question': 'Do you provide refunds, or only store credit/exchanges?',
        'answer': 'We offer full refunds to your original payment method, store credit, or exchanges - your choice!'
    },
    
    # Shipping & Delivery
    {
        'category': 'shipping',
        'question': 'Do you offer home delivery or shipping services?',
        'answer': 'Yes! We offer standard shipping, express delivery, and same-day delivery in select areas.'
    },
    {
        'category': 'shipping',
        'question': 'How long does delivery usually take?',
        'answer': 'Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days. Same-day delivery available in select cities.'
    },
    {
        'category': 'shipping',
        'question': 'Is there a minimum purchase amount for free delivery?',
        'answer': 'Yes! We offer free standard shipping on orders over $50. Express shipping is free on orders over $100.'
    }
]

def seed_comprehensive_faq():
    """Add comprehensive retail FAQs"""
    try:
        with table.batch_writer() as batch:
            for item in comprehensive_faq:
                batch.put_item(Item=item)
        
        print(f"Successfully added {len(comprehensive_faq)} comprehensive FAQ items")
        
        # Display summary by category
        categories = {}
        for item in comprehensive_faq:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nFAQ Categories Added:")
        for category, count in categories.items():
            print(f"  {category}: {count} items")
            
    except Exception as e:
        print(f"Error adding comprehensive FAQ data: {e}")

if __name__ == "__main__":
    seed_comprehensive_faq()
