#!/bin/bash

#PROJECT_NAME=${1:-$(basename "$(pwd)")}
PROJECT_NAME=trading_bot_dev
echo "Cleaning up Docker resources for project: $PROJECT_NAME"

echo "Stopping and removing containers for project: $PROJECT_NAME"
docker-compose -p "$PROJECT_NAME" down --volumes --rmi all

echo "Removing project volumes..."
docker volume ls -q | grep "^${PROJECT_NAME}" | while read -r volume; do
    docker volume rm "$volume"
done

echo "Removing project networks..."
docker network ls -q | grep "^${PROJECT_NAME}" | while read -r network; do
    docker network rm "$network"
done

echo "Removing project images..."
docker images --format "{{.Repository}} {{.ID}}" | grep "^${PROJECT_NAME}" | while read -r image_name image_id; do
    docker rmi "$image_id"
done

echo "Project-specific cleanup complete for: $PROJECT_NAME"