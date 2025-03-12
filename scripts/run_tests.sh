#!/bin/bash

# Function to cleanup
cleanup() {
    echo "Cleaning up test containers..."
    docker-compose -f docker-compose.test.yml down --remove-orphans
    exit
}

# Trap SIGINT and SIGTERM signals and cleanup
trap cleanup SIGINT SIGTERM

echo "=== Running Unit Tests (SQLite) ==="
poetry run pytest tests/ -v -m "not integration"

echo -e "\n=== Preparing for Integration Tests ==="
echo "Starting test PostgreSQL container..."
docker-compose -f docker-compose.test.yml up -d

echo "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until docker-compose -f docker-compose.test.yml exec -T postgres_test pg_isready -U test_user -d test_db || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
    echo "Waiting for PostgreSQL... ($(( RETRY_COUNT + 1 ))/$MAX_RETRIES)"
    RETRY_COUNT=$(( RETRY_COUNT + 1 ))
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Error: PostgreSQL failed to become ready in time"
    cleanup
    exit 1
fi

echo -e "\n=== Running Integration Tests (PostgreSQL) ==="
export USE_POSTGRES_TEST_DB=1
poetry run pytest tests/ -v -m "integration"

# Cleanup
cleanup