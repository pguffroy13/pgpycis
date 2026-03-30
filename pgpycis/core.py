"""
Core PGPYCIS engine - Main assessment orchestrator
Handles database connection, check execution, and result aggregation
"""

import psycopg2
from psycopg2 import sql
import subprocess
import os
import sys
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from .labels import Labels
from .messages import Messages
from .report import ReportGenerator
from .netmask import NetworkValidator


class PGPYCIS:
    """Main PostgreSQL security assessment engine"""
    
    def __init__(self, user="postgres", host="localhost", port=5432, 
                 database="postgres", lang="en_US", pgdata=None):
        """Initialize PGPYCIS assessment tool"""
        self.user = user
        self.host = host
        self.port = port
        self.database = database
        self.language = lang
        self.pgdata = pgdata or self._detect_pgdata()
        
        self.labels = Labels(lang)
        self.messages = Messages(lang)
        self.report = ReportGenerator(format="text", language=lang)
        
        self.connection = None
        self.version = None
        self.is_superuser = False
        self.results = {}
        
    def _detect_pgdata(self) -> Optional[str]:
        """Auto-detect PGDATA location"""
        # Try to get from PostgreSQL cluster
        try:
            result = subprocess.run(
                ["sudo", "-u", "postgres", "psql", "-c", "SHOW data_directory"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and line != "data_directory":
                        return line
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Common locations
        for path in ["/var/lib/pgsql/data", "/var/lib/postgresql/data", 
                     "/opt/postgres/data", "/opt/postgresql/data"]:
            if os.path.isdir(path):
                return path
        
        return None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connection"""
        try:
            conn = psycopg2.connect(
                user=self.user,
                host=self.host,
                port=self.port,
                database=self.database
            )
            yield conn
        except psycopg2.Error as e:
            print(f"Database connection error: {e}", file=sys.stderr)
            raise
        finally:
            if conn:
                conn.close()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                user=self.user,
                host=self.host,
                port=self.port,
                database=self.database
            )
            return True
        except psycopg2.Error as e:
            print(f"Database connection error: {e}", file=sys.stderr)
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize(self) -> bool:
        """Initialize and validate environment"""
        if not self.connect():
            return False
        
        # Get PostgreSQL version
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT version(), current_user, usesuper FROM pg_user WHERE usename = current_user")
                result = cur.fetchone()
                if result:
                    version_str, current_user, is_superuser = result
                    self.version = version_str
                    self.is_superuser = is_superuser
                else:
                    # Fallback query
                    cur.execute("SELECT version(), current_user")
                    version_str, current_user = cur.fetchone()
                    self.version = version_str
                    cur.execute("SELECT has_database_privilege(%s, %s, 'CREATE')", (current_user, self.database))
                    self.is_superuser = cur.fetchone()[0]
                
                print(f"Connected to: {version_str}")
                print(f"Current user: {current_user}")
                print(f"Is superuser: {self.is_superuser}")
        except psycopg2.Error as e:
            print(f"Error initializing: {e}", file=sys.stderr)
            return False
        
        return True
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute a query and return results"""
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except psycopg2.Error as e:
            # Reset transaction state after error
            try:
                self.connection.rollback()
            except:
                pass
            print(f"Query error: {e}", file=sys.stderr)
            return []
    
    def get_setting(self, name: str) -> Optional[str]:
        """Get a PostgreSQL configuration setting"""
        result = self.execute_query(
            "SELECT setting FROM pg_settings WHERE name = %s",
            (name,)
        )
        return result[0][0] if result else None
    
    def run_checks(self, check_filter: Optional[str] = None) -> bool:
        """Execute all 95+ security checks"""
        if not self.is_superuser:
            print("Warning: Not running as superuser. Some checks may fail.", file=sys.stderr)
        
        # Import all checks
        from .checks import run_checks as execute_all_checks
        
        # Execute all checks
        print("\nRunning all 95+ PostgreSQL security checks...")
        all_results = execute_all_checks(self)
        
        # Organize results by section
        section_map = {
            "1": "1 - Installation and Patches",
            "2": "2 - Directory and File Permissions", 
            "3": "3 - Logging and Auditing",
            "4": "4 - User Access and Authorization",
            "5": "5 - Connection and Login",
            "6": "6 - PostgreSQL Settings",
            "7": "7 - Replication",
            "8": "8 - Special Considerations",
        }
        
        for check_id, result in all_results.items():
            # Determine section from check ID (e.g., "1.1" -> section "1")
            section_num = check_id.split(".")[0]
            section_name = section_map.get(section_num, "Other")
            
            self.report.add_result(
                check_id,
                self.labels.get(check_id),
                result.get("status", "INFO"),
                result.get("details", ""),
                section_name
            )
            self.results[check_id] = result
        
        return True
    
    def generate_report(self, format="text", output_file: Optional[str] = None) -> str:
        """Generate final report"""
        self.report.format = format
        return self.report.generate(output_file)
    
    def run(self, format="text", output_file: Optional[str] = None) -> bool:
        """Main execution method"""
        print("PGPYCIS - PostgreSQL CIS Compliance Assessment Tool")
        print("=" * 50)
        print()
        
        if not self.initialize():
            return False
        
        if not self.run_checks():
            return False
        
        report = self.generate_report(format=format, output_file=output_file)
        
        if not output_file:
            print("\n" + report)
        else:
            print(f"\nReport saved to: {output_file}")
        
        self.disconnect()
        return True
