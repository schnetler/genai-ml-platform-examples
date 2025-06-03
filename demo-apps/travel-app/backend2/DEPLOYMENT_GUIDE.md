# Travel Planner Backend - Complete Deployment Guide

This guide provides step-by-step instructions for deploying the Travel Planner backend infrastructure and services on AWS.

## Prerequisites

1. **AWS CLI v2** - Installed and configured with appropriate credentials
2. **Python 3.12** - For Lambda runtime compatibility
3. **PostgreSQL client** (`psql`) - For database setup
4. **Node.js** (optional) - If using AWS CDK for infrastructure
5. **AWS Account** with permissions for:
   - Lambda
   - API Gateway
   - DynamoDB
   - DSQL
   - Bedrock (Knowledge Base)
   - IAM

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   API Gateway   │────▶│  Proxy Lambda    │────▶│ Orchestrator    │
└─────────────────┘     └──────────────────┘     │    Lambda       │
                                                  └────────┬────────┘
                                                           │
                                                  ┌────────▼────────┐
                                                  │   Specialist    │
                                                  │     Agents      │
                                                  └────────┬────────┘
                                                           │
                              ┌────────────────────────────┼────────────────────────────┐
                              │                            │                            │
                        ┌─────▼─────┐              ┌──────▼──────┐            ┌────────▼────────┐
                        │ DynamoDB  │              │    DSQL     │            │ Bedrock         │
                        │  (Plans)  │              │ (Travel DB) │            │ Knowledge Base  │
                        └───────────┘              └─────────────┘            └─────────────────┘
```

**Specialist Agents:**
- **Flight Specialist**: Searches and recommends flights from DSQL
- **Hotel Specialist**: Finds accommodations matching preferences from DSQL  
- **Activities Curator**: Discovers experiences and attractions from DSQL
- **Destination Expert**: Provides destination insights via Bedrock Knowledge Base
- **Budget Analyst**: Tracks and optimizes travel expenses
- **Itinerary Builder**: Creates day-by-day travel plans

## Deployment Steps

### Step 1: Create DSQL Database

1. **Create DSQL Cluster** (AWS Console or CLI):
   ```bash
   # Note: DSQL cluster creation is currently only available via Console
   # Create a cluster named "travel-planner-dsql" in your preferred region
   ```

2. **Set environment variables**:
   ```bash
   
   export DSQL_ENDPOINT=your-cluster-endpoint.dsql.region.on.aws
   export AWS_REGION=us-west-2
   export DSQL_DATABASE=postgres
   export DSQL_USER=admin
   ```

3. **Setup database schema and seed data**:
   ```bash
   cd data-setup/dsql
   ./setup_dsql.sh fresh
   ```

   This will:
   - Create a Python virtual environment (if needed)
   - Install all required dependencies
   - Apply the schema (cities, hotels, activities, flight_routes, etc.)
   - Seed with sample data
   
   Note: The script automatically manages a virtual environment in `backend/venv/`

### Step 2: Create Bedrock Knowledge Base

Currently, this must be done manually through the AWS Console:

1. Navigate to Amazon Bedrock → Knowledge bases
2. Click "Create knowledge base"
3. Configure:
   - Name: `travel-planner-kb`
   - Embeddings model: `Titan Embeddings G1 - Text`
   - Vector database: `OpenSearch Serverless`

4. **Prepare and upload documents**:
   ```bash
   cd data-setup/knowledge_base
   python3 create_kb_documents.py
   # This creates JSON documents in kb_data/
   ```

5. Upload the generated documents to S3 and sync with Knowledge Base

6. Note the Knowledge Base ID (e.g., `TMLXOGDYXH`)

### Step 3: Create DynamoDB Table

```bash
# Create table for plan storage
aws dynamodb create-table \
  --table-name travel-planner-plans \
  --attribute-definitions \
    AttributeName=plan_id,AttributeType=S \
  --key-schema \
    AttributeName=plan_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $AWS_REGION
