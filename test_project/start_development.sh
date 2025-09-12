#!/bin/bash

set -e  # Exit immediately if a command fails

echo "🚀 Building and starting containers..."
docker compose up --build -d

echo "⏳ Waiting for database to be ready..."
# Wait until PostgreSQL is accepting connections
until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
  sleep 1
done

echo "✅ Database is ready!"

echo "🔧 Running Django migrations..."
docker compose exec web python manage.py migrate

echo "👤 Creating superuser (press Ctrl+C to skip)..."
docker compose exec web python manage.py createsuperuser || true

echo "🌍 Project is running at: http://localhost:8000"
echo "📦 To view logs: docker compose logs -f"
echo "🛑 To stop containers: docker compose down"

# Attach to container logs (interactive, follows output)
docker compose exec web bash
