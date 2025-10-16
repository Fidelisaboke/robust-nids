#!/bin/bash
set -e

# Set uv to use the virtual environment in appuser's home directory
export UV_PROJECT_ENVIRONMENT=/home/appuser/.venv
export VENV_PATH=/home/appuser/.venv
export PATH="$VENV_PATH/bin:$PATH"
echo "[DEBUG] Virtual environment path set to $VENV_PATH"
echo "[DEBUG] Python path: $(which python)"
echo "[DEBUG] Alembic path: $(which alembic)"

# Run database migrations
echo "[INFO] Running database migrations..."
alembic upgrade head
echo "[INFO] Database migrations completed!"

# Seed the database with initial data
echo "[INFO] Seeding database..."
python -m database.seed

# Start the FastAPI server
echo "[INFO] Starting application..."
echo "----------------------------------------"
echo "Once the application is running, you can access the following links:"
echo "FastAPI: http://localhost:8000"
echo "Swagger UI: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo "pgAdmin: http://localhost:5050"
exec "$@"
