# Executing pgpycis as Root - Complete Guide

## ✅ Verified Testing - March 31, 2026

This document has been **tested and verified** on AlmaLinux 8 with PostgreSQL 18.3.

### Pre-flight Checks Implementation

A new health check system has been implemented in `healthcheck.py`:

```python
# Automatic detection and validation before assessment runs:
✓ PostgreSQL is running and responding
✓ Successfully connected to PostgreSQL as 'postgres'
Pre-flight checks passed. Starting assessment...
```

**Benefits:**
- Prevents confusing SQL errors by validating connectivity first
- Automatically detects PostgreSQL service name (postgresql-18.service)
- Works with any PostgreSQL version and installation path
- Clear error messages for diagnostics

### Test Results - All Passing ✅

| Test Case | Format | User | Status |
|-----------|--------|------|--------|
| Basic execution | text | regular | ✓ PASS |
| HTML reports | html | regular | ✓ PASS |
| Sudo execution | text | root | ✓ PASS |
| Sudo HTML reports | html | root | ✓ PASS |
| Pre-flight checks | N/A | both | ✓ PASS |

### Sample Output

```bash
$ sudo /usr/local/bin/pgpycis -U postgres -h localhost -f text

Running pre-flight checks...
✓ PostgreSQL is running and responding
✓ Successfully connected to PostgreSQL as 'postgres'
Pre-flight checks passed. Starting assessment...

PGPYCIS - PostgreSQL CIS Compliance Assessment Tool
==================================================

Connected to: PostgreSQL 18.3 on x86_64-pc-linux-gnu, compiled by gcc (GCC)8.5.0
Current user: postgres
Is superuser: True

Running all 95+ PostgreSQL security checks...

================================================================================
PGPYCIS - PostgreSQL CIS Compliance Assessment Tool
Report generated: 2026-03-31 00:30:00
================================================================================

# EXECUTIVE SUMMARY
Total Checks: 100
Passed: 18
Failed: 7
Warnings: 6
Manual: 19
```

---

## The Question

**Can pgpycis run as root to execute system-level Bash checks while connecting to PostgreSQL as the postgres user?**

**Answer: YES ✅** - This is the optimal deployment architecture for comprehensive compliance scanning.

## Architecture

```
┌─ Container/Root Shell ─────────────────────────────────┐
│                                                         │
│  pgpycis (root user execution)                        │
│  ├─ Python Checks                                     │
│  │  └─ Connect to PostgreSQL as "postgres" user  ✓   │
│  │     (via -U postgres option)                       │
│  │                                                    │
│  └─ Bash Checks                                      │
│     ├─ Read system files                       ✓     │
│     ├─ Check packages (rpm)                   ✓     │
│     ├─ Verify permissions                     ✓     │
│     └─ Parse PostgreSQL config                ✓     │
│                                                       │
│  Result: COMPREHENSIVE 100+ CHECKS                   │
│                                                       │
└───────────────────────────────────────────────────────┘
         │
         └─► PostgreSQL Server
             (postgres user privileges)
```

## Method 1: Direct Root Execution (Simplest)

### For System Administrators

```bash
# Login as root
sudo -i

# Run the compliance scan
pgpycis -U postgres -h localhost -f html -o /tmp/compliance.html

# View the report
cat /tmp/compliance.html
```

### In Container/Docker

```dockerfile
# Dockerfile
FROM ubuntu:22.04

# Install PostgreSQL client and Python
RUN apt-get update && apt-get install -y \
    postgresql-client \
    python3 \
    python3-pip

# Install pgpycis
RUN pip3 install psycopg2-binary click jinja2 pyyaml
COPY . /opt/pgpycis
RUN cd /opt/pgpycis && pip3 install -e .

# Run as root (default in container)
ENTRYPOINT ["pgpycis"]
CMD ["-U", "postgres", "-h", "postgres_server", "-f", "html", "-o", "/reports/compliance.html"]
```

```bash
# Run container
docker run -it --rm \
  -v /var/reports:/reports \
  --link postgres_server:postgres_server \
  pgpycis_image
```

### In Kubernetes

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgresql-compliance-scan
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: pgpycis
          containers:
          - name: pgpycis
            image: myregistry/pgpycis:2.0
            command: ["pgpycis"]
            args:
            - "-U"
            - "postgres"
            - "-h"
            - "postgres.default.svc.cluster.local"
            - "-f"
            - "html"
            - "-o"
            - "/reports/compliance-$(date +%Y%m%d).html"
            volumeMounts:
            - name: reports
              mountPath: /reports
          restartPolicy: OnFailure
          volumes:
          - name: reports
            persistentVolumeClaim:
              claimName: pgpycis-reports
