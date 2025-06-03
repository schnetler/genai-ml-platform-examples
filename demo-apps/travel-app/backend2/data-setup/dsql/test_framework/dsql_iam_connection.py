"""DSQL connection using IAM authentication."""

import os
import subprocess
import psycopg2
import boto3
from contextlib import contextmanager
import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class DSQLIAMConnection:
    """Direct connection to DSQL using IAM authentication."""
    
    def __init__(self):
        self.dsql_endpoint = os.environ.get('DSQL_ENDPOINT')
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.username = os.environ.get('DSQL_USER', 'admin')
        self.database = os.environ.get('DSQL_DATABASE', 'travel_planner')
        
        if not self.dsql_endpoint:
            raise ValueError("DSQL_ENDPOINT environment variable not set")
    
    def generate_auth_token(self, expires_in: int = 900) -> str:
        """Generate IAM authentication token for DSQL."""
        try:
            # Use AWS CLI to generate token
            cmd = [
                'aws', 'dsql', 'generate-db-connect-admin-auth-token',
                '--region', self.region,
                '--expires-in', str(expires_in),
                '--hostname', self.dsql_endpoint
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to generate auth token: {result.stderr}")
                raise Exception(f"Auth token generation failed: {result.stderr}")
            
            token = result.stdout.strip()
            logger.debug("Successfully generated IAM auth token")
            return token
            
        except Exception as e:
            logger.error(f"Error generating auth token: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection using IAM authentication."""
        # Generate fresh auth token
        auth_token = self.generate_auth_token()
        
        # Connect with SSL required
        conn = psycopg2.connect(
            host=self.dsql_endpoint,
            port=5432,
            database=self.database,
            user=self.username,
            password=auth_token,
            sslmode='require',
            connect_timeout=10
        )
        
        logger.info(f"Connected to Aurora DSQL at {self.dsql_endpoint}")
        
        try:
            yield conn
        finally:
            conn.close()
    
    def get_connection_params(self) -> Dict[str, any]:
        """Get connection parameters with fresh auth token."""
        auth_token = self.generate_auth_token()
        
        return {
            'host': self.dsql_endpoint,
            'port': 5432,
            'database': self.database,
            'user': self.username,
            'password': auth_token,
            'sslmode': 'require',
            'connect_timeout': 10
        }
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                logger.info(f"Connected to: {version[0]}")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


class DSQLIAMConnectionPool:
    """Connection pool manager for Aurora DSQL with IAM auth token refresh."""
    
    def __init__(self, min_conn: int = 2, max_conn: int = 10):
        self.connection_manager = DSQLIAMConnection()
        self.min_conn = min_conn
        self.max_conn = max_conn
        self._pool = []
        self._used_connections = set()
        
    def _create_connection(self):
        """Create a new connection with fresh auth token."""
        params = self.connection_manager.get_connection_params()
        return psycopg2.connect(**params)
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool."""
        conn = None
        
        try:
            # Try to get an existing connection
            if self._pool:
                conn = self._pool.pop()
                # Test if connection is still valid
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                except:
                    # Connection is stale, create new one
                    conn.close()
                    conn = self._create_connection()
            else:
                # Create new connection
                conn = self._create_connection()
            
            self._used_connections.add(conn)
            yield conn
            
        finally:
            if conn:
                self._used_connections.discard(conn)
                # Return to pool if under max
                if len(self._pool) < self.max_conn:
                    self._pool.append(conn)
                else:
                    conn.close()


def setup_dsql_iam_auth():
    """Setup script to configure IAM authentication for Aurora DSQL."""
    print("=== Aurora DSQL IAM Authentication Setup ===")
    print()
    
    # Check AWS CLI version
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        print(f"AWS CLI Version: {result.stdout.strip()}")
    except:
        print("❌ AWS CLI not found. Please install AWS CLI v2")
        return False
    
    # Test IAM credentials
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(f"✓ AWS Identity: {identity['Arn']}")
        else:
            print("❌ AWS credentials not configured")
            return False
    except Exception as e:
        print(f"❌ Failed to verify AWS credentials: {e}")
        return False
    
    # Get DSQL endpoint
    dsql_endpoint = os.environ.get('DSQL_ENDPOINT')
    if not dsql_endpoint:
        dsql_endpoint = input("Enter your Aurora DSQL endpoint: ").strip()
        os.environ['DSQL_ENDPOINT'] = dsql_endpoint
    
    print(f"\nDSQL Endpoint: {dsql_endpoint}")
    
    # Test token generation
    print("\nTesting IAM auth token generation...")
    try:
        manager = DSQLIAMConnection()
        token = manager.generate_auth_token()
        print(f"✓ Auth token generated (length: {len(token)})")
    except Exception as e:
        print(f"❌ Failed to generate auth token: {e}")
        return False
    
    # Test connection
    print("\nTesting database connection...")
    try:
        if manager.test_connection():
            print("✓ Successfully connected to Aurora DSQL!")
            
            # Get database info
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current database
                cursor.execute("SELECT current_database()")
                db = cursor.fetchone()
                print(f"  Database: {db[0]}")
                
                # Get table count
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()
                print(f"  Tables: {table_count[0]}")
                
            return True
        else:
            print("❌ Connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if setup_dsql_iam_auth():
        print("\n✅ Aurora DSQL IAM authentication is working!")
        print("\nYou can now use:")
        print("  export DSQL_CONNECTION_METHOD=iam")
        print("  export USE_AURORA_DSQL=true")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check your configuration.")
        sys.exit(1)