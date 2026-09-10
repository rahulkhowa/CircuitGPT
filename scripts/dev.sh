#!/bin/bash
# Start local development environment using Docker Compose

# Navigate to the root directory if we are run from scripts/
cd "$(dirname "$0")/.."

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
  echo "⚠️ .env file not found. Copying from .env.example..."
  cp .env.example .env
fi

# Run docker compose up with build
docker compose -f docker-compose.dev.yml up --build "$@"
