"""
Message templates and error descriptions for pgpycis
Supports multiple languages and check-specific messaging
"""

class Messages:
    """Security check messages and detailed descriptions"""
    
    MESSAGES_EN = {
        # Success and failure templates
        "SUCCESS": "{check_id}: {title} => SUCCESS",
        "FAILURE": "{check_id}: {title} => FAILURE",
        "WARNING": "{check_id}: {title} => WARNING",
        "ERROR": "{check_id}: {title} => ERROR",
        "INFO": "{check_id}: {title} => INFO",
        "MANUAL": "{check_id}: {title} (Manual)",
        
        # Section 1 messages
        "1.1.1": "PostgreSQL packages obtained from authorized PGDG repository",
        "1.3": "PostgreSQL systemd service is enabled and running",
        "1.4": "PostgreSQL data cluster initialized with valid version",
        "1.4.3": "Data cluster checksums are enabled for integrity verification",
        "1.4.4": "WAL files and temp files separated from PGDATA on different partition",
        "1.5": "PostgreSQL version is current and patched",
        "1.6": "PGPASSWORD environment variable not set in user profiles",
        "1.7": "PGPASSWORD not found in shell initialization files",
        
        # Section 2 messages
        "2.1": "File permissions mask set to secure defaults (0077)",
        "2.2": "Extension directory ownership and permissions appropriate",
        "2.3": "PostgreSQL command history disabled or protected",
        "2.4": "Service configuration files do not contain passwords",
        "2.5": "pg_hba.conf permissions set to 0600",
        "2.6": "Unix socket permissions appropriately restricted",
        "2.7": "PGDATA directory permissions set correctly (0700)",
        
        # Section 3 messages
        "3.1.1": "PostgreSQL logging is properly configured",
        "3.1.2": "Log destination configured for syslog or file",
        "3.1.3": "Logging collector daemon is enabled",
        "3.1.14": "Connections and disconnections are logged",
        "3.1.20": "Connection attempts are logged",
        "3.1.21": "User disconnections are logged",
        "3.2": "PostgreSQL audit extension (pgAudit) is installed",
        
        # Section 4 messages
        "4.1": "Interactive login disabled for PostgreSQL user",
        "4.3": "Excessive superuser privileges have been revoked",
        "4.8": "set_user extension installed for privilege auditing",
        
        # Section 5 messages
        "5.1": "Only secure authentication methods configured in pg_hba.conf",
        "5.2": "SSL/TLS is required for all remote connections",
        "5.5": "Superuser remote access is appropriately restricted",
        
        # Section 6 messages
        "6.1": "FIPS 140-2 compliance mode is enabled",
        "6.2": "TLS cipher suites are strong (TLS 1.2+)",
        
        # Section 7 messages
        "7.1": "Replication users have limited privileges",
        "7.2": "WAL archiving is properly configured",
        
        # Error/warning templates
        "GENERIC_ERROR": "Error executing check {check_id}: {error}",
        "DB_CONNECTION_ERROR": "Failed to connect to PostgreSQL: {error}",
        "DEPENDENCY_ERROR": "Required dependency not found: {dependency}",
    }
    
    MESSAGES_FR = {
        "SUCCESS": "{check_id}: {title} => SUCCÈS",
        "FAILURE": "{check_id}: {title} => ÉCHEC",
        # ... ajouter les traductions FR
    }
    
    MESSAGES_ZH = {
        "SUCCESS": "{check_id}: {title} => 成功",
        "FAILURE": "{check_id}: {title} => 失败",
        # ... ajouter les traductions ZH
    }
    
    def __init__(self, language="en_US"):
        """Initialize messages with specified language"""
        self.language = language
        
        if language == "en_US":
            self.messages = self.MESSAGES_EN
        elif language == "fr_FR":
            self.messages = self.MESSAGES_FR
        elif language == "zh_CN":
            self.messages = self.MESSAGES_ZH
        else:
            self.messages = self.MESSAGES_EN
    
    def get(self, key, **kwargs):
        """Get message template and format with kwargs"""
        template = self.messages.get(key, key)
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError):
            return template
    
    def format_check(self, check_id, title, status, details=""):
        """Format a check result message"""
        template = self.messages.get(status, "{check_id}: {title} => {status}")
        msg = template.format(check_id=check_id, title=title, status=status)
        if details:
            msg += f"\n  {details}"
        return msg
    
    def format_error(self, check_id, error_msg):
        """Format an error message for a failed check"""
        template = self.messages.get("GENERIC_ERROR", "Error: {error}")
        return template.format(check_id=check_id, error=error_msg)
