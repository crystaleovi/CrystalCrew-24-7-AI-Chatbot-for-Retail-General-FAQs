import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('prod-chatbot-faq')

# Sample FAQ data for retail business
faq_data = [
    {
        'category': 'general',
        'question': 'What are your store hours?',
        'answer': 'Our store is open Monday-Saturday 9AM-9PM, Sunday 10AM-6PM.'
    },
    {
        'category': 'general',
        'question': 'Where are you located?',
        'answer': 'We have multiple locations. Please visit our store locator on our website for the nearest location.'
    },
    {
        'category': 'shipping',
        'question': 'How long does shipping take?',
        'answer': 'Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days.'
    },
    {
        'category': 'shipping',
        'question': 'Do you offer free shipping?',
        'answer': 'Yes! We offer free standard shipping on orders over $50.'
    },
    {
        'category': 'returns',
        'question': 'What is your return policy?',
        'answer': 'We accept returns within 30 days of purchase with original receipt and tags attached.'
    },
    {
        'category': 'returns',
        'question': 'How do I return an item?',
        'answer': 'You can return items in-store or mail them back using our prepaid return label.'
    },
    {
        'category': 'payment',
        'question': 'What payment methods do you accept?',
        'answer': 'We accept all major credit cards, PayPal, Apple Pay, and Google Pay.'
    },
    {
        'category': 'products',
        'question': 'Do you have size guides?',
        'answer': 'Yes, you can find size guides on each product page or in our sizing section.'
    },
    {
        'category': 'products',
        'question': 'When will items be back in stock?',
        'answer': 'Stock updates happen daily. Sign up for restock notifications on the product page.'
    },
    {
        'category': 'account',
        'question': 'How do I create an account?',
        'answer': 'Click "Sign Up" at the top of our website and follow the simple registration process.'
    }
]

def seed_faq():
    """Seed FAQ data into DynamoDB"""
    try:
        with table.batch_writer() as batch:
            for item in faq_data:
                batch.put_item(Item=item)
        
        print(f"Successfully seeded {len(faq_data)} FAQ items")
        
    except Exception as e:
        print(f"Error seeding FAQ data: {e}")

if __name__ == "__main__":
    seed_faq()
