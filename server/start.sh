#!/bin/bash
set -e

echo "Starting PostgreSQL container..."
docker compose up -d

echo "Waiting for PostgreSQL to be ready..."
until docker compose exec -T db pg_isready -U postgres -d passmypass > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  # Enable CORS for development
  sed -i '' 's/# CORS_ORIGINS/CORS_ORIGINS/' .env 2>/dev/null || sed -i 's/# CORS_ORIGINS/CORS_ORIGINS/' .env
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt --quiet

echo ""
echo "Starting FastAPI server..."
echo "API will be available at http://localhost:8000"
echo ""
uvicorn app.main:app --reload --port 8000
