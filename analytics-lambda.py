import json
import boto3
from datetime import datetime, timedelta
from collections import Counter

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
analytics_table = dynamodb.Table('chatbot-analytics')

def lambda_handler(event, context):
    """Generate analytics dashboard data"""
    try:
        # Get date range (last 7 days by default)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Query analytics data
        analytics_data = get_analytics_data(start_date, end_date)
        
        # Generate insights
        insights = {
            'total_conversations': len(analytics_data),
            'sentiment_distribution': get_sentiment_distribution(analytics_data),
            'language_distribution': get_language_distribution(analytics_data),
            'daily_volume': get_daily_volume(analytics_data),
            'peak_hours': get_peak_hours(analytics_data)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(insights)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_analytics_data(start_date, end_date):
    """Fetch analytics data from DynamoDB"""
    items = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        response = analytics_table.query(
            IndexName='date-index',
            KeyConditionExpression='#date = :date',
            ExpressionAttributeNames={'#date': 'date'},
            ExpressionAttributeValues={':date': date_str}
        )
        items.extend(response['Items'])
        current_date += timedelta(days=1)
    
    return items

def get_sentiment_distribution(data):
    """Calculate sentiment distribution"""
    sentiments = [item['sentiment'] for item in data]
    return dict(Counter(sentiments))

def get_language_distribution(data):
    """Calculate language distribution"""
    languages = [item['language'] for item in data]
    return dict(Counter(languages))

def get_daily_volume(data):
    """Calculate daily conversation volume"""
    dates = [item['date'] for item in data]
    return dict(Counter(dates))

def get_peak_hours(data):
    """Calculate peak usage hours"""
    hours = []
    for item in data:
        timestamp = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
        hours.append(timestamp.hour)
    return dict(Counter(hours))
