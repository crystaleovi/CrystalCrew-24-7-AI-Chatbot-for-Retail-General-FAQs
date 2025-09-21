import json
import boto3
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
comprehend = boto3.client('comprehend', region_name='ap-southeast-1')
translate = boto3.client('translate', region_name='ap-southeast-1')
dynamodb = boto3.resource('dynamodb')
events = boto3.client('events', region_name='ap-southeast-1')

# Environment variables
CHAT_HISTORY_TABLE = os.environ['CHAT_HISTORY_TABLE']
FAQ_TABLE = os.environ['FAQ_TABLE']
EVENT_BUS_NAME = os.environ['EVENT_BUS_NAME']

def convert_floats_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(v) for v in obj]
    return obj

class ChatbotService:
    def __init__(self):
        self.chat_table = dynamodb.Table(CHAT_HISTORY_TABLE)
        self.faq_table = dynamodb.Table(FAQ_TABLE)
    
    def detect_language(self, text: str) -> str:
        """Detect language of input text"""
        try:
            response = comprehend.detect_dominant_language(Text=text)
            return response['Languages'][0]['LanguageCode']
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return 'en'
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages"""
        if source_lang == target_lang:
            return text
        
        try:
            response = translate.translate_text(
                Text=text,
                SourceLanguageCode=source_lang,
                TargetLanguageCode=target_lang
            )
            return response['TranslatedText']
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotion"""
        try:
            response = comprehend.detect_sentiment(
                Text=text,
                LanguageCode='en'
            )
            return {
                'sentiment': response['Sentiment'],
                'confidence': response['SentimentScore']
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'sentiment': 'NEUTRAL', 'confidence': {}}
    
    def search_faq(self, query: str) -> Optional[str]:
        """Search FAQ database across all categories"""
        try:
            categories = ['general', 'shipping', 'returns', 'payment', 'products', 'account']
            
            query_lower = query.lower()
            for category in categories:
                try:
                    response = self.faq_table.query(
                        KeyConditionExpression='category = :cat',
                        ExpressionAttributeValues={':cat': category}
                    )
                    
                    for item in response['Items']:
                        if any(word in item['question'].lower() for word in query_lower.split()):
                            return item['answer']
                except Exception:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"FAQ search failed: {e}")
            return None
    
    def generate_bedrock_response(self, message: str, context: str = "") -> str:
        """Generate AI response using Bedrock Claude"""
        try:
            prompt = f"""You are a helpful customer service chatbot for a retail business. 
            Provide accurate, friendly, and concise responses in a conversational tone.
            
            Context: {context}
            Customer message: {message}
            
            Please provide a helpful response:"""
            
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7,
                "anthropic_version": "bedrock-2023-05-31"
            })
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Bedrock failed: {e}")
            # Fallback to smart response
            return self.generate_smart_response(message)
    
    def generate_smart_response(self, message: str) -> str:
        """Fallback intelligent responses"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! Welcome to our store. How can I help you today?"
        
        if any(word in message_lower for word in ['thank', 'thanks']):
            return "You're very welcome! Is there anything else I can help you with?"
        
        if any(word in message_lower for word in ['product', 'item', 'buy']):
            return "I'd be happy to help you with product information. You can browse our catalog on our website or visit one of our stores."
        
        return "Thank you for your message. I'm here to help with any questions about our store, products, or services. What can I assist you with?"

def lambda_handler(event, context):
    """Main Lambda handler with Bedrock integration"""
    try:
        chatbot = ChatbotService()
        
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '')
        session_id = body.get('sessionId', context.aws_request_id)
        user_language = body.get('language', 'en')
        
        if not user_message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Message is required'})
            }
        
        # Detect language
        detected_language = chatbot.detect_language(user_message)
        
        # Translate to English for processing
        english_message = chatbot.translate_text(user_message, detected_language, 'en')
        
        # Analyze sentiment
        sentiment_data = chatbot.analyze_sentiment(english_message)
        
        # Search FAQ first
        faq_response = chatbot.search_faq(english_message)
        
        # Generate response
        if faq_response:
            bot_response = faq_response
            used_faq = True
            used_bedrock = False
        else:
            bot_response = chatbot.generate_bedrock_response(english_message)
            used_faq = False
            used_bedrock = True
        
        # Translate response back to user's language
        final_response = chatbot.translate_text(bot_response, 'en', user_language)
        
        # Prepare metadata
        metadata = {
            'detectedLanguage': detected_language,
            'userLanguage': user_language,
            'sentiment': sentiment_data,
            'usedFAQ': used_faq,
            'usedBedrock': used_bedrock,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save chat history
        try:
            timestamp = int(datetime.now().timestamp())
            metadata_decimal = convert_floats_to_decimal(metadata)
            
            chatbot.chat_table.put_item(
                Item={
                    'sessionId': session_id,
                    'timestamp': timestamp,
                    'userMessage': user_message,
                    'botResponse': final_response,
                    'metadata': metadata_decimal
                }
            )
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
        
        # Publish analytics event
        try:
            events.put_events(
                Entries=[
                    {
                        'Source': 'chatbot.service',
                        'DetailType': 'chat.interaction',
                        'Detail': json.dumps({
                            'sessionId': session_id,
                            'sentiment': sentiment_data['sentiment'],
                            'language': detected_language,
                            'usedFAQ': used_faq,
                            'usedBedrock': used_bedrock
                        }),
                        'EventBusName': EVENT_BUS_NAME
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': final_response,
                'sessionId': session_id,
                'metadata': metadata
            })
        }
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }
