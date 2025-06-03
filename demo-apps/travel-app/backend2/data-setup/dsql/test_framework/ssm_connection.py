"""AWS Systems Manager Session Manager connection for DSQL."""

import subprocess
import json
import time
import os
import atexit
from contextlib import contextmanager
import psycopg2
import logging

logger = logging.getLogger(__name__)

class SSMConnectionManager:
    """Manages port forwarding through SSM Session Manager."""
    
    def __init__(self):
        self.instance_id = os.environ.get('SSM_INSTANCE_ID')
        self.dsql_endpoint = os.environ.get('DSQL_ENDPOINT')
        self.local_port = 5432
        self.session_process = None
        
        if not self.instance_id:
            raise ValueError("SSM_INSTANCE_ID environment variable not set")
        if not self.dsql_endpoint:
            raise ValueError("DSQL_ENDPOINT environment variable not set")
            
        # Register cleanup
        atexit.register(self.stop_session)
    
    def start_session(self) -> bool:
        """Start SSM port forwarding session."""
        if self.session_process and self.session_process.poll() is None:
            logger.info("SSM session already running")
            return True
        
        # Build SSM command
        parameters = {
            "host": [self.dsql_endpoint],
            "portNumber": ["5432"],
            "localPortNumber": [str(self.local_port)]
        }
        
        cmd = [
            'aws', 'ssm', 'start-session',
            '--target', self.instance_id,
            '--document-name', 'AWS-StartPortForwardingSessionToRemoteHost',
            '--parameters', json.dumps(parameters),
            '--region', os.environ.get('AWS_REGION', 'us-east-1')
        ]
        
        logger.info(f"Starting SSM session to {self.instance_id}")
        
        try:
            self.session_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait for session to establish
            for i in range(15):
                time.sleep(1)
                if self.test_connection():
                    logger.info("✓ SSM port forwarding established")
                    return True
            
            logger.error("Failed to establish SSM session after 15 seconds")
            self.stop_session()
            return False
            
        except Exception as e:
            logger.error(f"Failed to start SSM session: {e}")
            return False
    
    def stop_session(self):
        """Stop SSM session."""
        if self.session_process:
            logger.info("Stopping SSM session...")
            self.session_process.terminate()
            try:
                self.session_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.session_process.kill()
            self.session_process = None
    
    def test_connection(self) -> bool:
        """Test database connection through SSM."""
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
        """Get database connection through SSM port forwarding."""
        if not self.start_session():
            raise Exception("Failed to establish SSM session")
        
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
        """Get connection parameters for SSM forwarded connection."""
        if not self.start_session():
            raise Exception("Failed to establish SSM session")
        
        return {
            'host': 'localhost',
            'port': self.local_port,
            'database': 'travel_planner',
            'user': os.environ.get('DSQL_USER', 'admin'),
            'password': os.environ.get('DSQL_PASSWORD')
        }


def check_ssm_prerequisites() -> bool:
    """Check if SSM prerequisites are met."""
    checks = []
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True)
        checks.append(('AWS CLI', result.returncode == 0))
    except:
        checks.append(('AWS CLI', False))
    
    # Check Session Manager plugin
    try:
        result = subprocess.run(['session-manager-plugin'], capture_output=True)
        checks.append(('Session Manager Plugin', True))
    except:
        checks.append(('Session Manager Plugin', False))
    
    # Check AWS credentials
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True
        )
        checks.append(('AWS Credentials', result.returncode == 0))
    except:
        checks.append(('AWS Credentials', False))
    
    # Check instance accessibility
    instance_id = os.environ.get('SSM_INSTANCE_ID')
    if instance_id:
        try:
            result = subprocess.run(
                ['aws', 'ssm', 'describe-instance-information',
                 '--instance-information-filter-list',
                 f'key=InstanceIds,valueSet={instance_id}'],
                capture_output=True
            )
            data = json.loads(result.stdout)
            instance_found = len(data.get('InstanceInformationList', [])) > 0
            checks.append(('SSM Instance', instance_found))
        except:
            checks.append(('SSM Instance', False))
    
    # Print results
    print("SSM Prerequisites Check:")
    print("-" * 40)
    all_passed = True
    for check, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check}")
        if not passed:
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    # Test SSM connection
    logging.basicConfig(level=logging.INFO)
    
    if not check_ssm_prerequisites():
        print("\nPlease install missing prerequisites:")
        print("- AWS CLI: https://aws.amazon.com/cli/")
        print("- Session Manager Plugin: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html")
        exit(1)
    
    print("\nTesting SSM connection...")
    try:
        manager = SSMConnectionManager()
        with manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"\n✓ Connected to DSQL via SSM: {version[0]}")
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")