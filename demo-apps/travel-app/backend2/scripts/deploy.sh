#!/bin/bash

# Deploy Lambda with layers using Python 3.12
set -e

echo "🚀 Deploying Travel Planner Lambda with layers..."

# Configuration
FUNCTION_NAME="travel-planner-orchestrator"
LAYER_NAME="${FUNCTION_NAME}-dependencies"
RUNTIME="python3.12"
HANDLER="orchestrator_wrapper.handler"
MEMORY_SIZE="2048"
TIMEOUT="300"
REGION="us-west-2"

# Environment variables
KB_ID="TMLXOGDYXH"
DSQL_ENDPOINT="ayabud2etsyifayzwduclf4uge.dsql.us-west-2.on.aws"
DSQL_DATABASE="postgres"
DSQL_USER="admin"
PLANS_TABLE_NAME="travel-planner-plans"

# Get account ID
ACCOUNT_ID=$(/usr/local/bin/aws sts get-caller-identity --query Account --output text)

# First, create/update the dependencies layer
echo "Creating dependencies layer..."
LAYER_VERSION=$(/usr/local/bin/aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "Dependencies for Travel Planner Lambda" \
    --zip-file fileb://packaging/dependencies.zip \
    --compatible-runtimes $RUNTIME \
    --region $REGION \
    --query 'LayerVersionArn' \
    --output text)

echo "Layer created: $LAYER_VERSION"

# Check if function exists
if /usr/local/bin/aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    # Update existing function
    echo "Updating existing Lambda function..."
    
    # Update code
    /usr/local/bin/aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://packaging/app.zip \
        --region $REGION
    
    # Wait for update
    echo "Waiting for code update..."
    /usr/local/bin/aws lambda wait function-updated \
        --function-name $FUNCTION_NAME \
        --region $REGION
    
    # Update configuration
    /usr/local/bin/aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --layers $LAYER_VERSION \
        --environment "Variables={KB_ID=$KB_ID,KB_REGION=$REGION,DSQL_ENDPOINT=$DSQL_ENDPOINT,DSQL_DATABASE=$DSQL_DATABASE,DSQL_USER=$DSQL_USER,PLANS_TABLE_NAME=$PLANS_TABLE_NAME}" \
        --region $REGION
        
else
    # Create new function
    echo "Creating new Lambda function..."
    
    # Ensure role exists
    ROLE_NAME="${FUNCTION_NAME}-role"
    ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
    
    if ! /usr/local/bin/aws iam get-role --role-name $ROLE_NAME --region $REGION 2>/dev/null; then
        echo "Creating IAM role..."
        
        # Create trust policy
        cat > /tmp/trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
        
        # Create role
        /usr/local/bin/aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file:///tmp/trust-policy.json \
            --region $REGION
        
        # Attach policies
        /usr/local/bin/aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
            --region $REGION
        
        # Create custom policy
        cat > /tmp/lambda-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:Retrieve",
                "bedrock:RetrieveAndGenerate"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "rds:DescribeDBClusters",
                "rds:GenerateDbAuthToken",
                "rds-db:connect"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dsql:DbConnect",
                "dsql:DbConnectAdmin",
                "dsql:GenerateDbConnectAdminAuthToken",
                "dsql:GenerateDbConnectAuthToken"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/travel-planner-plans"
        }
    ]
}
EOF
        
        /usr/local/bin/aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name "${FUNCTION_NAME}-policy" \
            --policy-document file:///tmp/lambda-policy.json \
            --region $REGION
        
        echo "Waiting for role propagation..."
        sleep 10
    fi
    
    # Create function
    /usr/local/bin/aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --memory-size $MEMORY_SIZE \
        --timeout $TIMEOUT \
        --zip-file fileb://packaging/app.zip \
        --layers $LAYER_VERSION \
        --region $REGION \
        --environment "Variables={KB_ID=$KB_ID,KB_REGION=$REGION,DSQL_ENDPOINT=$DSQL_ENDPOINT,DSQL_DATABASE=$DSQL_DATABASE,DSQL_USER=$DSQL_USER,PLANS_TABLE_NAME=$PLANS_TABLE_NAME}"
fi

# Clean up
rm -f /tmp/trust-policy.json /tmp/lambda-policy.json

echo "✅ Lambda deployment complete!"
echo ""
echo "Function: $FUNCTION_NAME"
echo "Runtime: $RUNTIME"
echo "Handler: $HANDLER"
echo "Layer: $LAYER_VERSION"
echo ""

# Test the deployment
echo "🧪 Testing deployment..."
TEST_RESULT=$(/usr/local/bin/aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload '{"prompt":"Find hotels in NYC"}' \
    --region $REGION \
    /tmp/lambda-response.json)

echo "Lambda response status: $TEST_RESULT"
echo "Response content:"
cat /tmp/lambda-response.json
echo ""

# Clean up
rm -f /tmp/lambda-response.json

echo "🎉 Deployment and test complete!"
echo ""
echo "🔧 Available commands:"
echo "  Test Lambda: /usr/local/bin/aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"prompt\":\"Find hotels in Paris\"}' /tmp/response.json"
echo "  View logs: /usr/local/bin/aws logs tail /aws/lambda/$FUNCTION_NAME --region $REGION"