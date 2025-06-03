"""SSH Tunnel Manager for DSQL local development connections."""

import subprocess
import time
import psycopg2
import os
import atexit
import socket
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DSQLTunnelManager:
    """Manages SSH tunnel for DSQL connections."""
    
    _instance = None
    _tunnel_process = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one tunnel."""
        if cls._instance is None:
            cls._instance = super(DSQLTunnelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize tunnel manager."""
        if hasattr(self, '_initialized'):
            return
            
        self.bastion_host = os.environ.get('BASTION_HOST')
        self.dsql_endpoint = os.environ.get('DSQL_ENDPOINT')
        self.ssh_key_path = os.environ.get('SSH_KEY_PATH', '~/.ssh/id_rsa')
        self.local_port = self._find_free_port()
        self._initialized = True
        
        # Register cleanup on exit
        atexit.register(self.stop_tunnel)
    
    def _find_free_port(self) -> int:
        """Find a free local port for tunneling."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start_tunnel(self) -> bool:
        """Start SSH tunnel to DSQL."""
        if self._tunnel_process and self._tunnel_process.poll() is None:
            logger.info("SSH tunnel already running")
            return True
            
        if not self.bastion_host or not self.dsql_endpoint:
            logger.error("BASTION_HOST and DSQL_ENDPOINT must be set")
            return False
        
        ssh_key_path = os.path.expanduser(self.ssh_key_path)
        
        cmd = [
            'ssh', '-N', '-L',
            f'{self.local_port}:{self.dsql_endpoint}:5432',
            f'ec2-user@{self.bastion_host}',
            '-i', ssh_key_path,
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ServerAliveInterval=60',
            '-o', 'ServerAliveCountMax=3',
            '-o', 'LogLevel=ERROR'
        ]
        
        logger.info(f"Starting SSH tunnel through {self.bastion_host} on local port {self.local_port}")
        
        try:
            self._tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for tunnel to establish
            for i in range(10):
                time.sleep(1)
                if self.test_connection():
                    logger.info("✓ SSH tunnel established successfully")
                    return True
                    
            logger.error("Failed to establish SSH tunnel after 10 seconds")
            self.stop_tunnel()
            return False
            
        except Exception as e:
            logger.error(f"Failed to start SSH tunnel: {e}")
            return False
    
    def stop_tunnel(self):
        """Stop SSH tunnel."""
        if self._tunnel_process:
            logger.info("Stopping SSH tunnel...")
            self._tunnel_process.terminate()
            try:
                self._tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._tunnel_process.kill()
            self._tunnel_process = None
    
    def test_connection(self) -> bool:
        """Test connection through tunnel."""
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=self.local_port,
                database='travel_planner',
                user=os.environ.get('DSQL_USER', 'admin'),
                password=os.environ.get('DSQL_PASSWORD'),
                connect_timeout=3
            )
            conn.close()
            return True
        except:
            return False
    
    @contextmanager
    def get_connection(self):
        """Get database connection through tunnel."""
        if not self.start_tunnel():
            raise Exception("Failed to establish SSH tunnel")
            
        conn = psycopg2.connect(
            host='localhost',
            port=self.local_port,
            database='travel_planner',
            user=os.environ.get('DSQL_USER', 'admin'),
            password=os.environ.get('DSQL_PASSWORD')
        )
        
        try:
            yield conn
        finally:
            conn.close()
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for tunneled connection."""
        if not self.start_tunnel():
            raise Exception("Failed to establish SSH tunnel")
            
        return {
            'host': 'localhost',
            'port': self.local_port,
            'database': 'travel_planner',
            'user': os.environ.get('DSQL_USER', 'admin'),
            'password': os.environ.get('DSQL_PASSWORD')
        }


class DSQLDirectConnection:
    """Direct connection manager for DSQL (when in VPC)."""
    
    def __init__(self):
        self.dsql_endpoint = os.environ.get('DSQL_ENDPOINT')
        
    @contextmanager
    def get_connection(self):
        """Get direct database connection."""
        conn = psycopg2.connect(
            host=self.dsql_endpoint,
            port=5432,
            database='travel_planner',
            user=os.environ.get('DSQL_USER', 'admin'),
            password=os.environ.get('DSQL_PASSWORD'),
            sslmode='require'
        )
        
        try:
            yield conn
        finally:
            conn.close()
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for direct connection."""
        return {
            'host': self.dsql_endpoint,
            'port': 5432,
            'database': 'travel_planner',
            'user': os.environ.get('DSQL_USER', 'admin'),
            'password': os.environ.get('DSQL_PASSWORD'),
            'sslmode': 'require'
        }


def get_dsql_connection_manager():
    """Factory function to get appropriate connection manager."""
    connection_method = os.environ.get('DSQL_CONNECTION_METHOD', 'ssh_tunnel')
    
    if connection_method == 'ssh_tunnel':
        return DSQLTunnelManager()
    elif connection_method == 'ssm':
        from .ssm_connection import SSMConnectionManager
        return SSMConnectionManager()
    elif connection_method == 'direct':
        return DSQLDirectConnection()
    else:
        raise ValueError(f"Unknown connection method: {connection_method}")


# Example usage
if __name__ == "__main__":
    # Test the tunnel manager
    logging.basicConfig(level=logging.INFO)
    
    manager = get_dsql_connection_manager()
    
    try:
        with manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"Connected to: {version[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
            table_count = cursor.fetchone()
            print(f"Tables in public schema: {table_count[0]}")
            
    except Exception as e:
        print(f"Connection failed: {e}")