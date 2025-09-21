import json
import boto3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

CHAT_HISTORY_TABLE = os.environ['CHAT_HISTORY_TABLE']

class AnalyticsService:
    def __init__(self):
        self.chat_table = dynamodb.Table(CHAT_HISTORY_TABLE)
    
    def get_chat_metrics(self, hours: int = 24) -> Dict:
        """Get chat metrics for the specified time period"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            start_timestamp = int(start_time.timestamp())
            
            # Scan for recent chats (in production, use GSI for better performance)
            response = self.chat_table.scan(
                FilterExpression='#ts >= :start_time',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={':start_time': start_timestamp}
            )
            
            items = response['Items']
            
            # Calculate metrics
            total_chats = len(items)
            sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'MIXED': 0}
            language_counts = {}
            faq_usage = 0
            
            for item in items:
                metadata = item.get('metadata', {})
                
                # Sentiment analysis
                sentiment = metadata.get('sentiment', {}).get('sentiment', 'NEUTRAL')
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                # Language distribution
                lang = metadata.get('detectedLanguage', 'en')
                language_counts[lang] = language_counts.get(lang, 0) + 1
                
                # FAQ usage
                if metadata.get('usedFAQ', False):
                    faq_usage += 1
            
            return {
                'totalChats': total_chats,
                'sentimentDistribution': sentiment_counts,
                'languageDistribution': language_counts,
                'faqUsageRate': (faq_usage / total_chats * 100) if total_chats > 0 else 0,
                'timeRange': f'{hours} hours'
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat metrics: {e}")
            return {}
    
    def publish_metrics_to_cloudwatch(self, metrics: Dict):
        """Publish metrics to CloudWatch"""
        try:
            # Total chats
            cloudwatch.put_metric_data(
                Namespace='Chatbot/Analytics',
                MetricData=[
                    {
                        'MetricName': 'TotalChats',
                        'Value': metrics.get('totalChats', 0),
                        'Unit': 'Count'
                    }
                ]
            )
            
            # Sentiment metrics
            sentiment_dist = metrics.get('sentimentDistribution', {})
            for sentiment, count in sentiment_dist.items():
                cloudwatch.put_metric_data(
                    Namespace='Chatbot/Sentiment',
                    MetricData=[
                        {
                            'MetricName': f'{sentiment}Sentiment',
                            'Value': count,
                            'Unit': 'Count'
                        }
                    ]
                )
            
            # FAQ usage rate
            cloudwatch.put_metric_data(
                Namespace='Chatbot/Performance',
                MetricData=[
                    {
                        'MetricName': 'FAQUsageRate',
                        'Value': metrics.get('faqUsageRate', 0),
                        'Unit': 'Percent'
                    }
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to publish metrics: {e}")

def lambda_handler(event, context):
    """Analytics Lambda handler"""
    try:
        analytics = AnalyticsService()
        
        # Get time range from event (default 24 hours)
        hours = event.get('hours', 24)
        
        # Generate metrics
        metrics = analytics.get_chat_metrics(hours)
        
        # Publish to CloudWatch
        analytics.publish_metrics_to_cloudwatch(metrics)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Analytics handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to generate analytics'})
        }
