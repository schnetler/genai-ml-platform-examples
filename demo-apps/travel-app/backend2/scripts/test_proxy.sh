#!/bin/bash

# Test script for the proxy Lambda solution
# Tests both direct Lambda invocation and API Gateway endpoints

set -e

echo "🧪 Testing Travel Planner Proxy Solution..."

# Configuration
PROXY_FUNCTION_NAME="travel-planner-proxy"
REGION="${AWS_REGION:-us-west-2}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to pretty print JSON
pretty_json() {
    echo "$1" | python3 -m json.tool 2>/dev/null || echo "$1"
}

# Test 1: Direct Lambda invocation
echo ""
echo "📝 Test 1: Direct Lambda Invocation - Start Planning"
echo "================================================"

# Create test event for direct invocation
cat > /tmp/test-event.json <<EOF
{
  "path": "/api/planning/start",
  "httpMethod": "POST",
  "headers": {},
  "body": "{\"user_goal\": \"I want to visit Paris for 5 days\", \"user_id\": \"test-user\"}"
}
EOF

echo "Request:"
pretty_json "$(cat /tmp/test-event.json)"

RESPONSE=$(aws lambda invoke \
    --function-name $PROXY_FUNCTION_NAME \
    --payload file:///tmp/test-event.json \
    --region $REGION \
    /tmp/response.json \
    --output text \
    --query 'StatusCode')

echo -e "\nLambda Status Code: $RESPONSE"
echo -e "\nResponse:"
pretty_json "$(cat /tmp/response.json)"

# Extract plan_id from response
PLAN_ID=$(cat /tmp/response.json | python3 -c "import json, sys; data = json.load(sys.stdin); body = json.loads(data['body']); print(body.get('plan_id', ''))" 2>/dev/null || echo "")

if [ -n "$PLAN_ID" ]; then
    echo -e "\n${GREEN}✅ Test 1 PASSED${NC} - Plan created with ID: $PLAN_ID"
else
    echo -e "\n${RED}❌ Test 1 FAILED${NC} - No plan_id in response"
fi

# Test 2: API Gateway endpoints (if configured)
if [ -f api_config.json ]; then
    echo ""
    echo "📝 Test 2: API Gateway Endpoints"
    echo "================================"
    
    API_ENDPOINT=$(cat api_config.json | python3 -c "import json, sys; print(json.load(sys.stdin)['api_endpoint'])")
    
    echo "API Endpoint: $API_ENDPOINT"
    
    # Test 2a: Start planning via API
    echo -e "\n${YELLOW}Test 2a: POST /api/planning/start${NC}"
    
    API_RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/planning/start" \
        -H "Content-Type: application/json" \
        -d '{"user_goal": "I want to explore Tokyo for a week", "user_id": "api-test-user"}')
    
    echo "Response:"
    pretty_json "$API_RESPONSE"
    
    API_PLAN_ID=$(echo "$API_RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('plan_id', ''))" 2>/dev/null || echo "")
    
    if [ -n "$API_PLAN_ID" ]; then
        echo -e "${GREEN}✅ Test 2a PASSED${NC} - Plan created with ID: $API_PLAN_ID"
        
        # Test 2b: Get status
        echo -e "\n${YELLOW}Test 2b: GET /api/planning/{plan_id}/status${NC}"
        
        STATUS_RESPONSE=$(curl -s "$API_ENDPOINT/api/planning/$API_PLAN_ID/status")
        echo "Response:"
        pretty_json "$STATUS_RESPONSE"
        
        if echo "$STATUS_RESPONSE" | grep -q "plan_id"; then
            echo -e "${GREEN}✅ Test 2b PASSED${NC}"
        else
            echo -e "${RED}❌ Test 2b FAILED${NC}"
        fi
        
        # Test 2c: Continue planning
        echo -e "\n${YELLOW}Test 2c: POST /api/planning/continue${NC}"
        
        CONTINUE_RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/planning/continue" \
            -H "Content-Type: application/json" \
            -d "{\"plan_id\": \"$API_PLAN_ID\", \"user_input\": \"I prefer budget hotels near train stations\"}")
        
        echo "Response:"
        pretty_json "$CONTINUE_RESPONSE"
        
        if echo "$CONTINUE_RESPONSE" | grep -q "success"; then
            echo -e "${GREEN}✅ Test 2c PASSED${NC}"
        else
            echo -e "${RED}❌ Test 2c FAILED${NC}"
        fi
        
        # Test 2d: Finalize plan
        echo -e "\n${YELLOW}Test 2d: POST /api/planning/{plan_id}/finalize${NC}"
        
        FINALIZE_RESPONSE=$(curl -s -X POST "$API_ENDPOINT/api/planning/$API_PLAN_ID/finalize")
        echo "Response:"
        pretty_json "$FINALIZE_RESPONSE"
        
        if echo "$FINALIZE_RESPONSE" | grep -q "success"; then
            echo -e "${GREEN}✅ Test 2d PASSED${NC}"
        else
            echo -e "${RED}❌ Test 2d FAILED${NC}"
        fi
        
    else
        echo -e "${RED}❌ Test 2a FAILED${NC} - No plan_id in response"
    fi
else
    echo -e "\n${YELLOW}⚠️  API Gateway not configured. Run ./scripts/setup_api_gateway.sh first.${NC}"
fi

# Test 3: Error handling
echo ""
echo "📝 Test 3: Error Handling"
echo "========================"

# Test invalid endpoint
echo -e "\n${YELLOW}Test 3a: Invalid endpoint${NC}"
cat > /tmp/test-invalid.json <<EOF
{
  "path": "/api/invalid/endpoint",
  "httpMethod": "GET",
  "headers": {},
  "body": "{}"
}
EOF

INVALID_RESPONSE=$(aws lambda invoke \
    --function-name $PROXY_FUNCTION_NAME \
    --payload file:///tmp/test-invalid.json \
    --region $REGION \
    /tmp/invalid-response.json \
    --output text \
    --query 'StatusCode')

echo "Response:"
pretty_json "$(cat /tmp/invalid-response.json)"

if cat /tmp/invalid-response.json | grep -q "404"; then
    echo -e "${GREEN}✅ Test 3a PASSED${NC} - Returned 404 for invalid endpoint"
else
    echo -e "${RED}❌ Test 3a FAILED${NC} - Should return 404"
fi

# Test missing parameters
echo -e "\n${YELLOW}Test 3b: Missing required parameters${NC}"
cat > /tmp/test-missing-params.json <<EOF
{
  "path": "/api/planning/start",
  "httpMethod": "POST",
  "headers": {},
  "body": "{}"
}
EOF

MISSING_PARAMS_RESPONSE=$(aws lambda invoke \
    --function-name $PROXY_FUNCTION_NAME \
    --payload file:///tmp/test-missing-params.json \
    --region $REGION \
    /tmp/missing-params-response.json \
    --output text \
    --query 'StatusCode')

echo "Response:"
pretty_json "$(cat /tmp/missing-params-response.json)"

if cat /tmp/missing-params-response.json | grep -q "400"; then
    echo -e "${GREEN}✅ Test 3b PASSED${NC} - Returned 400 for missing parameters"
else
    echo -e "${RED}❌ Test 3b FAILED${NC} - Should return 400"
fi

# Cleanup
rm -f /tmp/test-event.json /tmp/response.json /tmp/test-invalid.json /tmp/invalid-response.json /tmp/test-missing-params.json /tmp/missing-params-response.json

echo ""
echo "🏁 Testing complete!"