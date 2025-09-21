#!/bin/bash

# 24/7 AI Chatbot Deployment Script

set -e

ENVIRONMENT=${1:-prod}
REGION=${2:-ap-southeast-1}
STACK_NAME="${ENVIRONMENT}-chatbot-stack"

echo "Deploying chatbot to environment: $ENVIRONMENT in region: $REGION"

# Deploy CloudFormation stack
echo "Deploying infrastructure..."
aws cloudformation deploy \
    --template-file infrastructure.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --profile awsisb_IsbUsersPS-162343471173

# Get stack outputs
echo "Getting stack outputs..."
CHAT_HISTORY_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`ChatHistoryTableName`].OutputValue' \
    --output text \
    --region $REGION \
    --profile awsisb_IsbUsersPS-162343471173)

FAQ_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`FAQTableName`].OutputValue' \
    --output text \
    --region $REGION \
    --profile awsisb_IsbUsersPS-162343471173)

# Package Lambda functions
echo "Packaging Lambda functions..."
mkdir -p build
cd lambda

# Package chatbot handler
zip -r ../build/chatbot-handler.zip chatbot_handler.py
zip -r ../build/analytics-handler.zip analytics_handler.py

cd ..

# Deploy Lambda functions
echo "Deploying Lambda functions..."

# Chatbot handler
aws lambda create-function \
    --function-name "${ENVIRONMENT}-chatbot-handler" \
    --runtime python3.9 \
    --role $(aws iam get-role --role-name "${ENVIRONMENT}-chatbot-LambdaExecutionRole" --query 'Role.Arn' --output text --profile awsisb_IsbUsersPS-162343471173) \
    --handler chatbot_handler.lambda_handler \
    --zip-file fileb://build/chatbot-handler.zip \
    --environment Variables="{CHAT_HISTORY_TABLE=$CHAT_HISTORY_TABLE,FAQ_TABLE=$FAQ_TABLE,EVENT_BUS_NAME=${ENVIRONMENT}-chatbot-events}" \
    --timeout 30 \
    --region $REGION \
    --profile awsisb_IsbUsersPS-162343471173 \
    || aws lambda update-function-code \
        --function-name "${ENVIRONMENT}-chatbot-handler" \
        --zip-file fileb://build/chatbot-handler.zip \
        --region $REGION \
        --profile awsisb_IsbUsersPS-162343471173

# Analytics handler
aws lambda create-function \
    --function-name "${ENVIRONMENT}-analytics-handler" \
    --runtime python3.9 \
    --role $(aws iam get-role --role-name "${ENVIRONMENT}-chatbot-LambdaExecutionRole" --query 'Role.Arn' --output text --profile awsisb_IsbUsersPS-162343471173) \
    --handler analytics_handler.lambda_handler \
    --zip-file fileb://build/analytics-handler.zip \
    --environment Variables="{CHAT_HISTORY_TABLE=$CHAT_HISTORY_TABLE}" \
    --timeout 60 \
    --region $REGION \
    --profile awsisb_IsbUsersPS-162343471173 \
    || aws lambda update-function-code \
        --function-name "${ENVIRONMENT}-analytics-handler" \
        --zip-file fileb://build/analytics-handler.zip \
        --region $REGION \
        --profile awsisb_IsbUsersPS-162343471173

# Seed FAQ data
echo "Seeding FAQ data..."
python3 scripts/seed_faq.py

echo "Deployment completed successfully!"
echo "Chat History Table: $CHAT_HISTORY_TABLE"
echo "FAQ Table: $FAQ_TABLE"
