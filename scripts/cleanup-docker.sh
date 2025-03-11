#!/bin/bash

# Define project name (usually the directory name of your docker-compose.yml)
PROJECT_NAME=$(basename "$(pwd)")

echo "Stopping and removing all containers for project: $PROJECT_NAME"
docker-compose down --volumes --rmi all

echo "Removing unused Docker volumes"
docker volume prune -f

echo "Removing unused Docker networks"
docker network prune -f

echo "Removing dangling Docker images"
docker image prune -f

echo "Removing all Docker containers"
docker container prune -f

echo "Removing all Docker images"
docker image prune -a -f

echo "Cleanup complete. All Docker data related to the project has been wiped."