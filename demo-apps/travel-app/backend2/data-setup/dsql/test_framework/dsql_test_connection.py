"""DSQL test connection framework for local testing."""

import os
import psycopg2
import pytest
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager
import subprocess
import time

logger = logging.getLogger(__name__)

class DSQLTestFramework:
    """Framework for testing DSQL from local environment."""
    
    def __init__(self, use_tunnel: bool = True):
        self.use_tunnel = use_tunnel
        self.connection = None
        self.tunnel_process = None
        
    def setup_ssh_tunnel(self) -> Optional[subprocess.Popen]:
        """Setup SSH tunnel to DSQL via bastion host."""
        bastion_host = os.environ.get('BASTION_HOST')
        if not bastion_host:
            logger.warning("No BASTION_HOST set, attempting direct connection")
            return None
            
        dsql_endpoint = os.environ['DSQL_ENDPOINT']
        
        # Create SSH tunnel command
        tunnel_cmd = [
            'ssh', '-N', '-L',
            f'5432:{dsql_endpoint}:5432',
            f'ec2-user@{bastion_host}',
            '-o', 'StrictHostKeyChecking=no'
        ]
        
        logger.info(f"Creating SSH tunnel through {bastion_host}")
        tunnel_process = subprocess.Popen(tunnel_cmd)
        
        # Wait for tunnel to establish
        time.sleep(2)
        
        return tunnel_process
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for local testing."""
        if self.use_tunnel:
            # Connect through SSH tunnel
            return {
                'host': '127.0.0.1',
                'port': 5432,
                'database': 'travel_planner',
                'user': os.environ.get('DSQL_USER', 'postgres'),
                'password': os.environ.get('DSQL_PASSWORD'),
                'connect_timeout': 10
            }
        else:
            # Direct connection (if DSQL is publicly accessible for testing)
            return {
                'host': os.environ['DSQL_ENDPOINT'],
                'port': 5432,
                'database': 'travel_planner',
                'user': os.environ.get('DSQL_USER', 'postgres'),
                'password': os.environ.get('DSQL_PASSWORD'),
                'sslmode': 'require',
                'connect_timeout': 10
            }
    
    @contextmanager
    def connect(self):
        """Context manager for database connections."""
        if self.use_tunnel and not self.tunnel_process:
            self.tunnel_process = self.setup_ssh_tunnel()
        
        try:
            self.connection = psycopg2.connect(**self.get_connection_params())
            yield self.connection
        finally:
            if self.connection:
                self.connection.close()
            if self.tunnel_process:
                self.tunnel_process.terminate()
                self.tunnel_process = None
    
    def test_connection(self) -> bool:
        """Test basic connection to DSQL."""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                logger.info(f"Connected to DSQL: {version[0]}")
                
                # Test DSQL specific features
                cursor.execute("SELECT aurora_version()")
                aurora_version = cursor.fetchone()
                logger.info(f"DSQL version: {aurora_version[0]}")
                
                return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def validate_schema(self, schema_file: str) -> bool:
        """Validate that schema was created correctly."""
        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            with self.connect() as conn:
                cursor = conn.cursor()
                
                # Split and execute statements separately
                statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
                
                for statement in statements:
                    if statement:
                        cursor.execute(statement)
                
                conn.commit()
                logger.info("Schema created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Schema creation failed: {e}")
            return False
    
    def check_tables(self) -> Dict[str, int]:
        """Check tables and row counts."""
        table_info = {}
        
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """)
                
                tables = cursor.fetchall()
                
                for (table_name,) in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    table_info[table_name] = count
                    
                logger.info(f"Found {len(table_info)} tables")
                for table, count in table_info.items():
                    logger.info(f"  {table}: {count} rows")
                    
        except Exception as e:
            logger.error(f"Failed to check tables: {e}")
            
        return table_info
    
    def test_performance(self, query: str, expected_time: float = 1.0) -> bool:
        """Test query performance."""
        import time
        
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                
                # Warm up
                cursor.execute("SELECT 1")
                
                # Test query
                start = time.time()
                cursor.execute(query)
                results = cursor.fetchall()
                duration = time.time() - start
                
                logger.info(f"Query executed in {duration:.3f} seconds")
                logger.info(f"Returned {len(results)} rows")
                
                return duration < expected_time
                
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return False