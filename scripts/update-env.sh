#!/bin/bash
# scripts/update-env.sh

# Get the project name
PROJECT_NAME=$(basename "$(pwd)")

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Update environment variables in running containers"
    echo
    echo "Options:"
    echo "  -s, --service NAME    Update specific service (backend, frontend, postgres)"
    echo "  -a, --all            Update all services"
    echo "  -v, --validate       Validate environment before updating"
    echo "  -h, --help           Show this help message"
    echo
    echo "Examples:"
    echo "  $0 --all             # Update all services"
    echo "  $0 -s backend        # Update only backend service"
}

# Function to validate environment
validate_env() {
    echo "🔍 Validating environment configuration..."
    if ./scripts/validate-env.sh; then
        echo "✅ Environment validation successful"
        return 0
    else
        echo "❌ Environment validation failed"
        return 1
    fi
}

# Function to safely stop and remove containers
stop_containers() {
    echo "🛑 Stopping and removing containers..."

    docker-compose down --remove-orphans

    local containers
    containers=$(docker ps -a --filter name="trading_bot_dev_" --format "{{.Names}}")
    if [ -n "$containers" ]; then
        echo "⚠️ Forcing removal of lingering containers..."
        echo "$containers" | xargs docker rm -f
    fi

    local networks
    networks=$(docker network ls --filter name="trading_bot_dev_" -q)
    if [ -n "$networks" ]; then
        echo "🧹 Cleaning up project networks..."
        echo "$networks" | xargs docker network rm 2>/dev/null || true
    fi
}

start_containers() {
    echo "🚀 Starting services..."
    docker-compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 5
    local failed_containers
    failed_containers=$(docker-compose ps --services --filter "status=exit")
    if [ -n "$failed_containers" ]; then
        echo "❌ Some services failed to start:"
        echo "$failed_containers"
        echo "📜 Showing logs for failed services:"
        for service in $failed_containers; do
            echo "=== $service logs ==="
            docker-compose logs $service
        done
        return 1
    fi
}

# Function to update specific service
update_service() {
    local service=$1
    echo "🔄 Updating $service service..."

    # Check if service exists
    if ! docker-compose ps "$service" >/dev/null 2>&1; then
        echo "❌ Service $service not found"
        return 1
    fi

    # Store current container ID and status
    local old_container_id
    old_container_id=$(docker-compose ps -q "$service")
    if [ -n "$old_container_id" ]; then
        echo "📊 Current container ID: ${old_container_id:0:12}"
        echo "📊 Current container status: $(docker inspect -f '{{.State.Status}}' "$old_container_id")"
    fi

    # Recreate the service
    docker-compose up -d --force-recreate "$service"

    # Wait for new container to be ready
    echo "⏳ Waiting for $service to be ready..."
    sleep 5

    # Verify service is running
    local new_container_id
    new_container_id=$(docker-compose ps -q "$service")
    if [ -n "$new_container_id" ]; then
        echo "📊 New container ID: ${new_container_id:0:12}"

        # Compare container IDs
        if [ "$old_container_id" = "$new_container_id" ]; then
            echo "⚠️ Warning: Container was not recreated. This might indicate an issue."
        else
            echo "✅ Container was successfully recreated"
        fi

        # Check if container is running
        if [ "$(docker inspect -f '{{.State.Running}}' "$new_container_id")" = "true" ]; then
            echo "✅ $service is running"

            # Show logs of the new container
            echo "📜 Recent logs for $service:"
            docker-compose logs --tail=10 "$service"
        else
            echo "❌ $service is not running"
            echo "📜 Error logs:"
            docker-compose logs --tail=20 "$service"
            return 1
        fi
    else
        echo "❌ Failed to create new container for $service"
        return 1
    fi
}
# Parse command line arguments
VALIDATE=0
ALL_SERVICES=0
SPECIFIC_SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--validate)
            VALIDATE=1
            shift
            ;;
        -a|--all)
            ALL_SERVICES=1
            shift
            ;;
        -s|--service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate environment if requested
if [ $VALIDATE -eq 1 ]; then
    validate_env || exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    exit 1
fi

echo "🔄 Updating environment variables for project: $PROJECT_NAME"

# Update services based on arguments
if [ $ALL_SERVICES -eq 1 ]; then
    echo "📦 Updating all services..."
    # Stop and remove existing containers
    stop_containers
    # Start services
    if start_containers; then
        echo "✅ All services updated successfully"
    else
        echo "❌ Failed to update services"
        exit 1
    fi
elif [ -n "$SPECIFIC_SERVICE" ]; then
    update_service "$SPECIFIC_SERVICE"
else
    echo "❌ Please specify either --all or --service NAME"
    show_help
    exit 1
fi

echo "🔍 Checking service health..."
docker-compose ps

echo "✨ Environment update complete!"