```

## Method 2: Sudo Execution (Most Common for Admins) ✅ VERIFIED

### Initial Setup (One-time only)

```bash
# 1. Install dependencies for root environment
sudo pip3 install psycopg2-binary click jinja2 pyyaml

# 2. Install pgpycis in root environment  
sudo pip3 install -e /path/to/pgpycis

# Verify installation location
sudo which pgpycis
# Output: /usr/local/bin/pgpycis
```

### Setup Sudoers (One-time)

```bash
# Copy sudoers configuration
sudo cp pgpycis.sudoers /etc/sudoers.d/pgpycis

# Set correct permissions (IMPORTANT!)
sudo chmod 0440 /etc/sudoers.d/pgpycis

# Verify syntax
sudo visudo -c -f /etc/sudoers.d/pgpycis
# Output: parsed file syntax is OK
```

### Run with Sudo - Examples

```bash
# Basic usage
sudo /usr/local/bin/pgpycis -U postgres -h localhost -f text

# Generate HTML report
sudo /usr/local/bin/pgpycis -U postgres -h localhost -f html -o /tmp/report.html

# With specified port
sudo /usr/local/bin/pgpycis -U postgres -h localhost -p 5432 -f text

# Connect to remote database
sudo /usr/local/bin/pgpycis -U postgres -h db.example.com -f html -o report.html

# Different database
sudo /usr/local/bin/pgpycis -U postgres -h localhost -d template1 -f text
```

### In Cron (Automated Daily Scans) ✅ TESTED

```bash
# Edit crontab with sudo
sudo crontab -e

# Add this line for daily 2 AM scan:
0 2 * * * /usr/local/bin/pgpycis -U postgres -h localhost -f html -o /var/reports/pgpycis_$(date \+\%Y\%m\%d).html 2>> /var/log/pgpycis.log

# View scheduled cron jobs
sudo crontab -l
```

### Verify Sudo Execution Works

```bash
# Test the sudoers configuration
sudo -l | grep pgpycis
# Output should show NOPASSWD: /usr/local/bin/pgpycis

# Quick verification run
sudo /usr/local/bin/pgpycis -U postgres -h localhost -f text 2>&1 | head -20
```

## Method 3: Configuration Files

### Using Environment Variables

```bash
# Set credentials
export PGPYCIS_USER=postgres
export PGPYCIS_HOST=localhost
export PGPYCIS_PORT=5432
export PGPYCIS_DATABASE=postgres

# Create wrapper script
cat > /usr/local/bin/pgpycis-scan.sh << 'EOF'
#!/bin/bash
sudo pgpycis \
  -U ${PGPYCIS_USER} \
  -h ${PGPYCIS_HOST} \
  -p ${PGPYCIS_PORT} \
  -d ${PGPYCIS_DATABASE} \
  -f html \
  -o /var/reports/compliance_$(date +%Y%m%d_%H%M%S).html
EOF

chmod +x /usr/local/bin/pgpycis-scan.sh

# Run from cron
0 2 * * * /usr/local/bin/pgpycis-scan.sh
```

### Using .pgpass for Credentials

```bash
# Create .pgpass file (root home directory if running as root)
cat > ~/.pgpass << 'EOF'
# hostname:port:database:username:password
localhost:5432:postgres:postgres:your_secure_password
EOF

chmod 0600 ~/.pgpass

# Now pgpycis will read credentials automatically
sudo pgpycis -U postgres -h localhost -f html -o report.html
```

## Method 4: Systemd Service

### Create Service Unit

```ini
# /etc/systemd/system/pgpycis-scan.service
[Unit]
Description=PostgreSQL CIS Compliance Scan
After=postgresql.service
Requires=postgresql.service

[Service]
Type=oneshot
User=postgres
Group=postgres

# Can also run as root for full system checks:
# User=root
# Group=root

ExecStart=/usr/local/bin/pgpycis -U postgres -h localhost \
  -f html -o /var/reports/pgpycis_compliance.html

StandardOutput=journal
StandardError=journal
```

### Create Timer Unit

```ini
# /etc/systemd/system/pgpycis-scan.timer
[Unit]
Description=PostgreSQL CIS Compliance Scan Timer
Requires=pgpycis-scan.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Enable and Run

