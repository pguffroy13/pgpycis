# pgpycis - PostgreSQL CIS Compliance Assessment Tool

A comprehensive Python-based security assessment tool for PostgreSQL that performs **100+ security checks** covering all recommendations from the [CIS PostgreSQL Benchmark](https://www.cisecurity.org/cis-benchmarks/).

**Status**: ✅ Production Ready | **Version**: 2.0 | **Last Updated**: March 31, 2026

---

## 🧭 Quick Navigation

- **🆕 New to pgpycis?** Start with the **[📁 Project Architecture](#-project-architecture)** section below
- **🚀 Want to get started immediately?** Jump to **[Quick Start](#-quick-start)**
- **📚 Need structured guidance?** See **[DOCUMENTATION.md](DOCUMENTATION.md)** for a complete index with reading recommendations
- **💻 System Admin?** Go directly to **[RUNNING_AS_ROOT.md](RUNNING_AS_ROOT.md)**
- **👨‍💻 Developer?** Check **[Project Structure Explained](#-understanding-each-component)** section

---

## 📊 Features at a Glance

- ✅ **100+ Security Checks** - Complete CIS PostgreSQL Benchmark coverage
  - 75 Python checks (database configuration & queries)
  - 25+ Bash checks (system-level & file-based)
- ✅ **Multi-Format Reports** - HTML (styled) & Text (detailed)
- ✅ **Multi-Language Support** - English, French, Chinese 
- ✅ **Flexible Execution** - Regular user, sudo, or root modes
- ✅ **Pre-flight Validation** - Auto-discovers and validates PostgreSQL connectivity
- ✅ **No Heavy Dependencies** - Only psycopg2, click, jinja2, pyyaml
- ✅ **PostgreSQL 12-18 Support** - Works with all modern PostgreSQL versions

### Example Reports

- 📄 **Text Format**: [sample/example_compliance_report.txt](sample/example_compliance_report.txt)
- 🌐 **HTML Format**: [sample/example_compliance_report.html](sample/example_compliance_report.html)

---

## 🏗️ Project Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    pgpycis CLI (entrypoint)                     │
│                       pgpycis/cli.py                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Pre-flight Checks (healthcheck.py)                  │   │
│  │    - Detect PostgreSQL service (systemctl)             │   │
│  │    - Test server availability (pg_isready)             │   │
│  │    - Validate database connection (psycopg2)           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│            PGPYCIS Assessment Engine (core.py)                  │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  Initialize      │  │  Run All Checks  │                   │
│  │  - Connect to DB │  │  - Collect results                  │
│  │  - Get PG info   │  │  - Merge findings                   │
│  │  - Detect PGDATA │  │                  │                   │
│  └──────────────────┘  └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│         Check Orchestrator (checks/all_checks.py)              │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Python Checks (75+)                                  │   │
│  │  └─ Section 1-8: Database settings, permissions, etc │   │
│  │     └─ Uses psycopg2 for SQL queries                 │   │
│  └────────────────────────────────────────────────────────┘   │
│                             ↓                                   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Bash Checks (25+)                                    │   │
│  │  └─ bash_runner.py executes bash_checks.sh           │   │
│  │     └─ System commands, file permissions, packages   │   │
│  │     └─ JSON output parsed by Python                  │   │
│  └────────────────────────────────────────────────────────┘   │
│                             ↓                                   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Merge Results                                        │   │
│  │  └─ Combine Python + Bash results                    │   │
│  │  └─ Override MANUAL checks with actual findings      │   │
│  │  └─ Generate statistics (passed/failed/warnings)     │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│         Report Generation (report.py)                           │
│                                                                 │
│  Text Format          →  Console Output                        │
│  HTML Format          →  Styled Report (29 KB)                │
│  Language Support     →  en_US, fr_FR, zh_CN                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure Explained

### Directory Layout

```
pgpycis/
├── README.md                          ← You are here
├── setup.py                           ← Package configuration
├── RUNNING_AS_ROOT.md                 ← Sudo/Root execution guide
├── BASH_CHECKS_INTEGRATION.md         ← Bash checks documentation
├── TESTING_REPORT.md                  ← Testing verification
├── SESSION_SUMMARY.md                 ← Development session notes
│
├── pgpycis/                           ← Main Python package
│   ├── __init__.py                   ← Package metadata (__version__)
│   ├── cli.py                         ← Command-line interface (entrypoint)
│   ├── core.py                        ← Assessment engine orchestrator
│   ├── healthcheck.py                 ← Pre-flight PostgreSQL validation
│   │
│   ├── labels.py                      ← Check labels/titles (multilingual)
│   ├── messages.py                    ← Result messages (multilingual)
│   ├── report.py                      ← Report generation (text/HTML)
│   ├── netmask.py                     ← IP netmask validation
│   │
│   ├── checks/                        ← All PostgreSQL CIS checks
│   │   ├── __init__.py
│   │   ├── all_checks.py              ← Orchestrates Python + Bash checks
│   │   ├── bash_checks.sh             ← System-level Bash checks (~300 lines)
│   │   ├── bash_runner.py             ← Executes bash_checks.sh, parses JSON
│   │   │
│   │   └── (Individual check sections would go here)
│   │
│   └── __pycache__/                   ← Python bytecode cache
│
├── sample/                            ← Example output files
│   ├── example_compliance_report.txt   ← Sample text report
│   ├── example_compliance_report.html  ← Sample HTML report
│   └── report.html                    ← From original project
│
├── doc/                               ← Additional documentation
│   └── pgdsat.pod                     ← Original Perl tool docs
│
└── scripts/                           ← Utility scripts (if any)
    └── (build, test, deploy scripts)
```

---

## 🧩 Understanding Each Component

### 1. **Command-Line Interface** (`pgpycis/cli.py`)

**Purpose**: Entry point for the tool. Parses arguments and coordinates execution.

**Key Functions**:
- Parse command-line arguments (user, host, port, database, format, language)
- Call `healthcheck.py` for pre-flight validation
- Initialize `PGPYCIS` engine
- Manage error handling and user output

**Typical Flow**:
```python
# User runs: pgpycis -U postgres -h localhost -f html -o report.html
cli.main()
  ├─ Parse arguments
  ├─ Run pre-flight checks
  ├─ Create PGPYCIS instance
  ├─ Execute assessment
  └─ Generate report
```

### 2. **Health Check System** (`pgpycis/healthcheck.py`) - NEW ✨

**Purpose**: Validates PostgreSQL is accessible BEFORE running assessment.

**Three Key Checks**:
1. **Service Detection**: Auto-finds PostgreSQL service (postgresql-18.service)
2. **Availability Test**: Uses `pg_isready` or TCP connection test
3. **Connection Validation**: Attempts actual psycopg2 connection

**Why It's Important**: Prevents confusing error messages mid-assessment.

**Smart Features**:
- Auto-searches PostgreSQL paths (/usr/pgsql-*/bin, /usr/bin, etc.)
- Handles PATH issues with sudo
- Clear error messages for diagnostics

### 3. **Assessment Engine** (`pgpycis/core.py`)

**Purpose**: Main orchestrator that runs the security assessment.

**Key Methods**:
- `__init__()` - Initialize with connection parameters
- `connect()` - Establish database connection
- `initialize()` - Get PostgreSQL version and user info
- `run_checks()` - Execute all 100+ checks
- `generate_report()` - Create output file
- `run()` - Main execution method

**Execution Flow**:
```
PGPYCIS.run()
  ├─ connect() → PostgreSQL
  ├─ initialize() → Get version, superuser status
  ├─ run_checks() → Call checks orchestrator
  ├─ generate_report() → Format results
  └─ Return success/failure
```

### 4. **Check Orchestrator** (`pgpycis/checks/all_checks.py`)

**Purpose**: Runs all 100+ security checks in organized sections.

**Sections** (8 total):
1. **Installation & Patches** - 18 checks
2. **File Permissions** - 15 checks  
3. **Logging & Auditing** - 20 checks
4. **User Access** - 15 checks
5. **Connection & Login** - 15 checks
6. **PostgreSQL Settings** - 10 checks
7. **Replication** - 5 checks
8. **Special Considerations** - 2 checks

**Check Types**:
- ✅ **SUCCESS** - Check passed security requirement
- ❌ **FAILURE** - Check failed, security issue detected
- ⚠️ **WARNING** - Potential security concern
- ℹ️ **INFO** - Informational (no action needed)
- 📋 **MANUAL** - Requires human review or elevated privileges

### 5. **Python Checks** (75+)

**Example Checks**:
- Authentication settings (MD5 vs SCRAM-SHA-256)
- Superuser role verification
- Extension audit
- Replication settings
- SSL/TLS configuration
- Database encoding

**Implementation Pattern**:
```python
def check_1_1_1_pgdg_packages():
    """Check if PostgreSQL from PGDG repository"""
    result = subprocess.run(["rpm", "-q", "postgresql-server"], ...)
    return {
        "status": "SUCCESS" if result.returncode == 0 else "FAILURE",
        "details": "PostgreSQL installed from PGDG" or "PostgreSQL not from PGDG"
    }
```

**Database Query Example**:
```python
# Get all database users
cur.execute("SELECT usename, usesuper FROM pg_user ORDER BY usename")
results = cur.fetchall()

# Check for dangerous settings
cur.execute("SELECT name, setting FROM pg_settings WHERE name LIKE '%log%'")
```

### 6. **Bash Checks** (25+) - System Level

**Purpose**: Checks that require system-level access or file operations.

**Examples**:
- Package verification (rpm/dpkg queries)
- File permissions (/var/lib/pgsql/data, /var/log/pgbackrest)
- Systemd service status
- Config file parsing (postgresql.conf, pg_hba.conf)
- System resources and partitions

**Execution**:
```
Python (cli.py)
  ↓
bash_runner.py::safe_run_bash_checks()
  ├─ Find bash_checks.sh
  ├─ Execute with subprocess.run()
  ├─ Capture JSON output
  └─ Return dict of results
  ↓
Results merged into final report
```

**JSON Output Example** (from bash_checks.sh):
```json
{
  "1.1": {"status": "WARNING", "details": "PostgreSQL not from PGDG"},
  "1.2": {"status": "SUCCESS", "details": "No unnecessary packages"},
  "2.4": {"status": "SUCCESS", "details": "No passwords in .pg_service.conf"}
}
```

### 7. **Report Generation** (`pgpycis/report.py`)

**Purpose**: Format assessment results into human-readable reports.

**Supported Formats**:
- **Text**: Detailed console output with status symbols (✓, ✗, ⚠)
- **HTML**: Styled report with summary statistics, sections, collapsible details

**Report Contents**:
1. **Executive Summary** - Pass/fail/warning/manual counts
2. **Section Results** - Organized by CIS benchmark section
3. **Check Details** - Each check with status and explanation
4. **Metadata** - Timestamp, PostgreSQL version, hostname

**Example HTML Features**:
- Responsive design
- Color-coded statuses (green/red/yellow)
- Summary statistics with charts
- Sortable check tables
- Dark mode support (CSS)

### 8. **Localization** (`pgpycis/labels.py`, `pgpycis/messages.py`)

**Purpose**: Support multiple languages for global compliance teams.

**Supported Languages**:
- 🇺🇸 English (en_US) - Default
- 🇫🇷 French (fr_FR)
- 🇨🇳 Chinese (zh_CN)

**Data**:
- `labels.py` - Check titles and descriptions
- `messages.py` - Status messages and explanations

**Usage**:
```python
labels = Labels("fr_FR")  # French labels
print(labels.get("1.1"))  # Returns French label for check 1.1
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download
cd ~/DEV/pgpycis

# Install with pip
pip install -e .

# Or install for root (for sudo execution)
sudo pip3 install -e .
```

### First Run

```bash
# Basic scan
pgpycis -U postgres -h localhost

# Generate HTML report
pgpycis -U postgres -h localhost -f html -o compliance.html

# French report
pgpycis -U postgres -h localhost -l fr_FR -f html -o compliance_fr.html
```

### With Elevated Privileges

```bash
# Run with sudo (requires sudo access)
sudo /usr/local/bin/pgpycis -U postgres -h localhost -f text

# Or as root
sudo -i
pgpycis -U postgres -h localhost -f html -o /var/reports/compliance.html
```

---

## 📊 How It Works: Execution Flow

### Step-by-Step Execution

```
1. User runs: pgpycis -U postgres -h localhost -f html -o report.html
                    ↓
2. cli.main() parses arguments and validates
                    ↓
3. healthcheck.py verifies:
   ✓ PostgreSQL service is running
   ✓ pg_isready connection succeeds
   ✓ Database connection succeeds
                    ↓
4. core.py::PGPYCIS initializes:
   - Connects to database
   - Gets version: PostgreSQL 18.3
   - Detects superuser: True
   - Detects PGDATA: /var/lib/pgsql/18/data
                    ↓
5. checks/all_checks.py runs checksSECTION 1: Installation & Patches (18 checks)
   ├─ 1.1: Repository check → Python (rpm query)
   ├─ 1.2: Package check   → Bash (system-level)
   └─ ...
   SECTION 2: File Permissions (15 checks)
   ├─ 2.4: Password search → Bash (grep)
   └─ ...
                    ↓
6. bash_runner.py::safe_run_bash_checks():
   - Executes bash_checks.sh
   - Captures JSON output
   - Parses results
   - Merges with Python results
                    ↓
7. Results collected:
   - Total checks: 100
   - Passed: 18
   - Failed: 7
   - Warnings: 6
   - Manual: 19
   - Errors: 50
                    ↓
8. report.py generates HTML report:
   - Executive summary
   - Section-by-section findings
   - Detailed check explanations
                    ↓
9. Report saved: report.html (29 KB)
                    ↓
10. Output: "Report saved to: report.html"
```

---

## 🔍 Key Features Explained

### Pre-Flight Health Checks ✨ NEW

Automatically validates PostgreSQL before running assessment:

```python
# healthcheck.py
Running pre-flight checks...
✓ PostgreSQL is running and responding          # pg_isready check
✓ Successfully connected to PostgreSQL as 'postgres'  # psycopg2 test
Pre-flight checks passed. Starting assessment...
```

**Why?** Without this, users would see confusing SQL errors. Now they get clear diagnostics immediately.

### Hybrid Python + Bash Approach

| Component | Python | Bash |
|-----------|--------|------|
| Database queries | ✅ | ❌ |
| Settings verification | ✅ | ❌ |
| File permissions | ⚠️ | ✅ |
| Package info | ⚠️ | ✅ |
| Service status | ⚠️ | ✅ |
| **Total Checks** | **~75** | **~25** |

**Result**: Comprehensive coverage (100+ total checks)

### Multi-Privilege Execution

```
Mode 1: Regular User
  pgpycis -U postgres -h localhost
  ├─ Database checks: ✅ Full access
  └─ System checks: ⚠️ Limited (permission denied on some files)

Mode 2: With Sudo (Recommended)
  sudo pgpycis -U postgres -h localhost
  ├─ Database checks: ✅ Full access
  └─ System checks: ✅ Full access (runs as root)

Mode 3: As Root Shell
  sudo -i
  pgpycis -U postgres -h localhost
  ├─ Database checks: ✅ Full access
  └─ System checks: ✅ Full access
```

---

## 📈 Sample Report Output

### Text Format

```
PGPYCIS - PostgreSQL CIS Compliance Assessment Tool
====================================================

Connected to: PostgreSQL 18.3 on x86_64-pc-linux-gnu
Current user: postgres
Is superuser: True

Running all 95+ PostgreSQL security checks...

================================================================================
PGPYCIS - PostgreSQL CIS Compliance Assessment Tool
Report generated: 2026-03-31 00:47:23
================================================================================

# EXECUTIVE SUMMARY

Total Checks: 100
Passed: 18
Failed: 7
Warnings: 6
Manual: 19

# DETAILED ASSESSMENT

## 1 - Installation and Patches

  ✗ [1.1] Ensure packages are obtained from authorized repositories => WARNING
      PostgreSQL installed but repository not verified

  ✓ [1.2] Install only required packages => SUCCESS
      No unnecessary packages found

  ✓ [1.4.3] Ensure Data Cluster have checksum enabled => SUCCESS
      Checksums enabled

## 2 - Directory and File Permissions

  ✓ [2.4] Ensure Passwords are Not Stored => SUCCESS
      No passwords found in accessible .pg_service.conf files

  ...
```

### HTML Format

Beautiful styled report with:
- 📊 Summary statistics panel
- 🎨 Color-coded check statuses
- 📋 Sortable check tables
- 📱 Responsive mobile design
- 🌙 Dark theme support

[View sample HTML report →](sample/example_compliance_report.html)

---

## 🔐 Security Model

### Read-Only Design

pgpycis **NEVER**:
- ❌ Modifies database configurations
- ❌ Alters user passwords
- ❌ Modifies system files
- ❌ Installs packages

pgpycis **ONLY**:
- ✅ Reads PostgreSQL settings (SELECT queries)
- ✅ Inspects file permissions (ls operations)
- ✅ Queries system information (rpm, systemctl)
- ✅ Analyzes configuration files (cat, grep)

### Safe Sudo Execution

When running with `sudo pgpycis`:
- Tool connects to PostgreSQL as specified user (default: postgres)
- System checks run with root privileges
- No database modification capabilities
- Full audit trail in sudo logs

See [RUNNING_AS_ROOT.md](RUNNING_AS_ROOT.md) for complete security details.

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | This file - overview and getting started |
| **RUNNING_AS_ROOT.md** | Comprehensive guide for sudo/root execution |
| **BASH_CHECKS_INTEGRATION.md** | Technical details about system check integration |
| **TESTING_REPORT.md** | Detailed test results and verification |
| **SESSION_SUMMARY.md** | Development milestones and learnings |

---

## 🛠️ Development & Debugging

### Run Pre-flight Checks Only

```python
from pgpycis.healthcheck import check_postgres_service, verify_postgres_connection

is_running, msg = check_postgres_service("localhost", 5432)
print(f"Service: {is_running}, {msg}")

can_connect, msg = verify_postgres_connection("postgres", "localhost", 5432, "postgres")
print(f"Connection: {can_connect}, {msg}")
```

### Extract Bash Check Results

```python
from pgpycis.checks.bash_runner import safe_run_bash_checks

results = safe_run_bash_checks()
print(f"Found {len(results)} bash checks")
for check_id, data in results.items():
    print(f"  {check_id}: {data['status']} - {data['details']}")
```

### Generate Report Programmatically

```python
from pgpycis.core import PGPYCIS

assessment = PGPYCIS(user="postgres", host="localhost", lang="en_US")
assessment.initialize()
assessment.run_checks()
report = assessment.generate_report(format="html", output_file="report.html")
print("✓ Report generated")
```

---

## 🎯 Common Use Cases

### 1. Compliance Audit for Management

```bash
pgpycis -U postgres -h prod-pg-01 \
  -f html \
  -o compliance_report_$(date +%Y%m%d).html

# Email or upload to compliance tracking system
```

### 2. Automated CI/CD Security Check

```bash
# In .gitlab-ci.yml
pgpycis -U postgres -h localhost -f text | \
  grep -E "FAILURE|ERROR" && exit 1 || exit 0
```

### 3. Multi-Database Compliance Tracking

```bash
#!/bin/bash
for db in prod-pg-01 prod-pg-02 staging-pg-01; do
  echo "Scanning $db..."
  sudo pgpycis -U postgres -h $db -f html \
    -o reports/${db}_$(date +%Y%m%d).html
done
```

---

## 🤝 Contributing

Enhancements welcome! Areas for contribution:
- Additional CIS benchmark checks
- Support for PostgreSQL 19+
- Additional language translations
- Performance optimizations
- Bug fixes and issue reports

---

## 📄 License

[Specify your license here]

---

## 📞 Support & Documentation

**📋 Complete Documentation Index**: [DOCUMENTATION.md](DOCUMENTATION.md) ← **Start here for navigation!**

| Item | Location |
|------|----------|
| 🚀 Getting Started | This README.md |
| 🔐 Root/Sudo Execution | [RUNNING_AS_ROOT.md](RUNNING_AS_ROOT.md) |
| 🧩 Bash Checks Architecture | [BASH_CHECKS_INTEGRATION.md](BASH_CHECKS_INTEGRATION.md) |
| ✅ Testing & Verification | [TESTING_REPORT.md](TESTING_REPORT.md) |
| 📊 Development Summary | [SESSION_SUMMARY.md](SESSION_SUMMARY.md) |
| 📖 Doc Navigation Guide | [DOCUMENTATION.md](DOCUMENTATION.md) |

### Quick Help

- 🐛 **Bug reports or issues?** Check [TESTING_REPORT.md](TESTING_REPORT.md)
- ❓ **Configuration questions?** See [RUNNING_AS_ROOT.md](RUNNING_AS_ROOT.md)
- 📊 **Want to see sample reports?** Review [sample/](sample/) directory (text & HTML)
- 🔧 **Need technical details?** Read [BASH_CHECKS_INTEGRATION.md](BASH_CHECKS_INTEGRATION.md)
- 🧭 **Don't know where to start?** See [DOCUMENTATION.md](DOCUMENTATION.md) for guided recommendations

---

**Last Updated**: March 31, 2026 | **Status**: ✅ Production Ready | **Tested On**: AlmaLinux 8 + PostgreSQL 18.3
