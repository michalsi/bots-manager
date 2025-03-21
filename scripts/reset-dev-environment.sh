#!/bin/bash

PROJECT_NAME=$(basename "$(pwd)")
echo "🔍 Operating on project: $PROJECT_NAME"

echo "🧹 Cleaning up development environment..."

echo "📥 Stopping project containers and removing volumes..."
docker-compose -p "$PROJECT_NAME" down -v

# Additional cleanup for potentially lingering containers
echo "🧹 Removing any lingering containers..."
docker rm -f \
    trading_bot_dev_postgres \
    trading_bot_dev_backend \
    trading_bot_dev_frontend \
    2>/dev/null || true


echo "🗑️ Removing existing .env file..."
rm -f .env

echo "🧹 Running Docker cleanup for project-specific resources..."
./scripts/cleanup-docker.sh "$PROJECT_NAME"

echo "🔧 Generating new development environment..."
./scripts/setup-env.sh dev

echo "📚 Initializing database..."
./scripts/init-db.sh dev

echo "🚀 Building and starting services..."
docker-compose -p "$PROJECT_NAME" up -d --build

echo "✨ Development environment has been reset and initialized!"
echo "🔍 Checking services health..."
sleep 5

if docker-compose -p "$PROJECT_NAME" ps | grep -q "Up"; then
    echo "✅ Services are running!"
else
    echo "❌ Some services failed to start. Please check docker-compose logs"
fi