# 24/7 AI Chatbot for Retail Customer Support

A comprehensive, production-ready AI chatbot solution built with AWS services to provide round-the-clock customer support for retail businesses.

## 🚀 Features

### Core Capabilities
- **24/7 Availability**: Serverless architecture ensures continuous operation
- **Multilingual Support**: Automatic language detection and translation
- **Emotion Intelligence**: Sentiment analysis for better customer understanding
- **FAQ Integration**: Smart matching with pre-configured answers
- **Real-time Analytics**: Business insights and performance metrics
- **Event-Driven Architecture**: Scalable and responsive system design

### AWS Services Used
- **Amazon Bedrock**: AI/LLM for natural language responses
- **Amazon Comprehend**: Sentiment analysis and language detection
- **Amazon Translate**: Multi-language support
- **DynamoDB**: Chat history and FAQ storage
- **Lambda**: Serverless compute functions
- **API Gateway**: REST API endpoints
- **CloudWatch**: Monitoring and analytics
- **Cognito**: User authentication
- **EventBridge**: Event-driven messaging

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.9+
- AWS account with access to:
  - Bedrock (Claude models)
  - Comprehend
  - Translate
  - DynamoDB
  - Lambda
  - CloudFormation

## 🛠️ Deployment

### 1. Clone and Setup
```bash
git clone <repository-url>
cd aws-hackathon
```

### 2. Deploy Infrastructure
```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh prod ap-southeast-1
```

### 3. Manual Lambda Deployment (if needed)
```bash
# Package functions
cd lambda
zip -r ../build/chatbot-handler.zip chatbot_handler.py
zip -r ../build/analytics-handler.zip analytics_handler.py
cd ..

# Deploy chatbot function
aws lambda create-function \
    --function-name "prod-chatbot-handler" \
    --runtime python3.9 \
    --role "arn:aws:iam::YOUR-ACCOUNT:role/prod-chatbot-stack-LambdaExecutionRole-XXXXX" \
    --handler chatbot_handler.lambda_handler \
    --zip-file fileb://build/chatbot-handler.zip \
    --environment Variables="{CHAT_HISTORY_TABLE=prod-chatbot-history,FAQ_TABLE=prod-chatbot-faq,EVENT_BUS_NAME=prod-chatbot-events}" \
    --timeout 30 \
    --region ap-southeast-1
```

### 4. Seed FAQ Data
```bash
python3 -m venv venv
source venv/bin/activate
pip install boto3
python3 scripts/seed_faq.py
```

## 🧪 Testing

### Test Lambda Function Directly
```bash
# Create test payload
echo '{"body": "{\"message\": \"What are your store hours?\", \"sessionId\": \"test-123\", \"language\": \"en\"}"}' | base64 | aws lambda invoke \
    --function-name prod-chatbot-handler \
    --payload file:///dev/stdin \
    --region ap-southeast-1 \
    response.json

# View response
cat response.json
```

### Test Web Interface
Open `chatbot-interface.html` in your browser for a demo interface.

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Web Client    │───▶│ API Gateway  │───▶│ Lambda Function │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
                       ┌─────────────────────────────┼─────────────────────────────┐
                       │                             ▼                             │
                       │                    ┌─────────────────┐                    │
                       │                    │   Amazon        │                    │
                       │                    │   Bedrock       │                    │
                       │                    │   (Claude)      │                    │
                       │                    └─────────────────┘                    │
                       │                                                           │
                       ▼                                                           ▼
              ┌─────────────────┐                                        ┌─────────────────┐
              │   Amazon        │                                        │   Amazon        │
              │   Comprehend    │                                        │   Translate     │
              │   (Sentiment)   │                                        │   (Languages)   │
              └─────────────────┘                                        └─────────────────┘
                       │                                                           │
                       └─────────────────────────────┬─────────────────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │   DynamoDB      │
                                            │   Tables        │
                                            │   - Chat History│
                                            │   - FAQ Data    │
                                            └─────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │   EventBridge   │
                                            │   (Analytics)   │
                                            └─────────────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │   CloudWatch    │
                                            │   (Monitoring)  │
                                            └─────────────────┘
```

## 🔧 Configuration

### Environment Variables
- `CHAT_HISTORY_TABLE`: DynamoDB table for chat history
- `FAQ_TABLE`: DynamoDB table for FAQ data
- `EVENT_BUS_NAME`: EventBridge custom bus name

### Bedrock Models
The system uses Claude 3 Haiku for cost-effective responses. You can modify the model in `chatbot_handler.py`:

```python
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',  # Change model here
    body=body,
    contentType='application/json'
)
```

## 📈 Analytics

The system provides comprehensive analytics:

### Metrics Tracked
- Total chat interactions
- Sentiment distribution (Positive/Negative/Neutral/Mixed)
- Language usage patterns
- FAQ utilization rates
- Response times

### Viewing Analytics
```bash
# Invoke analytics function
aws lambda invoke \
    --function-name prod-analytics-handler \
    --payload '{"hours": 24}' \
    --region ap-southeast-1 \
    analytics-response.json

cat analytics-response.json
```

## 🔒 Security Features

- **Authentication**: Cognito user pools for secure access
- **IAM Roles**: Least privilege access for Lambda functions
- **Encryption**: Data encrypted at rest and in transit
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Built-in AWS service limits

## 🌍 Multi-Language Support

Supported languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- And more via Amazon Translate

## 📝 FAQ Management

### Adding New FAQs
```python
# Add to scripts/seed_faq.py
{
    'category': 'products',
    'question': 'Do you have gift cards?',
    'answer': 'Yes! We offer digital and physical gift cards in various denominations.'
}
```

### FAQ Categories
- `general`: Store information, hours, locations
- `shipping`: Delivery, costs, timeframes
- `returns`: Return policy, process
- `payment`: Payment methods, billing
- `products`: Product information, availability
- `account`: User account management

## 🚨 Error Handling

The system includes comprehensive error handling:
- Graceful fallbacks for service failures
- Detailed logging for debugging
- User-friendly error messages
- Automatic retries for transient failures

## 📊 Performance Optimization

- **Cold Start Mitigation**: Optimized Lambda functions
- **Caching**: DynamoDB caching for FAQ responses
- **Async Processing**: Event-driven architecture
- **Resource Optimization**: Right-sized Lambda memory and timeout

## 🔄 Monitoring & Maintenance

### CloudWatch Dashboards
Monitor key metrics:
- Lambda function performance
- DynamoDB read/write capacity
- Bedrock API usage
- Error rates and latencies

### Alerts
Set up CloudWatch alarms for:
- High error rates
- Unusual traffic patterns
- Service quotas approaching limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Open an issue on GitHub

## 🎯 Roadmap

- [ ] Voice integration with Amazon Polly
- [ ] Advanced analytics dashboard
- [ ] Integration with CRM systems
- [ ] A/B testing capabilities
- [ ] Advanced NLP features
- [ ] Mobile app integration

---

**Built with ❤️ using AWS AI Services**
