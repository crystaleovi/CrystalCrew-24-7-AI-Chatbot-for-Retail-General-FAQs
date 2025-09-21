import json
import boto3
import logging
from datetime import datetime
import uuid

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='ap-southeast-1')
translate = boto3.client('translate', region_name='ap-southeast-1')
comprehend = boto3.client('comprehend', region_name='ap-southeast-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB tables
sessions_table = dynamodb.Table('chatbot-sessions')
analytics_table = dynamodb.Table('chatbot-analytics')

def lambda_handler(event, context):
    try:
        # Parse request
        body = json.loads(event['body']) if event.get('body') else {}
        user_message = body.get('message', '')
        session_id = body.get('session_id', str(uuid.uuid4()))
        language = body.get('language', 'en')
        
        # Detect sentiment
        sentiment = detect_sentiment(user_message)
        
        # Translate if needed
        if language != 'en':
            user_message = translate_text(user_message, language, 'en')
        
        # Get AI response from Bedrock
        ai_response = get_bedrock_response(user_message, session_id)
        
        # Translate response back
        if language != 'en':
            ai_response = translate_text(ai_response, 'en', language)
        
        # Store session and analytics
        store_session(session_id, user_message, ai_response, sentiment)
        store_analytics(session_id, sentiment, language)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': ai_response,
                'session_id': session_id,
                'sentiment': sentiment,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

def get_bedrock_response(message, session_id):
    """Get response from AWS Bedrock"""
    try:
        # Get conversation history
        history = get_session_history(session_id)
        
        prompt = f"""You are a helpful customer service chatbot for a retail business. 
        Provide accurate, friendly responses to customer inquiries.
        
        Conversation history: {history}
        
        Customer: {message}
        Assistant:"""
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        return result['content'][0]['text']
        
    except Exception as e:
        logger.error(f"Bedrock error: {str(e)}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again."

def detect_sentiment(text):
    """Detect sentiment using Amazon Comprehend"""
    try:
        response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
        return response['Sentiment']
    except:
        return 'NEUTRAL'

def translate_text(text, source_lang, target_lang):
    """Translate text using Amazon Translate"""
    try:
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang
        )
        return response['TranslatedText']
    except:
        return text

def get_session_history(session_id):
    """Get conversation history from DynamoDB"""
    try:
        response = sessions_table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': session_id},
            Limit=5,
            ScanIndexForward=False
        )
        return [item['conversation'] for item in response['Items']]
    except:
        return []

def store_session(session_id, user_msg, bot_response, sentiment):
    """Store conversation in DynamoDB"""
    try:
        sessions_table.put_item(
            Item={
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'conversation': f"User: {user_msg}\nBot: {bot_response}",
                'sentiment': sentiment
            }
        )
    except Exception as e:
        logger.error(f"Session storage error: {str(e)}")

def store_analytics(session_id, sentiment, language):
    """Store analytics data"""
    try:
        analytics_table.put_item(
            Item={
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'sentiment': sentiment,
                'language': language,
                'date': datetime.utcnow().strftime('%Y-%m-%d')
            }
        )
    except Exception as e:
        logger.error(f"Analytics storage error: {str(e)}")
