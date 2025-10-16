#!/bin/bash
set -e

echo "🚀 Starting development environment..."

# Build and start containers
docker compose -f docker-compose.yml up --build
