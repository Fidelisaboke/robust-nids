#!/bin/bash

# PostgreSQL Database Setup Script
# This script automates the database setup process with proper error handling and logging

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

# Load environment variables
load_env() {
    log_info "Loading environment configuration"

    # Path to .env file (currently backend/.env)
    ENV_FILE=$(dirname "$0")/../.env

    if [ -f "$ENV_FILE" ]; then
        # Safe way to load .env file - automatically exports all variables
        set -a  # Automatically export all variables
        . "$ENV_FILE"   # Source the .env file
        set +a  # Turn off auto-export
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
    DB_ADMIN_PASSWORD=${DB_ADMIN_PASSWORD:-""}

    log_info "Configuration:"
    log_info "  Host: $DB_HOST"
    log_info "  Port: $DB_PORT"
    log_info "  Database: $DB_NAME"
    log_info "  User: $DB_USER"
    log_info "  Admin: $DB_ADMIN_USER"
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python and required packages are available
check_python_dependencies() {
    log_info "Checking Python dependencies"

    if ! command -v python2 &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python is not installed"
        exit 1
    fi

    # Check if SQLAlchemy is installed
    if ! python3 -c "import sqlalchemy" 2>/dev/null; then
        log_error "SQLAlchemy is not installed. Run: pip install sqlalchemy"
        exit 1
    fi

    log_success "Python dependencies are available"
}

# Check if PostgreSQL client tools are available
check_dependencies() {
    log_info "Checking dependencies"

    if ! command -v psql &> /dev/null; then
        log_error "PostgreSQL client (psql) is not installed"
        exit 1
    fi

    check_python_dependencies
    log_success "All dependencies are available"
}

# Test PostgreSQL server connection
test_postgres_connection() {
    log_info "Testing PostgreSQL server connection"

    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "SELECT 1" postgres &> /dev/null; then
        log_success "Connected to PostgreSQL server"
        return 0
    else
        log_error "Failed to connect to PostgreSQL server"
        log_info "Please ensure:"
        log_info "1. PostgreSQL is running on $DB_HOST:$DB_PORT"
        log_info "2. User '$DB_ADMIN_USER' has access with the provided password"
        log_info "3. Your pg_hba.conf allows password authentication"
        return 1
    fi
}

# Drop database if it exists
drop_database() {
    log_info "Checking if database '$DB_NAME' exists"

    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warning "Database '$DB_NAME' exists, dropping it"
        if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "DROP DATABASE $DB_NAME" postgres; then
            log_success "Database dropped successfully"
        else
            log_error "Failed to drop database"
            exit 1
        fi
    else
        log_info "Database doesn't exist, no need to drop"
    fi
}

# Create database user
create_user() {
    log_info "Checking if user '$DB_USER' exists"

    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" postgres | grep -q 1; then
        log_info "User '$DB_USER' exists, updating password"
        if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD'" postgres; then
            log_success "User password updated"
        else
            log_error "Failed to update user password"
            exit 1
        fi
    else
        log_info "Creating user '$DB_USER'"
        if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'" postgres; then
            log_success "User created successfully"
        else
            log_error "Failed to create user"
            exit 1
        fi
    fi
}

# Create database
create_database() {
    log_info "Creating database '$DB_NAME'"

    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER" postgres; then
        log_success "Database created successfully"
    else
        log_error "Failed to create database"
        exit 1
    fi
}

# Set up schema and permissions
setup_schema() {
    log_info "Setting up database schema and permissions"

    # Connect to the new database and set up schema
    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -d "$DB_NAME" << EOF
        -- Revoke default public privileges
        REVOKE ALL ON SCHEMA public FROM PUBLIC;

        -- Grant necessary privileges to the application user
        GRANT CONNECT ON DATABASE $DB_NAME TO $DB_USER;
        GRANT USAGE ON SCHEMA public TO $DB_USER;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $DB_USER;
        GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

        -- Set default privileges for future objects
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $DB_USER;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO $DB_USER;
EOF
    then
        log_success "Schema setup completed successfully"
    else
        log_error "Failed to set up schema"
        exit 1
    fi
}

# Test database connection as application user
test_db_connection() {
    log_info "Testing database connection as application user '$DB_USER'"

    if PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null; then
        log_success "Application user can connect to the database successfully"
    else
        log_error "Application user cannot connect to the database"
        exit 1
    fi
}

# Run database seeding
run_seeding() {
    log_info "Starting database seeding process"

    # Check if seeding script exists
    if [ ! -f "scripts/seed_database.py" ]; then
        log_warning "Seeding script not found at scripts/seed_database.py"
        log_info "Skipping database seeding"
        return 0
    fi

    # Export database connection string for the seeding script
    export DB_CONNECTION_STRING="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    export ADMIN_DB_CONNECTION_STRING="postgresql://$DB_ADMIN_USER:$DB_ADMIN_PASSWORD@$DB_HOST:$DB_PORT/postgres"

    # Run the seeding script
    if python3 database/seed.py; then
        log_success "Database seeding completed successfully"
        return 0
    else
        log_error "Database seeding failed"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       PostgreSQL Setup for NIDS        ${NC}"
    echo -e "${BLUE}========================================${NC}"

    # Load environment configuration
    load_env

    # Check dependencies
    check_dependencies

    # Test PostgreSQL connection
    if ! test_postgres_connection; then
        exit 1
    fi

    # Execute setup steps
    drop_database
    create_user
    create_database
    setup_schema
    test_db_connection

    # Run database seeding
    if run_seeding; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  Database setup completed successfully!  ${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}  Database setup completed with warnings  ${NC}"
        echo -e "${YELLOW}========================================${NC}"
    fi

    # Print next steps
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Update your .env file with these database credentials:"
    echo "   DB_HOST=$DB_HOST"
    echo "   DB_PORT=$DB_PORT"
    echo "   DB_NAME=$DB_NAME"
    echo "   DB_USER=$DB_USER"
    echo "   DB_PASSWORD=$DB_PASSWORD"
    echo ""
    echo "2. Run your Streamlit application:"
    echo "   streamlit run app.py"
    echo ""
    echo "3. Consider changing the default passwords in production"
}

# Run main function
main "$@"
