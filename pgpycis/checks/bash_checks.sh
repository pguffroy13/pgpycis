#!/bin/bash
# Manual Security Checks for PostgreSQL CIS Benchmark
# Executes system-level checks that require root/sudo privileges
# Output: JSON format for parsing by Python

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Global arrays to store results
declare -A RESULTS
declare -A DETAILS

# Helper functions
log_check() {
    local check_id=$1
    local status=$2
    local details=$3
    RESULTS[$check_id]=$status
    DETAILS[$check_id]=$details
}

output_json() {
    echo "{"
    local first=true
    for check_id in "${!RESULTS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        # Escape quotes in details for JSON
        local escaped_details=$(echo "${DETAILS[$check_id]}" | sed 's/"/\\"/g' | sed "s/'/\\\\'/g")
        echo -n "  \"$check_id\": {\"status\": \"${RESULTS[$check_id]}\", \"details\": \"$escaped_details\"}"
    done
    echo ""
    echo "}"
}

# ============ SECTION 1: Installation and Patches ============

check_1_1_authorized_repos() {
    # Check if PostgreSQL from PGDG repository
    if command -v rpm &> /dev/null; then
        if rpm -qa | grep -q postgresql; then
            # Check repo signature
            local repo_info=$(rpm -qi postgresql-server 2>/dev/null | grep -E "^Packager" || echo "")
            if echo "$repo_info" | grep -iq "pgdg"; then
                log_check "1.1" "SUCCESS" "PostgreSQL is from authorized PGDG repository"
            else
                log_check "1.1" "WARNING" "PostgreSQL installed but repository not verified: $repo_info"
            fi
        else
            log_check "1.1" "FAILURE" "PostgreSQL server package not installed"
        fi
    else
        log_check "1.1" "MANUAL" "Cannot verify package source - rpm not available"
    fi
}

check_1_2_required_packages() {
    # Check for unnecessary packages
    local unnecessary_pkgs=("postgresql-contrib" "postgresql-devel" "postgresql-server-dev")
    local found_pkgs=""
    
    if command -v rpm &> /dev/null; then
        for pkg in "${unnecessary_pkgs[@]}"; do
            if rpm -q "$pkg" &>/dev/null; then
                found_pkgs="$found_pkgs $pkg"
            fi
        done
        
        if [ -z "$found_pkgs" ]; then
            log_check "1.2" "SUCCESS" "No unnecessary packages found"
        else
            log_check "1.2" "WARNING" "Found packages that may be unnecessary:$found_pkgs"
        fi
    else
        log_check "1.2" "MANUAL" "Cannot verify installed packages - rpm not available"
    fi
}

check_1_8_unused_extensions() {
    # This would require database connection - mark as MANUAL
    log_check "1.8" "MANUAL" "Review and remove unused extensions - requires database examination"
}

# ============ SECTION 2: Directory and File Permissions ============

check_2_1_file_permissions_mask() {
    # Check umask for postgres user - check current process
    local current_umask=$(umask)
    
    # This is informational - actual postgres user umask may differ
    if [ "$current_umask" = "0077" ] || [ "$current_umask" = "0027" ]; then
        log_check "2.1" "SUCCESS" "Secure umask configured: $current_umask"
    else
        log_check "2.1" "INFO" "Current umask: $current_umask (check postgres user umask via postgresql conf)"
    fi
}

check_2_4_passwords_in_service_file() {
    # Check for passwords in .pg_service.conf
    # Try accessible service files first
    local pg_service_files=(~/.pg_service.conf /tmp/.pg_service.conf)
    local found_passwords=false
    
    for service_file in "${pg_service_files[@]}"; do
        if [ -f "$service_file" ] && [ -r "$service_file" ]; then
            # Check for password= in the file
            if grep -q "password=" "$service_file" 2>/dev/null; then
                found_passwords=true
                break
            fi
        fi
    done
    
    if [ "$found_passwords" = true ]; then
        log_check "2.4" "FAILURE" "Passwords found in .pg_service.conf files - SECURITY RISK"
    else
        log_check "2.4" "SUCCESS" "No passwords found in accessible .pg_service.conf files"
    fi
}

check_2_8_pgdata_content() {
    # Check PGDATA for unexpected files/symlinks
    local pgdata=${1:-/var/lib/pgsql/data}
    
    if [ ! -d "$pgdata" ]; then
        log_check "2.8" "WARNING" "PGDATA not accessible: $pgdata"
        return
    fi
    
    # Look for suspicious symlinks
    local symlinks=$(find "$pgdata" -type l -exec readlink -f {} \; 2>/dev/null | grep -v "/var/lib/pgsql" || true)
    
    if [ -z "$symlinks" ]; then
        log_check "2.8" "SUCCESS" "No suspicious symlinks found in PGDATA"
    else
        log_check "2.8" "WARNING" "Symlinks found in PGDATA: $symlinks"
    fi
}