```

### Step 4: Deploy Lambda Functions

1. **Package dependencies**:
   ```bash
   cd /path/to/travel-planner/backend
   ./scripts/package.sh
   ```

2. **Deploy orchestrator Lambda**:
   ```bash
   ./scripts/deploy.sh
   ```

3. **Deploy proxy Lambda**:
   ```bash
   ./scripts/deploy_proxy.sh
   ```

4. **Update permissions**:
   ```bash
   ./scripts/update_orchestrator_permissions.sh
   ```

### Step 5: Setup API Gateway

```bash
./scripts/setup_api_gateway.sh
```

This creates REST API endpoints:
- `POST /api/planning/start`
- `POST /api/planning/continue`
- `GET /api/planning/{plan_id}/status`
- `POST /api/planning/{plan_id}/finalize`

### Step 6: Configure Environment Variables

Update Lambda environment variables:

```bash
# For orchestrator Lambda
aws lambda update-function-configuration \
  --function-name travel-planner-orchestrator \
  --environment Variables="{
    KB_ID=your-knowledge-base-id,
    KB_REGION=$AWS_REGION,
    DSQL_ENDPOINT=$DSQL_ENDPOINT,
    DSQL_DATABASE=$DSQL_DATABASE,
    DSQL_USER=$DSQL_USER,
    PLANS_TABLE_NAME=travel-planner-plans
  }" \
  --region $AWS_REGION

# For proxy Lambda (if needed)
aws lambda update-function-configuration \
  --function-name travel-planner-proxy \
  --environment Variables="{
    ORCHESTRATOR_FUNCTION_NAME=travel-planner-orchestrator
  }" \
  --region $AWS_REGION
```

## Testing the Deployment

1. **Test Lambda directly**:
   ```bash
   ./scripts/test.sh "Plan a 5-day trip to Paris with $3000 budget"
   ```

2. **Test via API Gateway**:
   ```bash
   # Get API endpoint from api_config.json after setup
   ./scripts/test_proxy.sh
   ```

3. **Test database connectivity**:
   ```bash
   cd data-setup/dsql
   ./test_dsql_direct.sh
   ```

## Monitoring and Troubleshooting

### CloudWatch Logs

View Lambda logs:
```bash
aws logs tail /aws/lambda/travel-planner-orchestrator --follow --region $AWS_REGION
aws logs tail /aws/lambda/travel-planner-proxy --follow --region $AWS_REGION
```

### Common Issues

1. **DSQL Connection Failed**
   - Verify IAM role has `dsql:GenerateDbConnectAdminAuthToken` permission
   - Check DSQL endpoint is correct
   - Ensure Lambda is in same region as DSQL cluster

2. **Knowledge Base Not Found**
   - Verify KB_ID environment variable
   - Check IAM permissions for Bedrock access

3. **DynamoDB Access Denied**
   - Run `update_orchestrator_permissions.sh` to add DynamoDB permissions
   - Verify table name in environment variables

## Security Best Practices

1. **IAM Roles**: Use least-privilege IAM roles for each Lambda
2. **DSQL Access**: Always use IAM authentication (no passwords)
3. **API Gateway**: Consider adding API keys or AWS IAM authorization
4. **Environment Variables**: Store sensitive data in AWS Secrets Manager
5. **VPC**: Consider placing Lambdas in VPC for network isolation

## Cost Optimization

1. **Lambda**: Monitor execution time and memory usage
2. **DynamoDB**: Use on-demand billing for variable workloads
3. **DSQL**: Start with minimum capacity and scale as needed
4. **API Gateway**: Use caching for frequently accessed data

## Maintenance

### Regular Tasks

1. **Update dependencies**: 
   ```bash
   # Update requirements-lambda.txt
   ./scripts/package.sh
   ./scripts/deploy.sh
   ```

2. **Database maintenance**:
   - Monitor query performance
   - Update statistics regularly
   - Review and optimize slow queries

3. **Knowledge Base updates**:
   - Sync new destination data
   - Update embeddings model if needed

### Backup and Recovery

1. **DSQL**: Automatic backups enabled by default
2. **DynamoDB**: Enable point-in-time recovery
3. **Lambda code**: Store in version control
4. **Knowledge Base**: Backup source documents in S3

## Next Steps

1. Set up CI/CD pipeline for automated deployments
2. Implement infrastructure as code (CDK/Terraform)
3. Add API authentication and rate limiting
4. Set up monitoring dashboards and alerts
5. Configure auto-scaling for high traffic