import requests
import json
import uuid

class ChatbotClient:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint
        self.session_id = str(uuid.uuid4())
    
    def send_message(self, message, language='en'):
        """Send message to chatbot"""
        payload = {
            'message': message,
            'sessionId': self.session_id,
            'language': language
        }
        
        try:
            response = requests.post(
                f"{self.api_endpoint}/chat",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}

def test_chatbot():
    """Test the chatbot with various scenarios"""
    # Replace with your actual API Gateway endpoint
    api_endpoint = "https://your-api-id.execute-api.ap-southeast-1.amazonaws.com/prod"
    
    client = ChatbotClient(api_endpoint)
    
    test_messages = [
        ("Hello, what are your store hours?", "en"),
        ("¿Cuáles son sus horarios de tienda?", "es"),  # Spanish
        ("How do I return an item?", "en"),
        ("I'm very frustrated with my order!", "en"),  # Negative sentiment
        ("Thank you for your excellent service!", "en"),  # Positive sentiment
    ]
    
    print("Testing 24/7 AI Chatbot")
    print("=" * 50)
    
    for message, language in test_messages:
        print(f"\nUser ({language}): {message}")
        response = client.send_message(message, language)
        
        if 'error' in response:
            print(f"Error: {response['error']}")
        else:
            print(f"Bot: {response['response']}")
            print(f"Sentiment: {response['metadata']['sentiment']['sentiment']}")
            print(f"Used FAQ: {response['metadata']['usedFAQ']}")

if __name__ == "__main__":
    test_chatbot()