# ============ SECTION 3: Logging and Auditing ============

check_3_1_5_log_filename() {
    # Check postgresql.conf for log_filename pattern
    local postgresql_conf=${1:-/var/lib/pgsql/data/postgresql.conf}
    
    if [ -f "$postgresql_conf" ] && [ -r "$postgresql_conf" ]; then
        local log_filename=$(grep "^log_filename" "$postgresql_conf" 2>/dev/null | cut -d= -f2 | sed "s/['\"]//g" | xargs)
        
        if [ -z "$log_filename" ]; then
            log_check "3.1.5" "INFO" "log_filename not explicitly set (using default)"
        elif echo "$log_filename" | grep -qE "postgresql-%a\.|postgresql-%w\."; then
            log_check "3.1.5" "SUCCESS" "log_filename pattern configured: $log_filename"
        else
            log_check "3.1.5" "WARNING" "log_filename may need adjustment: $log_filename"
        fi
    else
        log_check "3.1.5" "INFO" "postgresql.conf not readable at: $postgresql_conf"
    fi
}

check_3_1_8_rotation_lifetime() {
    # Check log_file_age_days or log_rotation_age setting
    local postgresql_conf=${1:-/var/lib/pgsql/data/postgresql.conf}
    
    if [ -f "$postgresql_conf" ] && [ -r "$postgresql_conf" ]; then
        local rotation_age=$(grep "^log_rotation_age" "$postgresql_conf" 2>/dev/null | cut -d= -f2 | sed "s/['\"]//g" | xargs || echo "")
        
        if [ -z "$rotation_age" ]; then
            log_check "3.1.8" "INFO" "log_rotation_age not explicitly configured (using default)"
        else
            log_check "3.1.8" "SUCCESS" "log_rotation_age configured: $rotation_age"
        fi
    else
        log_check "3.1.8" "INFO" "postgresql.conf not readable"
    fi
}

check_3_1_9_rotation_size() {
    # Check log_rotation_size setting
    local postgresql_conf=${1:-/var/lib/pgsql/data/postgresql.conf}
    
    if [ -f "$postgresql_conf" ] && [ -r "$postgresql_conf" ]; then
        local rotation_size=$(grep "^log_rotation_size" "$postgresql_conf" 2>/dev/null | cut -d= -f2 | sed "s/['\"]//g" | xargs || echo "")
        
        if [ -z "$rotation_size" ]; then
            log_check "3.1.9" "INFO" "log_rotation_size not explicitly configured"
        else
            log_check "3.1.9" "SUCCESS" "log_rotation_size configured: $rotation_size kB"
        fi
    else
        log_check "3.1.9" "INFO" "postgresql.conf not readable"
    fi
}

check_3_1_10_syslog_facility() {
    # Check syslog facility configuration
    local postgresql_conf=${1:-/var/lib/pgsql/data/postgresql.conf}
    
    if [ -f "$postgresql_conf" ] && [ -r "$postgresql_conf" ]; then
        local syslog_facility=$(grep "^syslog_facility" "$postgresql_conf" 2>/dev/null | cut -d= -f2 | sed "s/['\"]//g" | xargs || echo "")
        
        if [ -z "$syslog_facility" ]; then
            log_check "3.1.10" "INFO" "syslog_facility not configured"
        else
            log_check "3.1.10" "SUCCESS" "syslog_facility configured: $syslog_facility"
        fi
    else
        log_check "3.1.10" "INFO" "postgresql.conf not readable"
    fi
}

check_3_1_13_syslog_program_name() {
    # Check syslog_program_name setting
    local postgresql_conf=${1:-/var/lib/pgsql/data/postgresql.conf}
    
    if [ -f "$postgresql_conf" ] && [ -r "$postgresql_conf" ]; then
        local program_name=$(grep "^syslog_program_name" "$postgresql_conf" 2>/dev/null | cut -d= -f2 | sed "s/['\"]//g" | xargs || echo "")
        
        if [ -z "$program_name" ]; then
            log_check "3.1.13" "INFO" "syslog_program_name not explicitly set"
        else
            log_check "3.1.13" "SUCCESS" "syslog_program_name configured: $program_name"
        fi
    else
        log_check "3.1.13" "INFO" "postgresql.conf not readable"
    fi
}

# ============ SECTION 4: User Access and Authorization ============

check_4_4_lock_unused_accounts() {
    # This requires database access - mark as MANUAL
    log_check "4.4" "MANUAL" "Manually verify and lock unused database accounts"
}

check_4_5_security_definer_audit() {
    # This requires database access - mark as MANUAL
    log_check "4.5" "MANUAL" "Audit SECURITY DEFINER functions for privilege escalation risks"
}

