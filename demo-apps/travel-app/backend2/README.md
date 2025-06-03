# Travel Planner Lambda - AWS Deployment

A production-ready AWS Lambda function that provides travel planning capabilities using the strands agent framework with AWS service integrations.

## Architecture

```
Lambda Function (Python 3.12)
├── handler.py (Main orchestrator)
└── Tools
    ├── search_destinations (Knowledge Base RAG)
    ├── search_flights (Aurora DSQL ready)
    ├── search_hotels (Aurora DSQL ready)
    ├── search_activities (Hybrid search)
    └── analyze_budget (Budget calculations)
```

## AWS Resources Used

- **Bedrock Knowledge Base**
- **DSQL**: PostgreSQL-compatible distributed SQL
- **Bedrock Claude**: LLM for agent reasoning
- **Lambda**: Serverless compute
- **API Gateway**: REST API endpoint

## Project Structure

```
backend-strands-final/
├── lambda/
│   ├── handler_flat.py      # Production Lambda handler
│   ├── handler.py           # Original handler (reference)
│   ├── tools/               # Agent tools (for future use)
│   └── utils/               # Utilities (DSQL connection)
├── scripts/
│   ├── deploy.sh            # Deploy Lambda with layers
│   ├── package.sh           # Package dependencies
│   └── test.sh              # Test deployed Lambda
├── packaging/               # Build artifacts (generated)
│   ├── app.zip             # Lambda code
│   └── dependencies.zip    # Dependencies layer
└── requirements-lambda.txt  # Minimal Lambda dependencies
```

## Quick Start

### 1. Package Dependencies
```bash
./scripts/package.sh
```

### 2. Deploy to AWS
```bash
./scripts/deploy.sh
```

### 3. Test the Lambda
```bash
./scripts/test.sh "Plan a 7-day trip to Paris with $5000 budget"
```

## Environment Variables

Configure these in your Lambda environment:

- `KB_ID`: Knowledge Base ID (default: TMLXOGDYXH)
- `KB_REGION`: AWS region (default: us-west-2)
- `DSQL_ENDPOINT`: DSQL endpoint
- `DSQL_DATABASE`: Database name (default: travel_planner)
- `DSQL_USER`: Database user (default: admin)

## Testing

### Simple Query
```bash
./scripts/test.sh
```

### Complex Query
```bash
./scripts/test.sh "I need flights from NYC to Paris, a romantic hotel, and activities for a week with $5000 budget"
```

## Development

### Update Lambda Code
```bash
# Make changes to handler.py
zip -j packaging/app.zip lambda/handler.py
aws lambda update-function-code --function-name travel-planner-orchestrator --zip-file fileb://packaging/app.zip --region us-west-2
```

### Update Dependencies
```bash
# Edit requirements-lambda.txt
./scripts/package.sh
# Then redeploy with ./scripts/deploy.sh
```

### View Logs
```bash
aws logs tail /aws/lambda/travel-planner-orchestrator --follow --region us-west-2
```

## Deployment Details

- **Function Name**: travel-planner-orchestrator
- **Runtime**: Python 3.12
- **Memory**: 2048 MB
- **Timeout**: 300 seconds
- **Architecture**: x86_64
- **Handler**: handler_flat.handler