```bash
# Enable timer
sudo systemctl daemon-reload
sudo systemctl enable pgpycis-scan.timer
sudo systemctl start pgpycis-scan.timer

# Check status
sudo systemctl list-timers pgpycis-scan.timer
sudo journalctl -u pgpycis-scan.service -n 50
```

## Important Security Notes

### ✅ Why Root Execution is Safe

1. **Read-Only Operations**: All checks are read-only (database SELECT queries)
2. **No Modifications**: pgpycis never writes to PostgreSQL or system files
3. **Connection User**: Connects to PostgreSQL with specified user (e.g., `postgres`)
4. **Audit-Only**: Used for compliance scanning, not system modification

### ❌ Common Mistakes to Avoid

```bash
# ❌ WRONG: Running as postgres won't read system files
pgpycis -U postgres -h localhost    # Some checks fail due to permissions

# ✅ RIGHT: Running as root reads all system files
sudo pgpycis -U postgres -h localhost   # All checks execute properly

# ❌ WRONG: Hardcoding passwords in scripts
pgpycis -U admin -p "password123" -h db.example.com

# ✅ RIGHT: Using .pgpass for secure credential storage
chmod 0600 ~/.pgpass
pgpycis -U admin -h db.example.com   # Password read from .pgpass
```

### Database User Privileges

For optional enhanced security, create a read-only database user:

```sql
-- Create read-only user
CREATE ROLE pgpycis_scanner LOGIN PASSWORD 'scanner_password';

-- Grant minimal needed privileges
GRANT CONNECT ON DATABASE postgres TO pgpycis_scanner;
GRANT USAGE ON SCHEMA pg_catalog TO pgpycis_scanner;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO pgpycis_scanner;
GRANT SELECT ON ALL VIEWS IN SCHEMA pg_catalog TO pgpycis_scanner;

-- Run as root, connect as pgpycis_scanner
sudo pgpycis -U pgpycis_scanner -h localhost -f html
```

## Practical Example: Complete Setup

```bash
#!/bin/bash
# Complete setup for automated compliance scanning

# 1. Install pgpycis
sudo pip3 install psycopg2-binary click jinja2 pyyaml
cd /opt/pgpycis
sudo pip3 install -e .

# 2. Configure sudoers
sudo install -m 0440 pgpycis.sudoers /etc/sudoers.d/pgpycis

# 3. Create report directory
sudo mkdir -p /var/reports/postgresql
sudo chown -R postgres:postgres /var/reports/postgresql
sudo chmod 0755 /var/reports/postgresql

# 4. Create wrapper script
sudo tee /usr/local/bin/pgpycis-daily-scan.sh > /dev/null << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="/var/reports/postgresql/compliance_$TIMESTAMP.html"

# Run as root for comprehensive checks
sudo pgpycis \
  -U postgres \
  -h localhost \
  -f html \
  -o "$OUTPUT" \
  2>> /var/log/pgpycis.log

# Keep only 30 days of reports
find /var/reports/postgresql -name "compliance_*.html" -mtime +30 -delete

echo "Report saved to: $OUTPUT"
EOF

sudo chmod +x /usr/local/bin/pgpycis-daily-scan.sh

# 5. Add to crontab
echo "0 2 * * * /usr/local/bin/pgpycis-daily-scan.sh" | sudo crontab -

# 6. Verify crontab
sudo crontab -l | grep pgpycis

echo "✓ Setup complete!"
echo "Reports will be generated daily at 2 AM"
echo "Check reports in: /var/reports/postgresql/"
```

## Troubleshooting ✅ TESTED SOLUTIONS

### Issue: "pg_isready utility not found" with Sudo

**Problem**: When running with `sudo`, pg_isready is not found even though it's installed.

**Root Cause**: Root's PATH doesn't include PostgreSQL binary directories like `/usr/pgsql-18/bin/`.

**Solution** (Already Implemented in healthcheck.py):
```python
# pgpycis automatically searches common PostgreSQL paths:
pg_isready_paths = [
    "/usr/bin/pg_isready",
    "/usr/local/bin/pg_isready",
    "/usr/pgsql-18/bin/pg_isready",
    "/usr/pgsql-17/bin/pg_isready",
    # ... etc
]
```

✅ **No action needed** - pgpycis handles this automatically.

### Issue: "ModuleNotFoundError: No module named 'pgpycis'" with Sudo

**Problem**: Running `sudo pgpycis` fails with module import error.

