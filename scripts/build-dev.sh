#!/bin/bash
set -e

echo "Starting development environment..."

# Build and start containers
docker compose -f docker-compose.yml up --build -d

# Run database migrations
docker compose -f docker-compose.yml exec backend alembic upgrade head

# Seed database
docker compose -f docker-compose.yml exec backend python scripts/seed_database.py

echo "Services are ready!"
echo "FastAPI Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "PgAdmin: http://localhost:8080"
