#!/bin/bash

# Poll planning status until complete

if [ -z "$1" ]; then
    echo "Usage: $0 <plan_id>"
    exit 1
fi

PLAN_ID=$1
API_ENDPOINT="https://hfeppdqeh0.execute-api.us-west-2.amazonaws.com/prod"
MAX_POLLS=60  # Max 5 minutes (60 * 5 seconds)
POLL_COUNT=0

echo "📊 Polling status for plan: $PLAN_ID"
echo "⏱️  Checking every 5 seconds..."
echo ""

while [ $POLL_COUNT -lt $MAX_POLLS ]; do
    # Get status
    RESPONSE=$(curl -s "$API_ENDPOINT/api/planning/$PLAN_ID/status")
    
    # Parse status
    STATUS=$(echo "$RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")
    STAGE=$(echo "$RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('current_stage', 'unknown'))" 2>/dev/null || echo "error")
    
    # Display status
    printf "\r[%s] Status: %-12s Stage: %-12s (Poll %d/%d)" \
        "$(date +%H:%M:%S)" "$STATUS" "$STAGE" $((POLL_COUNT + 1)) $MAX_POLLS
    
    # Check if completed or failed
    if [ "$STATUS" = "completed" ]; then
        echo -e "\n\n✅ Planning completed!"
        
        # Check if we have final response
        HAS_RESPONSE=$(echo "$RESPONSE" | python3 -c "import json, sys; print('final_response' in json.load(sys.stdin))" 2>/dev/null || echo "false")
        
        if [ "$HAS_RESPONSE" = "True" ]; then
            echo -e "\n📄 Final Response:"
            echo "===================="
            echo "$RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin)['final_response'])" 2>/dev/null || echo "Error parsing response"
            
            # Show processing duration
            DURATION=$(echo "$RESPONSE" | python3 -c "import json, sys; print(f\"Processing took: {json.load(sys.stdin).get('processing_duration', 'unknown')} seconds\")" 2>/dev/null || echo "")
            echo -e "\n⏱️  $DURATION"
        fi
        
        exit 0
    elif [ "$STATUS" = "failed" ]; then
        echo -e "\n\n❌ Planning failed!"
        ERROR=$(echo "$RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "Unknown error")
        echo "Error: $ERROR"
        exit 1
    fi
    
    # Wait before next poll
    sleep 5
    POLL_COUNT=$((POLL_COUNT + 1))
done

echo -e "\n\n⏱️  Timeout: Planning is taking longer than expected"
echo "Plan ID: $PLAN_ID"
echo "You can continue checking status manually"
exit 2