"""
Bash Check Runner - Executes shell scripts for manual security checks
Handles subprocess execution, error handling, and JSON result parsing
Supports privilege escalation for system-level checks
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class BashCheckRunner:
    """Executes bash_checks.sh and returns structured results
    
    Supports running with elevated privileges (sudo) when needed
    """
    
    def __init__(self, script_path: Optional[str] = None, pgdata: Optional[str] = None, 
                 use_sudo: bool = False, run_as_user: Optional[str] = None):
        """Initialize the Bash check runner
        
        Args:
            script_path: Path to bash_checks.sh (auto-detected if None)
            pgdata: PostgreSQL data directory (passed to bash script)
            use_sudo: If True, execute script with sudo (default: False)
            run_as_user: User to run script as (e.g., 'postgres'). Requires use_sudo=True
        """
        self.script_path = script_path or self._find_script()
        self.pgdata = pgdata
        self.use_sudo = use_sudo
        self.run_as_user = run_as_user
        self.results = {}
        
    def _find_script(self) -> str:
        """Locate bash_checks.sh in the pgpycis package"""
        # Try different paths
        possible_paths = [
            Path(__file__).parent / "bash_checks.sh",
            Path(__file__).parent.parent.parent / "pgpycis" / "checks" / "bash_checks.sh",
            Path("/home/pguffroy13/DEV/pgpycis/pgpycis/checks/bash_checks.sh"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError("Could not locate bash_checks.sh")
    
    def run(self) -> Dict[str, Dict[str, str]]:
        """Execute bash_checks.sh and parse results
        
        Can run with or without sudo based on configuration
        
        Returns:
            Dictionary with check_id -> {status, details}
        """
        try:
            # Make script executable
            os.chmod(self.script_path, 0o755)
            
            # Build command
            cmd = []
            
            # Add sudo if requested
            if self.use_sudo:
                cmd.append("sudo")
                if self.run_as_user:
                    cmd.extend(["-u", self.run_as_user])
            
            # Add script and arguments
            cmd.extend(["/bin/bash", self.script_path])
            if self.pgdata:
                cmd.append(self.pgdata)
            
            # Execute script
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                if result.stderr:
                    print(f"Bash checks warning: {result.stderr}", file=sys.stderr)
                # Continue anyway - errors might be permission-related
            
            # Parse JSON output
            if result.stdout:
                try:
                    self.results = json.loads(result.stdout)
                except json.JSONDecodeError as e:
                    print(f"Error parsing bash results JSON: {e}", file=sys.stderr)
                    print(f"Output was: {result.stdout[:500]}", file=sys.stderr)
                    self.results = self._parse_error_output(result.stdout)
            
            return self.results
            
        except subprocess.TimeoutExpired:
            print("Bash checks timed out after 60 seconds", file=sys.stderr)
            return {}
        except Exception as e:
            print(f"Error running bash checks: {e}", file=sys.stderr)
            return {}
    
    def _parse_error_output(self, output: str) -> Dict[str, Dict[str, str]]:
        """Fallback parser if JSON parsing fails"""
        # Return empty dict - the all_checks.py will use MANUAL defaults
        return {}
    
    def get_result(self, check_id: str) -> Optional[Dict[str, str]]:
        """Get result for a specific check"""
        return self.results.get(check_id)
    
    def merge_with_python_results(self, python_results: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        """Merge bash results with python results
        
        Bash results override python MANUAL results
        """
        merged = python_results.copy()
        
        for check_id, bash_result in self.results.items():
            # Only override if the python result was MANUAL or INFO
            if check_id in merged:
                if merged[check_id].get("status") in ("MANUAL", "INFO"):
                    merged[check_id] = bash_result
            else:
                merged[check_id] = bash_result
        
        return merged


def safe_run_bash_checks(pgpycis=None, run_as_root: bool = False) -> Dict[str, Dict[str, str]]:
    """Safely execute bash checks with error handling
    
    Args:
        pgpycis: PGPYCIS instance (for PGDATA detection)
        run_as_root: If True, execute bash script with sudo
        
    Returns:
        Dictionary of check results, or empty dict on error
    """
    try:
        pgdata = None
        if pgpycis and hasattr(pgpycis, 'pgdata'):
            pgdata = pgpycis.pgdata
        
        # Determine if we need sudo
        is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        use_sudo = run_as_root and not is_root
        
        runner = BashCheckRunner(
            pgdata=pgdata, 
            use_sudo=use_sudo,
            run_as_user=None  # Don't switch users unless needed
        )
        return runner.run()
    except Exception as e:
        print(f"Warning: Could not run bash checks: {e}", file=sys.stderr)
        return {}