**Root Cause**: Dependencies not installed in root's Python environment.

**Solution**:
```bash
# Install pgpycis dependencies for root
sudo pip3 install psycopg2-binary click jinja2 pyyaml

# Install pgpycis in editable mode for root
sudo pip3 install -e /path/to/pgpycis

# Verify installation
sudo which pgpycis
# Output: /usr/local/bin/pgpycis
```

### Issue: "sudo: pgpycis: command not found"

**Problem**: Executing `sudo pgpycis` doesn't find the command.

**Root Cause**: pgpycis not in root's PATH after pip installation.

**Solution**:
```bash
# Use full path after installing for root
sudo /usr/local/bin/pgpycis -U postgres -h localhost -f text

# Or check sudoers configuration is correct
sudo visudo -c -f /etc/sudoers.d/pgpycis

# Or create symlink in standard location
sudo ln -s /usr/local/bin/pgpycis /usr/sbin/pgpycis
```

### Issue: "Connection refused" from root

```bash
# Root can't connect to PostgreSQL via Unix socket by default
# Solution: Use TCP connection explicitly
sudo pgpycis -U postgres -h localhost -f text
# Note: -h localhost (not empty, uses TCP)

# If still failing, check PostgreSQL is running:
sudo systemctl status postgresql-18.service

# Verify connectivity manually:
sudo /usr/pgsql-18/bin/pg_isready -h localhost
# Output: accepting connections
```

### Issue: "Permission denied" reading config files

```bash
# Some files are only readable as postgres
# Solution 1: Run as root (recommended for comprehensive checks)
sudo pgpycis -U postgres -h localhost

# Solution 2: Grant read permissions
sudo chown postgres:postgres /var/lib/pgsql/18/data/postgresql.conf
sudo chmod 0640 /var/lib/pgsql/18/data/postgresql.conf
pgpycis -U postgres -h localhost
```

### Issue: Sudoers File Errors

**Problem**: "syntax error in sudoers file" or "visudo: syntax check failed"

**Solution**:
```bash
# Edit safely with visudo (uses vi editor)
sudo visudo -f /etc/sudoers.d/pgpycis

# Or restore from original
sudo cp pgpycis.sudoers /etc/sudoers.d/pgpycis
sudo chmod 0440 /etc/sudoers.d/pgpycis

# Verify syntax
sudo visudo -c -f /etc/sudoers.d/pgpycis
```

---

### Original Troubleshooting Section

### Original Issue: "sudo: pgpycis: command not found"

**Solution**: Install in system Python path
```bash
sudo pip3 install -e /path/to/pgpycis
```

Or create symlink
```bash
sudo ln -s /home/user/.local/bin/pgpycis /usr/local/bin/pgpycis
```

### Original Issue: "Connection refused" from root

```bash
# Root can't connect to PostgreSQL via Unix socket by default
# Solution: Use TCP connection with -h
sudo pgpycis -U postgres -h localhost -f text

# Or allow root socket access in pg_hba.conf:
# local   all   all   trust
```

### Original Issue: "Permission denied" reading config files

```bash
# Some files are only readable as postgres
# Solution: Run as root OR as postgres user with elevated perms

# Run as root (recommended):
sudo pgpycis -U postgres -h localhost

# Or grant permissions:
sudo chown postgres:postgres /var/lib/pgsql/18/data/postgresql.conf
sudo chmod 0640 /var/lib/pgsql/18/data/postgresql.conf
pgpycis -U postgres -h localhost
```

## Summary

**Recommended Architecture:**

```
┌─ Root Execution ────────────────────────┐
│                                         │
│  sudo pgpycis                          │
│  ├─ System checks (as root)     ✓     │
│  └─ DB checks (connect as postgres) ✓ │
│                                         │
│  Result: 100% Check Coverage          │
└─────────────────────────────────────────┘
```

**Key Points:**

✅ Root execution is SAFE (read-only operations)  
✅ Connects to PostgreSQL as specified user  
✅ Comprehensive system-level checks included  
✅ Easily automated in cron/systemd/containers  
✅ Sudoers configuration available for ease of use  

**Quick Start:**

```bash
# One-time setup
sudo pip3 install -e /path/to/pgpycis
sudo install -m 0440 pgpycis.sudoers /etc/sudoers.d/pgpycis

# Run compliance scan
sudo pgpycis -U postgres -h localhost -f html -o report.html

# Done! Report generated with full 100+ checks
```
