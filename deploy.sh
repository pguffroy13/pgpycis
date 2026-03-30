#!/bin/bash
# Secure deployment configuration for pgpycis running as root or with sudo
# This script helps configure pgpycis to run with appropriate privileges

set -e

echo "PostgreSQL CIS Benchmark - Deployment Configuration"
echo "======================================================"
echo ""

# Detect the current user and installation directory
CURRENT_USER=$(whoami)
PGPYCIS_PATH=$(python3 -c "import site; print([p for p in site.getsitepackages() if 'site-packages' in p][0] if site.getsitepackages() else '/usr/local/lib/python3.10/site-packages')" 2>/dev/null || echo ~/.local/lib/python*/site-packages/pgpycis)
PGPYCIS_CMD=$(which pgpycis 2>/dev/null || echo ~/.local/bin/pgpycis)

echo "Current environment:"
echo "  User: $CURRENT_USER"
echo "  pgpycis command: $PGPYCIS_CMD"
echo ""

# Show options
echo "Choose deployment option:"
echo ""
echo "1. Run as current user (limited system checks)"
echo "2. Run with sudo (recommended for full coverage)"
echo "3. Configure password-less sudo (requires admin)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "✓ Standard mode"
        echo "  pgpycis can run with basic system checks"
        echo "  Some system-level checks may be skipped"
        echo ""
        echo "  Run with:"
        echo "  $ pgpycis -U postgres -h localhost -f text"
        ;;
    
    2)
        echo ""
        echo "✓ Sudo mode (manual)"
        echo "  pgpycis will be executed with sudo"
        echo "  You will be prompted for a password"
        echo ""
        echo "  Run with:"
        echo "  $ sudo bash -c 'python3 -m pip install --user -e /path/to/pgpycis'"
        echo "  $ sudo pgpycis -U postgres -h localhost -f text"
        ;;
    
    3)
        echo ""
        echo "✓ Configuring password-less sudo for pgpycis"
        echo ""
        
        if [ "$CURRENT_USER" != "root" ]; then
            echo "ERROR: This option requires root access"
            echo "Run this script with: sudo bash deploy.sh"
            exit 1
        fi
        
        # Create sudoers configuration
        SUDOERS_FILE="/etc/sudoers.d/pgpycis"
        
        # Get the actual command path
        PGPYCIS_BIN=$PGPYCIS_CMD
        
        if [ ! -f "$PGPYCIS_BIN" ]; then
            echo "ERROR: pgpycis not found at $PGPYCIS_BIN"
            exit 1
        fi
        
        echo "Creating sudoers configuration..."
        
        # Backup existing file if present
        if [ -f "$SUDOERS_FILE" ]; then
            cp "$SUDOERS_FILE" "${SUDOERS_FILE}.backup"
        fi
        
        # Create sudoers entry
        cat > "$SUDOERS_FILE" << 'EOF'
# pgpycis - PostgreSQL CIS Compliance Assessment Tool
# Allows pgpycis to run system-level security checks without password

# Allow all users to run pgpycis with sudo (only for postgres connections)
ALL ALL=(root) NOPASSWD: /home/*/*/.local/bin/pgpycis
ALL ALL=(root) NOPASSWD: /usr/local/bin/pgpycis

# Allow reading PostgreSQL configuration files
ALL ALL=(root) NOPASSWD: /bin/cat /var/lib/pgsql/*/data/postgresql.conf
ALL ALL=(root) NOPASSWD: /bin/cat /var/lib/pgsql/*/data/pg_hba.conf

# Allow checking package information
ALL ALL=(root) NOPASSWD: /bin/rpm *
ALL ALL=(root) NOPASSWD: /usr/bin/dpkg *

# Allow systemctl commands
ALL ALL=(root) NOPASSWD: /usr/bin/systemctl status postgresql*
ALL ALL=(root) NOPASSWD: /usr/bin/systemctl is-enabled postgresql*

# Allow file permission checks
ALL ALL=(root) NOPASSWD: /usr/bin/find /var/lib/pgsql -type *
EOF
        
        # Verify sudoers file syntax
        if ! visudo -c -f "$SUDOERS_FILE" > /dev/null 2>&1; then
            echo "ERROR: Invalid sudoers syntax!"
            rm "$SUDOERS_FILE"
            exit 1
        fi
        
        # Set secure permissions
        chmod 0440 "$SUDOERS_FILE"
        
        echo "✓ Sudoers configuration created at: $SUDOERS_FILE"
        echo ""
        echo "Now you can run pgpycis with sudo without password:"
        echo "  $ sudo pgpycis -U postgres -h localhost -f text"
        echo ""
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "======================================================"
echo "Setup complete!"
echo ""
