"""Setup script for local testing environment."""

import os
import json
import subprocess
import sys
from pathlib import Path

def setup_local_environment():
    """Setup local testing environment for AWS migration."""
    
    print("=== Setting up Local Testing Environment ===")
    
    # 1. Create necessary directories
    directories = [
        'test_framework',
        'tests',
        'lambda_functions',
        'lambda_functions/destination_expert',
        'lambda_functions/flight_specialist',
        'lambda_functions/hotel_specialist',
        'lambda_functions/activity_curator',
        'lambda_functions/budget_analyst',
        'schema',
        'migration_scripts'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    
    # 2. Create environment template
    env_template = {
        "USE_DSQL": "false",
        "DSQL_ENDPOINT": "your-dsql-cluster.cluster-xxxxx.us-east-1.dsql.amazonaws.com",
        "DSQL_USER": "admin",
        "DSQL_PASSWORD": "your-password",
        "BASTION_HOST": "optional-bastion-host-ip",
        "KNOWLEDGE_BASE_ID": "kb-xxxxx",
        "AWS_REGION": "us-east-1",
        "USE_LOCAL_MOCKS": "true"
    }
    
    env_file = Path('.env.testing')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            for key, value in env_template.items():
                f.write(f"{key}={value}\n")
        print(f"✓ Created {env_file} - Please update with your values")
    
    # 3. Create SAM template for local testing
    sam_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Description": "Travel Planner Local Testing Stack",
        
        "Globals": {
            "Function": {
                "Timeout": 300,
                "MemorySize": 1024,
                "Runtime": "python3.11",
                "Environment": {
                    "Variables": {
                        "USE_DSQL": "${USE_DSQL}",
                        "DSQL_ENDPOINT": "${DSQL_ENDPOINT}",
                        "KNOWLEDGE_BASE_ID": "${KNOWLEDGE_BASE_ID}"
                    }
                }
            }
        },
        
        "Resources": {
            "DestinationExpertFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "CodeUri": "lambda_functions/destination_expert/",
                    "Handler": "handler.lambda_handler",
                    "Events": {
                        "Api": {
                            "Type": "Api",
                            "Properties": {
                                "Path": "/destination-expert",
                                "Method": "post"
                            }
                        }
                    }
                }
            },
            
            "HealthCheckFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "InlineCode": |
                        import json
                        def lambda_handler(event, context):
                            return {
                                'statusCode': 200,
                                'body': json.dumps({'status': 'healthy'})
                            }
                    "Handler": "index.lambda_handler",
                    "Events": {
                        "Api": {
                            "Type": "Api",
                            "Properties": {
                                "Path": "/health",
                                "Method": "get"
                            }
                        }
                    }
                }
            }
        }
    }
    
    with open('template.yaml', 'w') as f:
        import yaml
        yaml.dump(sam_template, f, default_flow_style=False)
    print("✓ Created SAM template.yaml")
    
    # 4. Create test requirements
    test_requirements = """pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
psycopg2-binary>=2.9.0
boto3>=1.26.0
moto>=4.0.0
sentence-transformers>=2.2.0
numpy>=1.24.0
pyyaml>=6.0
python-dotenv>=1.0.0
"""
    
    with open('test-requirements.txt', 'w') as f:
        f.write(test_requirements)
    print("✓ Created test-requirements.txt")
    
    # 5. Create DSQL schema conversion script
    aurora_schema = """-- DSQL Schema for Travel Planner
-- PostgreSQL-compatible with JSONB support

-- Cities/Destinations table
CREATE TABLE IF NOT EXISTS cities (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    continent VARCHAR(50),
    timezone VARCHAR(50),
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    description TEXT,
    tags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create GIN index for JSONB tags
CREATE INDEX IF NOT EXISTS idx_cities_tags ON cities USING GIN(tags);

-- Airlines table
CREATE TABLE IF NOT EXISTS airlines (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hub_cities JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Hotels table
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city_code VARCHAR(10) NOT NULL REFERENCES cities(code),
    address TEXT,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    star_rating INTEGER CHECK (star_rating >= 1 AND star_rating <= 5),
    hotel_type VARCHAR(50),
    amenities JSONB,
    room_types JSONB,
    description TEXT,
    neighborhood_description TEXT,
    tags JSONB,
    base_price_min NUMERIC(10,2),
    base_price_max NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_hotels_city ON hotels(city_code);
CREATE INDEX IF NOT EXISTS idx_hotels_tags ON hotels USING GIN(tags);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    activity_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city_code VARCHAR(10) NOT NULL REFERENCES cities(code),
    location TEXT,
    category VARCHAR(100),
    description TEXT,
    duration_hours NUMERIC(4,2),
    price_adult NUMERIC(10,2),
    price_child NUMERIC(10,2),
    rating NUMERIC(3,2),
    tags JSONB,
    includes JSONB,
    available_days JSONB,
    time_slots JSONB,
    meeting_point TEXT,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activities_city ON activities(city_code);
CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category);
"""
    
    with open('schema/dsql_schema.sql', 'w') as f:
        f.write(aurora_schema)
    print("✓ Created DSQL schema")
    
    # 6. Create sample Lambda handler
    sample_handler = '''"""Sample Lambda handler for testing."""

import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for destination expert."""
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        # Check if using DSQL
        use_dsql = os.environ.get('USE_DSQL', 'false').lower() == 'true'
        
        response_text = f"Processing query: {query}"
        if use_dsql:
            response_text += " (using DSQL)"
        else:
            response_text += " (using local database)"
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': response_text,
                'query': query,
                'database': 'DSQL' if use_dsql else 'Local'
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
'''
    
    with open('lambda_functions/destination_expert/handler.py', 'w') as f:
        f.write(sample_handler)
    print("✓ Created sample Lambda handler")
    
    # 7. Create validation script
    validation_script = '''#!/bin/bash
# validate_setup.sh - Validate local testing setup

echo "=== Validating Local Testing Setup ==="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python version: $python_version"

# Check required tools
tools=("pytest" "aws" "sam" "psql")
for tool in "${tools[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "✓ $tool is installed"
    else
        echo "✗ $tool is not installed"
    fi
done

# Check environment file
if [ -f .env.testing ]; then
    echo "✓ .env.testing exists"
else
    echo "✗ .env.testing not found"
fi

# Check directories
dirs=("test_framework" "tests" "lambda_functions" "schema")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ Directory $dir exists"
    else
        echo "✗ Directory $dir missing"
    fi
done

echo "=== Setup validation complete ==="
'''
    
    with open('validate_setup.sh', 'w') as f:
        f.write(validation_script)
    os.chmod('validate_setup.sh', 0o755)
    print("✓ Created validation script")
    
    print("\n=== Setup Complete ===")
    print("\nNext steps:")
    print("1. Update .env.testing with your AWS credentials")
    print("2. Install test requirements: pip install -r test-requirements.txt")
    print("3. Run validation: ./validate_setup.sh")
    print("4. Start testing with: pytest tests/ -v")

if __name__ == "__main__":
    setup_local_environment()