# 🔐 For System Administrators Running as Root

## Quick Answer

**YES, pgpycis can run as root!** ✅

```bash
# Simple - just run as root
sudo -i
pgpycis -U postgres -h localhost -f html -o compliance.html

# Or with sudo directly (if sudoers configured)
sudo pgpycis -U postgres -h localhost -f html -o compliance.html

# Or in automated jobs
0 2 * * * sudo pgpycis -U postgres -h localhost -f html -o /var/reports/daily.html
```

**Key Point**: Root runs the security checks, but connects to PostgreSQL as the `postgres` user you specify. ✓

## What This Achieves

```
Your environment          pgpycis (root)              PostgreSQL
┌──────────────────┐      ┌─────────────────┐          ┌──────────┐
│  Root shell      │      │ Root execution  │          │ postgres │
│  (systemctl,     │ ──→  │ (read system    │ ──────→  │  user    │
│   config files,  │      │  files, run     │          │(read DB  │
│   etc)           │      │  bash checks)   │          │configs)  │
└──────────────────┘      └─────────────────┘          └──────────┘
```

## Full Documentation

### 📖 Main Guides
1. **[README.md](README.md)** - Start here (installation, usage)
2. **[RUNNING_AS_ROOT.md](RUNNING_AS_ROOT.md)** ⭐ **YOU ARE HERE** - Root execution details
3. **[BASH_CHECKS_INTEGRATION.md](BASH_CHECKS_INTEGRATION.md)** - How system checks work
4. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Architecture and design

### 🔧 Configuration Files
- **[pgpycis.sudoers](pgpycis.sudoers)** - Copy to `/etc/sudoers.d/pgpycis`
- **[deploy.sh](deploy.sh)** - Interactive setup helper

### 📍 Navigation
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Full documentation map

## Three Ways to Run

### 1️⃣ Direct Root Execution (Simplest)
```bash
sudo -i                              # Switch to root shell
pgpycis -U postgres -h localhost    # Run pgpycis as root
```

### 2️⃣ Sudo Execution (Recommended)
```bash
sudo pgpycis -U postgres -h localhost -f html -o report.html
```

### 3️⃣ Automated Scheduling
```bash
# Cron job
0 2 * * * sudo pgpycis -U postgres -h localhost -f html -o /var/reports/daily.html

# Systemd timer
# See RUNNING_AS_ROOT.md for example
```

## In 2 Minutes

```bash
# Step 1: Install (one time)
pip3 install psycopg2-binary click jinja2 pyyaml
cd /path/to/pgpycis
pip3 install -e .

# Step 2: Run compliance scan
sudo pgpycis -U postgres -h localhost -f html -o report.html

# Step 3: View report
open report.html  # or: cat report.html
```

**That's it!** Your system now has a comprehensive PostgreSQL CIS compliance report. ✓

## For Automated Daily Scans

```bash
# Create script
sudo tee /usr/local/bin/pgpycis-scan.sh > /dev/null << 'EOF'
#!/bin/bash
sudo pgpycis -U postgres -h localhost \
  -f html -o /var/reports/compliance_$(date +%Y%m%d).html
EOF

# Make executable
sudo chmod +x /usr/local/bin/pgpycis-scan.sh

# Schedule in cron
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/pgpycis-scan.sh
```

## Why This Works (It's Safe!)

✅ **Read-Only**: pgpycis never WRITES to PostgreSQL or system files  
✅ **Connection User**: Specified via `-U postgres` parameter  
✅ **Principle of Least Privilege**: Uses minimal required permissions  
✅ **Audit-Only**: Used for compliance checking, not system modification  

## Questions?

| Question | Answer |
|----------|--------|
| **How does root access help?** | Reads system files, checks packages, verifies permissions - not available to regular users |
| **Is it safe?** | YES - all operations are read-only. No writes to system. |
| **Can I run as postgres instead?** | Yes, but some checks will fail due to permissions. See [README.md](README.md) |
| **What if I forget the password?** | Configure sudoers: `sudo install -m 0440 pgpycis.sudoers /etc/sudoers.d/pgpycis` |
| **How often should I scan?** | Daily recommended. Schedule with cron or systemd (see below) |
| **What's the output?** | HTML report (pretty) or text report (raw). See [README.md](README.md) examples |
| **Can I integrate with monitoring?** | Yes! Parse JSON or HTML, feed to ELK/Prometheus/etc. (see examples in RUNNING_AS_ROOT.md) |

## Common Commands

```bash
# Generate HTML report
sudo pgpycis -U postgres -h localhost -f html -o compliance.html

# Generate text report (stdout)
sudo pgpycis -U postgres -h localhost -f text

# Connect to remote server
sudo pgpycis -U admin -h db.example.com -p 5433 -f html

# Specify alternative PGDATA
sudo pgpycis -U postgres -h localhost -D /opt/pg18/data -f html

# Write to file
sudo pgpycis -U postgres -h localhost -o /tmp/report.html

# French output
sudo pgpycis -U postgres -h localhost -l fr_FR -f text
```

## Troubleshooting

**Q**: "sudo: pgpycis: command not found"  
**A**: Install in system path: `sudo pip3 install -e /path/to/pgpycis`

**Q**: Database connection error  
**A**: Use `-h localhost` instead of socket connection when running as root

**Q**: Config file permission issues  
**A**: Root can read any file - if issue persists, check PostgreSQL startup user permissions

**Q**: Want to skip password prompts?  
**A**: Configure sudoers: See [pgpycis.sudoers](pgpycis.sudoers)

## More Details

👉 For complete documentation: **[RUNNING_AS_ROOT.md](RUNNING_AS_ROOT.md)**

## Summary

| Aspect | Details |
|--------|---------|
| **Execution** | `sudo pgpycis -U postgres -h localhost` |
| **Privilege** | Root execution for system checks |
| **Database** | Connects as specified user (e.g., postgres) |
| **Safety** | Read-only operations only |
| **Automation** | Easily scheduled with cron/systemd |
| **Reports** | HTML or text format |
| **Coverage** | 100+ comprehensive checks |

---

✅ **Ready to scan!** Start with: `sudo pgpycis --help`
