#!/bin/bash

# PostgreSQL Database Local Setup Script
set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_HOST="localhost"
DEFAULT_PORT="5432"
DEFAULT_DATABASE="nids_db"
DEFAULT_USER="nids_user"
DEFAULT_PASSWORD="change_this_in_production"

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Load environment variables
load_env() {
    log_info "Loading environment configuration"

    # Determine script directory and load .env file
    SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
    ENV_FILE="$SCRIPT_DIR/../.env"

    if [ -f "$ENV_FILE" ]; then
        set -a
        . "$ENV_FILE"
        set +a
        log_success "Environment file loaded from $ENV_FILE"
    else
        log_warning ".env file not found, using default values"
    fi

    # Set variables with fallbacks
    DB_HOST=${DB_HOST:-$DEFAULT_HOST}
    DB_PORT=${DB_PORT:-$DEFAULT_PORT}
    DB_NAME=${DB_NAME:-$DEFAULT_DATABASE}
    DB_USER=${DB_USER:-$DEFAULT_USER}
    DB_PASSWORD=${DB_PASSWORD:-$DEFAULT_PASSWORD}
    DB_ADMIN_USER=${DB_ADMIN_USER:-"postgres"}

    # Prompt for admin password if not set.
    if [[ -z "${DB_ADMIN_PASSWORD-}" ]]; then
        read -rsp "Enter password for PostgreSQL admin user '$DB_ADMIN_USER': " DB_ADMIN_PASSWORD
        echo
    fi

    log_info "Configuration loaded for database '$DB_NAME' on '$DB_HOST'"
}

# Check if PostgreSQL client tools are available
check_dependencies() {
    log_info "Checking dependencies"

    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL client (psql) is not installed"
        exit 1
    fi

    log_success "All dependencies are available"
}

# Test PostgreSQL server connection
test_postgres_connection() {
    log_info "Testing PostgreSQL server connection"

    export PGPASSWORD="$DB_ADMIN_PASSWORD"

    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "postgres" -c "SELECT 1" &> /dev/null; then
        log_success "Connected to PostgreSQL server"
    else
        log_error "Failed to connect to PostgreSQL server"
        log_info "Please ensure:"
        log_info "1. PostgreSQL is running on $DB_HOST:$DB_PORT"
        log_info "2. User '$DB_ADMIN_USER' has access with the provided password"
        log_info "3. Your pg_hba.conf allows password authentication"
        exit 1
    fi

    unset PGPASSWORD
}

# Drop database if it exists
drop_database() {
    log_info "Checking if database '$DB_NAME' exists"
    export PGPASSWORD="$DB_ADMIN_PASSWORD"

    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "postgres" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
        log_warning "Database '$DB_NAME' exists, dropping it"
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "postgres" -c "DROP DATABASE $(echo "$DB_NAME" | sed 's/"/""/g;s/^/"/;s/$/"/')"
        log_success "Database dropped successfully"
    else
        log_info "Database '$DB_NAME' does not exist, skipping drop"
    fi
    unset PGPASSWORD
}

# Create or update the database user
create_user() {
    log_info "Creating or updating user '$DB_USER'"
    export PGPASSWORD="$DB_ADMIN_PASSWORD"

    psql -v ON_ERROR_STOP=1 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "postgres" <<-EOF
        DO \$\$
        BEGIN
           IF EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
              RAISE NOTICE 'Role "$DB_USER" already exists. Updating password.';
              ALTER ROLE "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
           ELSE
              RAISE NOTICE 'Role "$DB_USER" does not exist. Creating it.';
              CREATE ROLE "$DB_USER" WITH LOGIN PASSWORD '$DB_PASSWORD';
           END IF;
        END
        \$\$;
EOF
    unset PGPASSWORD
    log_success "User '$DB_USER' is configured"
}

# Create the database
create_database() {
    log_info "Creating database '$DB_NAME' with owner '$DB_USER'"
    export PGPASSWORD="$DB_ADMIN_PASSWORD"

    psql -v ON_ERROR_STOP=1 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "postgres" \
        -c "CREATE DATABASE \"$DB_NAME\" WITH OWNER = \"$DB_USER\""

    unset PGPASSWORD
    log_success "Database created successfully"
}

# Test database connection as application user
test_db_connection() {
    log_info "Testing database connection as application user '$DB_USER'"
    export PGPASSWORD="$DB_PASSWORD"
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null
    log_success "Application user can connect to the database successfully"
    unset PGPASSWORD
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       PostgreSQL Setup for NIDS        ${NC}"
    echo -e "${BLUE}========================================${NC}"

    # Setup steps
    load_env
    check_dependencies
    test_postgres_connection

    # Database setup
    drop_database
    create_user
    create_database
    test_db_connection

    # Print next steps
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Run Alembic migrations to set up the schema:"
    echo "   alembic upgrade head"
    echo ""
    echo "2. Seed the database:"
    echo "   python database/seed.py"
    echo ""
    echo "3. Consider changing the default passwords in production"
}

main "$@"
