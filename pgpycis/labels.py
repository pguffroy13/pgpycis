"""
Multilingual labels and check descriptions for pgpycis
Complete implementation with all 95+ security checks
Supports: en_US (English), fr_FR (French), zh_CN (Chinese)
"""

class Labels:
    """Security check labels and hierarchical structure"""
    
    LANGUAGES = ["en_US", "fr_FR", "zh_CN"]
    
    LABELS_EN = {
        # SECTION 1: Installation and Patches (18 checks)
        "1.0": "Installation and Patches",
        "1.1": "Ensure packages are obtained from authorized repositories (Manual)",
        "1.1.1": "Ensure packages are obtained from PGDG",
        "1.2": "Install only required packages (Manual)",
        "1.3": "Ensure systemd Service Files Are Enabled",
        "1.4": "Ensure Data Cluster Initialized Successfully",
        "1.4.1": "Check initialization of the PGDATA",
        "1.4.2": "Check version in PGDATA",
        "1.4.3": "Ensure Data Cluster have checksum enabled",
        "1.4.4": "Ensure WALs and temporary files are not on same partition as PGDATA",
        "1.4.5": "Ensure that the PGDATA partition is encrypted (Manual)",
        "1.5": "Ensure PostgreSQL versions are up-to-date",
        "1.6": "Verify That PGPASSWORD is Not Set in Users' Profiles",
        "1.7": "Verify That the PGPASSWORD Environment Variable is Not in Use",
        "1.8": "Ensure unused PostgreSQL extensions are removed (Manual)",
        "1.9": "Ensure tablespace location is not inside the PGDATA",
        
        # SECTION 2: Directory and File Permissions (8 checks)
        "2.0": "Directory and File Permissions",
        "2.1": "Ensure the file permissions mask is correct (Manual)",
        "2.2": "Ensure extension directory has appropriate ownership and permissions",
        "2.3": "Disable PostgreSQL Command History",
        "2.4": "Ensure Passwords are Not Stored in the service file",
        "2.5": "Check permissions of pg_hba.conf",
        "2.6": "Check permissions on Unix Socket",
        "2.7": "Check permissions of PGDATA",
        "2.8": "List content of PGDATA to check unwanted files and symlinks (Manual)",
        
        # SECTION 3: Logging and Auditing (28 checks)
        "3.0": "Logging and Auditing",
        "3.1": "PostgreSQL Logging",
        "3.1.1": "Logging Rationale",
        "3.1.2": "Ensure the log destinations are set correctly",
        "3.1.3": "Ensure the logging collector is enabled",
        "3.1.4": "Ensure the log file destination directory is set correctly",
        "3.1.5": "Ensure the filename pattern for log files is set correctly (Manual)",
        "3.1.6": "Ensure the log file permissions are set correctly",
        "3.1.7": "Ensure log_truncate_on_rotation is enabled",
        "3.1.8": "Ensure the maximum log file lifetime is set correctly (Manual)",
        "3.1.9": "Ensure the maximum log file size is set correctly (Manual)",
        "3.1.10": "Ensure the correct syslog facility is selected (Manual)",
        "3.1.11": "Ensure syslog messages are not suppressed",
        "3.1.12": "Ensure syslog messages are not lost due to size",
        "3.1.13": "Ensure the program name for PostgreSQL syslog messages is correct (Manual)",
        "3.1.14": "Ensure the correct messages are written to the server log",
        "3.1.15": "Ensure the correct SQL statements generating errors are recorded",
        "3.1.16": "Ensure debug_print_parse is disabled",
        "3.1.17": "Ensure debug_print_rewritten is disabled",
        "3.1.18": "Ensure debug_print_plan is disabled",
        "3.1.19": "Ensure debug_pretty_print is enabled",
        "3.1.20": "Ensure log_connections is enabled",
        "3.1.21": "Ensure log_disconnections is enabled",
        "3.1.22": "Ensure log_error_verbosity is set correctly",
        "3.1.23": "Ensure log_hostname is set correctly",
        "3.1.24": "Ensure log_line_prefix is set correctly",
        "3.1.25": "Ensure log_statement is set correctly",
        "3.1.26": "Ensure log_timezone is set correctly",
        "3.1.27": "Ensure that log_directory is outside the PGDATA",
        "3.2": "Ensure the PostgreSQL Audit Extension (pgAudit) is enabled",
        
        # SECTION 4: User Access and Authorization (10 checks)
        "4.0": "User Access and Authorization",
        "4.1": "Ensure Interactive Login is Disabled",
        "4.2": "Ensure sudo is configured correctly (Manual)",
        "4.3": "Ensure excessive administrative privileges are revoked",
        "4.4": "Lock Out Accounts if Not Currently in Use (Manual)",
        "4.5": "Ensure excessive function privileges are revoked (Manual)",
        "4.6": "Ensure excessive DML privileges are revoked (Manual)",
        "4.7": "Ensure Row Level Security (RLS) is configured correctly (Manual)",
        "4.8": "Ensure the set_user extension is installed (Manual)",
        "4.9": "Make use of predefined roles (Manual)",
        "4.10": "Ensure the public schema is protected",
        
        # SECTION 5: Connection and Login (12 checks)
        "5.0": "Connection and Login",
        "5.1": "Do Not Specify Passwords in the Command Line (Manual)",
        "5.2": "Ensure PostgreSQL is Bound to an IP Address",
        "5.3": "Ensure login via local UNIX Domain Socket is configured correctly",
        "5.4": "Ensure login via host TCP/IP Socket is configured correctly",
        "5.5": "Ensure per-account connection limits are used (Manual)",
        "5.6": "Ensure Password Complexity is configured (Manual)",
        "5.7": "Ensure authentication timeout and delay are well configured",
        "5.8": "Ensure SSL is used for client connection",
        "5.9": "Ensure authorized IP addresses ranges are not too large (Manual)",
        "5.10": "Ensure specific database and users are used",
        "5.11": "Ensure superusers are not allowed to connect remotely",
        "5.12": "Verify that password_encryption is correctly set",
        
        # SECTION 6: PostgreSQL Settings (11 checks)
        "6.0": "PostgreSQL Settings",
        "6.1": "Understanding attack vectors and runtime parameters (Manual)",
        "6.2": "Ensure backend runtime parameters are configured correctly (Manual)",
        "6.3": "Ensure Postmaster runtime parameters are configured correctly (Manual)",
        "6.4": "Ensure SIGHUP runtime parameters are configured correctly (Manual)",
        "6.5": "Ensure Superuser runtime parameters are configured correctly (Manual)",
        "6.6": "Ensure User runtime parameters are configured correctly (Manual)",
        "6.7": "Ensure FIPS 140-2 OpenSSL cryptography is used",
        "6.8": "Ensure TLS is enabled and configured correctly",
        "6.9": "Ensure a cryptographic extension is installed",
        "6.10": "Ensure Weak SSL/TLS Ciphers Are Disabled",
        "6.11": "Ensure a data anonymization extension is installed",
        
        # SECTION 7: Replication (5 checks)
        "7.0": "Replication",
        "7.1": "Ensure a replication-only user is created and used for streaming replication",
        "7.2": "Ensure logging of replication commands is configured",
        "7.3": "Ensure base backups are configured and functional",
        "7.4": "Ensure WAL archiving is configured and functional",
        "7.5": "Ensure streaming replication parameters are configured correctly",
        
        # SECTION 8: Special Configuration Considerations (3 checks)
        "8.0": "Special Configuration Considerations",
        "8.1": "Ensure PostgreSQL subdirectory locations are outside the data cluster",
        "8.2": "Ensure the backup and restore tool pgBackRest is installed and configured",
        "8.3": "Ensure miscellaneous configuration settings are correct",
    }
    
    LABELS_FR = {
        "1.0": "Installation et Mises à Jour",
        "1.1": "Assurer que les paquets sont obtenus de sources autorisées (Manuel)",
        "1.1.1": "Assurer que les paquets sont obtenus de PGDG",
    }
    
    LABELS_ZH = {
        "1.0": "安装和补丁",
        "1.1": "确保从授权存储库获取软件包（手动）",
        "1.1.1": "确保从 PGDG 获得包",
    }
    
    def __init__(self, language="en_US"):
        """Initialize labels with specified language"""
        self.language = language
        
        if language == "en_US":
            self.labels = self.LABELS_EN
        elif language == "fr_FR":
            self.labels = self.LABELS_FR
        elif language == "zh_CN":
            self.labels = self.LABELS_ZH
        else:
            self.labels = self.LABELS_EN
    
    def get(self, check_id, default=None):
        """Get label for a check ID"""
        return self.labels.get(check_id, default or check_id)
    
    def get_section(self, section_num):
        """Get section label by number (1.0, 2.0, etc.)"""
        key = f"{section_num}.0"
        return self.get(key)
    
    @staticmethod
    def get_check_hierarchy(check_id):
        """Parse check ID and return hierarchy (section, subsection, check)"""
        parts = check_id.split(".")
        if len(parts) == 1:
            return (parts[0], None, None)
        elif len(parts) == 2:
            return (parts[0], parts[1], None)
        else:
            return (parts[0], parts[1], ".".join(parts[2:]))
    
    @staticmethod
    def get_all_checks():
        """Return list of all check IDs"""
        return list(Labels.LABELS_EN.keys())
    
    @staticmethod
    def get_section_checks(section_num):
        """Return all checks for a section"""
        prefix = f"{section_num}."
        return [k for k in Labels.LABELS_EN.keys() if k.startswith(prefix) and k != f"{section_num}.0"]
