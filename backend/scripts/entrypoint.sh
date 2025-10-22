#!/bin/bash
set -e

# Logging helper
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ENTRYPOINT] $1"
}

# Set uv to use the virtual environment in appuser's home directory
export UV_PROJECT_ENVIRONMENT=/home/appuser/.venv
export VENV_PATH=/home/appuser/.venv
export PATH="$VENV_PATH/bin:$PATH"

log "Virtual environment path set to $VENV_PATH"
log "Python path: $(which python)"
log "Alembic path: $(which alembic)"

# Check for alembic
if ! command -v alembic &> /dev/null; then
  log "ERROR: Alembic not found in PATH. Exiting..."
  exit 1
fi

# Run database migrations
if [ "$RUN_MIGRATIONS" != "false" ]; then
  log "Running database migrations..."
  alembic upgrade head
  log "Database migrations completed!"
else
  log "Skipping migrations (RUN_MIGRATIONS=false)"
fi

# Seed the database
if [ "$RUN_SEED" != "false" ]; then
  log "Seeding database..."
  python -m database.seed
else
  log "Skipping database seeding (RUN_SEED=false)"
fi

# Start the FastAPI server
log "Starting application..."
echo "----------------------------------------"
echo "Once the application is running, access:"
echo "FastAPI: http://localhost:8000"
echo "Swagger UI: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo "pgAdmin: http://localhost:5050"

exec "$@"
