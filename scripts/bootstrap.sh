#!/bin/bash
# CircuitGPT Monorepo Bootstrapper

set -e

echo "⚡ Bootstrapping CircuitGPT Workspace..."

# 1. Environment File Check
if [ ! -f .env ]; then
  echo "📝 Creating .env from .env.example..."
  cp .env.example .env
else
  echo "✅ .env file already exists."
fi

# 2. Dependency checks
echo "🔍 Checking system dependencies..."

if command -v docker &> /dev/null; then
  echo "✅ Docker is installed: $(docker --version)"
else
  echo "❌ Docker is not installed. Please install Docker and try again."
fi

if command -v docker-compose &> /dev/null; then
  echo "✅ Docker Compose is installed: $(docker-compose --version)"
elif docker compose version &> /dev/null; then
  echo "✅ Docker Compose V2 is available."
else
  echo "⚠️ Docker Compose was not found. Please ensure it is in your PATH."
fi

if command -v node &> /dev/null; then
  echo "✅ Node.js is installed: $(node -v)"
else
  echo "⚠️ Node.js is not installed. Required if you want to run frontend tasks locally outside Docker."
fi

if command -v python3 &> /dev/null; then
  echo "✅ Python is installed: $(python3 --version)"
elif command -v python &> /dev/null; then
  echo "✅ Python is installed: $(python --version)"
else
  echo "⚠️ Python is not installed. Required if you want to run backend linting/testing locally outside Docker."
fi

# 3. Create persistent directories (gitignored but required by docker volume configurations occasionally or local data)
echo "📁 Preparing local volumes and caching mount dirs..."
mkdir -p .docker_data/postgres .docker_data/redis .docker_data/minio .docker_data/qdrant

echo "🎉 Workspace bootstrapping complete! You can run 'npm run dev' or 'scripts/dev.sh' to start."
