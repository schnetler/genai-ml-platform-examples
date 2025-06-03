#!/bin/bash

# Production test script for Travel Planner Lambda
set -e

echo "🧪 Testing Travel Planner Lambda..."

# Configuration
FUNCTION_NAME="travel-planner-orchestrator"
REGION="us-west-2"
OUTPUT_FILE="/tmp/lambda_output.json"

# Test prompt
PROMPT="${1:-What are the best destinations for a romantic getaway?}"

echo "Sending prompt: $PROMPT"
echo ""

# Invoke Lambda
/usr/local/bin/aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --cli-binary-format raw-in-base64-out \
    --payload "{\"prompt\": \"$PROMPT\"}" \
    $OUTPUT_FILE \
    --log-type Tail \
    --query 'LogResult' \
    --output text | base64 -d | tail -20

echo ""
echo "Response:"
echo "========="

# Check if jq is available
if command -v jq &> /dev/null; then
    jq -r '.' $OUTPUT_FILE
else
    cat $OUTPUT_FILE
fi

# Clean up
rm -f $OUTPUT_FILE

echo ""
echo "✅ Test complete"