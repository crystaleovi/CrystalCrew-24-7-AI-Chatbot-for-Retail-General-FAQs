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

# Initialize AWS clients - Bedrock in US East 1, others in ap-southeast-1
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
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
    
    def search_faq(self, query: str, user_language: str = 'en') -> Optional[str]:
        """Search FAQ database with language-specific matching"""
        try:
            categories = ['general', 'shipping', 'returns', 'payment', 'products', 'account']
            
            query_lower = query.lower()
            
            # Define keywords for different languages
            if user_language == 'ms':  # Malay
                faq_keywords = {
                    'store hours': ['waktu', 'operasi', 'buka', 'tutup', 'jam'],
                    'location': ['lokasi', 'alamat', 'mana', 'kedai'],
                    'parking': ['parking', 'tempat', 'kereta'],
                    'online': ['online', 'website', 'internet'],
                    'availability': ['ada', 'stock', 'tersedia'],
                    'restock': ['restock', 'tambah', 'barang'],
                    'warranty': ['warranty', 'jaminan', 'waranti'],
                    'gift_cards': ['gift', 'kad', 'hadiah', 'voucher'],
                    'personal_shopping': ['personal', 'bantuan', 'styling'],
                    'payment': ['bayar', 'pembayaran', 'kad', 'cash'],
                    'installment': ['ansuran', 'bayar', 'kemudian'],
                    'return': ['pulang', 'pemulangan', 'balik', 'kembali', 'tukar'],
                    'refund': ['refund', 'wang', 'balik'],
                    'shipping': ['hantar', 'penghantaran', 'pos', 'delivery'],
                    'delivery_time': ['berapa', 'lama', 'masa', 'hari']
                }
            else:  # English and other languages
                faq_keywords = {
                    'store hours': ['hours', 'open', 'close', 'time', 'opening', 'closing'],
                    'location': ['location', 'address', 'where', 'store', 'located'],
                    'parking': ['parking', 'park', 'car'],
                    'online': ['online', 'website', 'internet', 'web'],
                    'availability': ['availability', 'available', 'stock', 'check'],
                    'restock': ['restock', 'sold out', 'replenish', 'when'],
                    'warranty': ['warranty', 'guarantee', 'protection'],
                    'gift_cards': ['gift card', 'voucher', 'gift certificate'],
                    'personal_shopping': ['personal shopping', 'styling', 'assistance', 'help'],
                    'payment': ['payment', 'pay', 'card', 'cash', 'methods'],
                    'installment': ['installment', 'payment plan', 'buy now pay later', 'klarna', 'afterpay'],
                    'return': ['return', 'exchange', 'policy'],
                    'refund': ['refund', 'money back', 'credit'],
                    'shipping': ['shipping', 'delivery', 'deliver', 'ship'],
                    'delivery_time': ['how long', 'delivery time', 'shipping time', 'take']
                }
            
            # Check for specific FAQ matches
            for faq_topic, keywords in faq_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    for category in categories:
                        try:
                            response = self.faq_table.query(
                                KeyConditionExpression='category = :cat',
                                ExpressionAttributeValues={':cat': category}
                            )
                            
                            for item in response['Items']:
                                question_lower = item['question'].lower()
                                
                                # Match language-specific questions
                                if user_language == 'ms':
                                    # For Malay, look for Malay questions
                                    if any(malay_word in question_lower for malay_word in ['apakah', 'bagaimana', 'adakah', 'berapa']):
                                        if any(keyword in question_lower for keyword in keywords):
                                            return item['answer']
                                else:
                                    # For English, look for English questions
                                    if not any(malay_word in question_lower for malay_word in ['apakah', 'bagaimana', 'adakah', 'berapa']):
                                        if any(keyword in question_lower for keyword in keywords):
                                            return item['answer']
                        except Exception:
                            continue
            
            return None
        except Exception as e:
            logger.error(f"FAQ search failed: {e}")
            return None
    
    def generate_llama_response(self, message: str, context: str = "") -> str:
        """Generate AI response using Llama 3 8B Instruct"""
        try:
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful customer service chatbot for a retail business. Provide accurate, friendly, and concise responses in a conversational tone. Keep responses under 100 words.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Context: {context}
Customer message: {message}

Please provide a helpful response:

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            
            body = json.dumps({
                "prompt": prompt,
                "max_gen_len": 200,
                "temperature": 0.7,
                "top_p": 0.9
            })
            
            response = bedrock.invoke_model(
                modelId='meta.llama3-8b-instruct-v1:0',
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['generation'].strip()
            
        except Exception as e:
            logger.error(f"Llama failed: {e}")
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
    """Main Lambda handler with Llama integration"""
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
        
        # Search FAQ first with user's language
        faq_response = chatbot.search_faq(english_message, user_language)
        
        # Generate response
        if faq_response:
            bot_response = faq_response
            used_faq = True
            used_bedrock = False
        else:
            bot_response = chatbot.generate_llama_response(english_message)
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
            'model': 'meta.llama3-8b-instruct-v1:0',
            'region': 'us-east-1',
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
                            'usedBedrock': used_bedrock,
                            'model': 'llama3-8b'
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
