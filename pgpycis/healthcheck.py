"""
Health check utilities for pgpycis
Verifies prerequisites before running compliance assessments
"""

import subprocess
import sys
import os
from typing import Optional, Tuple


def get_postgres_service() -> Optional[str]:
    """
    Detect the active PostgreSQL service name
    
    Returns:
        Service name (e.g., 'postgresql-18.service') or None if not found
    """
    try:
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'postgresql' in line and '.service' in line:
                    # Extract service name from systemctl output
                    service_name = line.split()[0]
                    return service_name
    
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    return None


def check_postgres_service(host: str = "localhost", port: int = 5432) -> Tuple[bool, str]:
    """
    Verify that PostgreSQL service is running and responding
    
    Args:
        host: PostgreSQL server host
        port: PostgreSQL server port
    
    Returns:
        Tuple of (is_running, message)
    """
    
    # First, detect and check the service
    service = get_postgres_service()
    
    if service:
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return False, f"PostgreSQL service '{service}' is not running. " \
                       f"Start it with: sudo systemctl start {service}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    # Find pg_isready in common PostgreSQL installation paths
    pg_isready_paths = [
        "/usr/bin/pg_isready",
        "/usr/local/bin/pg_isready",
        "/usr/pgsql-18/bin/pg_isready",
        "/usr/pgsql-17/bin/pg_isready",
        "/usr/pgsql-16/bin/pg_isready",
        "/usr/pgsql-15/bin/pg_isready",
    ]
    
    pg_isready_cmd = None
    for path in pg_isready_paths:
        if os.path.isfile(path):
            pg_isready_cmd = path
            break
    
    # Try to connect to PostgreSQL
    try:
        cmd = pg_isready_cmd or "pg_isready"
        result = subprocess.run(
            [cmd, "-h", host, "-p", str(port)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return True, "PostgreSQL is running and responding"
        else:
            service_info = f" (service: {service})" if service else ""
            return False, f"PostgreSQL is not responding on {host}:{port}{service_info}. " \
                   f"Check that the server is running and accessible."
    
    except subprocess.TimeoutExpired:
        return False, f"PostgreSQL health check timed out on {host}:{port}"
    except FileNotFoundError:
        return False, "pg_isready utility not found. Install postgresql-client package."


def verify_postgres_connection(user: str, host: str, port: int, 
                               database: str) -> Tuple[bool, str]:
    """
    Verify actual database connection can be established
    
    Args:
        user: PostgreSQL username
        host: PostgreSQL server host
        port: PostgreSQL server port
        database: Database name
    
    Returns:
        Tuple of (can_connect, message)
    """
    try:
        import psycopg2
        from psycopg2 import Error
    except ImportError:
        return False, "psycopg2 module not found. Install it with: pip install psycopg2-binary"
    
    try:
        conn = psycopg2.connect(
            user=user,
            host=host,
            port=port,
            database=database,
            connect_timeout=5
        )
        conn.close()
        return True, f"Successfully connected to PostgreSQL as '{user}'"
    except Error as e:
        return False, f"Failed to connect to PostgreSQL: {e}"