check_4_6_dml_privileges() {
    # This requires database access - mark as MANUAL
    log_check "4.6" "MANUAL" "Audit roles/users for excessive DML (INSERT, UPDATE, DELETE) privileges"
}

check_4_7_row_level_security() {
    # This requires database inspection - mark as MANUAL
    log_check "4.7" "MANUAL" "Setup and configure Row Level Security (RLS) policies on sensitive tables"
}

check_4_8_set_user_extension() {
    # Check if set_user extension could be installed
    log_check "4.8" "MANUAL" "Consider installing set_user extension for better privilege separation"
}

check_4_9_predefined_roles() {
    # This requires database access - mark as MANUAL
    log_check "4.9" "MANUAL" "Verify use of PostgreSQL predefined roles instead of custom ones"
}

# ============ SECTION 5: Connection and Login ============

check_5_5_connection_limits() {
    # This requires database role configuration - mark as MANUAL
    log_check "5.5" "MANUAL" "Configure per-account connection limits using ALTER ROLE ... CONNECTION LIMIT"
}

check_5_6_password_complexity() {
    # This requires custom setup - mark as MANUAL
    log_check "5.6" "MANUAL" "Implement password complexity requirements (e.g., via pgcrypto or extension)"
}

check_5_9_ip_ranges() {
    # Check pg_hba.conf for overly broad CIDR ranges
    local pgdata=${1:-/var/lib/pgsql/data}
    local pg_hba="$pgdata/pg_hba.conf"
    
    if [ -f "$pg_hba" ]; then
        # Look for 0.0.0.0/0 or ::/0 in non-local entries
        if grep -v "^#" "$pg_hba" | grep -v "^local" | grep -qE "0\.0\.0\.0\/0|:\/0"; then
            log_check "5.9" "FAILURE" "pg_hba.conf contains overly broad IP ranges (0.0.0.0/0 or ::/0)"
        else
            log_check "5.9" "SUCCESS" "pg_hba.conf IP ranges appear restricted"
        fi
    else
        log_check "5.9" "WARNING" "pg_hba.conf not found"
    fi
}

# ============ SECTION 8: Special Considerations ============

check_8_2_pgbackrest() {
    # Check if pgBackRest is installed
    if command -v pgbackrest &> /dev/null; then
        log_check "8.2" "SUCCESS" "pgBackRest is installed"
    else
        if [ -d /opt/pgbackrest ] || [ -d /usr/local/pgbackrest ]; then
            log_check "8.2" "SUCCESS" "pgBackRest appears to be installed"
        else
            log_check "8.2" "FAILURE" "pgBackRest not installed"
        fi
    fi
}

check_8_1_subdirectories() {
    # Check if WAL, tablespaces, etc. are on separate partitions
    local pgdata=${1:-/var/lib/pgsql/data}
    
    if [ -d "$pgdata" ]; then
        # Get filesystem for PGDATA
        local pgdata_fs=$(df "$pgdata" | awk 'NR==2 {print $1}')
        local wal_dir="$pgdata/pg_wal"
        
        if [ -d "$wal_dir" ]; then
            local wal_fs=$(df "$wal_dir" | awk 'NR==2 {print $1}')
            if [ "$pgdata_fs" = "$wal_fs" ]; then
                log_check "8.1" "WARNING" "WAL directory on same partition as PGDATA"
            else
                log_check "8.1" "SUCCESS" "WAL directory on separate partition"
            fi
        else
            log_check "8.1" "WARNING" "Could not verify WAL directory"
        fi
    else
        log_check "8.1" "WARNING" "PGDATA not found: $pgdata"
    fi
}

# ============ Main execution ============

main() {
    local pgdata="${1:-/var/lib/pgsql/data}"
    local postgresql_conf="$pgdata/postgresql.conf"
    
    # Run all checks
    check_1_1_authorized_repos
    check_1_2_required_packages
    check_1_8_unused_extensions
    
    check_2_1_file_permissions_mask
    check_2_4_passwords_in_service_file
    check_2_8_pgdata_content "$pgdata"
    
    check_3_1_5_log_filename "$postgresql_conf"
    check_3_1_8_rotation_lifetime "$postgresql_conf"
    check_3_1_9_rotation_size "$postgresql_conf"
    check_3_1_10_syslog_facility "$postgresql_conf"
    check_3_1_13_syslog_program_name "$postgresql_conf"
    
    check_4_4_lock_unused_accounts
    check_4_5_security_definer_audit
    check_4_6_dml_privileges
    check_4_7_row_level_security
    check_4_8_set_user_extension
    check_4_9_predefined_roles
    
    check_5_5_connection_limits
    check_5_6_password_complexity
    check_5_9_ip_ranges "$pgdata"
    
    check_8_1_subdirectories "$pgdata"
    check_8_2_pgbackrest
    
    # Output results as JSON
    output_json
}

# Execute main function
main "$@"
