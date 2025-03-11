#!/bin/bash

# Check if environment argument is provided
ENV=${1:-dev}
valid_environments=("dev" "stg" "prod")

# Validate environment argument
valid=false
for env in "${valid_environments[@]}"; do
    if [[ "$env" == "$ENV" ]]; then
        valid=true
        break
    fi
done

if [[ -z "$valid" ]]; then
    echo "Error: Invalid environment. Please use one of: ${valid_environments[*]}"
    exit 1
fi

# Check if .env file exists
if [ -f .env ]; then
    echo "Error: .env file already exists"
    exit 1
fi

# Generate random values for credentials
RANDOM_USER="trader_$(openssl rand -hex 4)"
RANDOM_PASSWORD=$(openssl rand -base64 16)
DB_NAME="trading_bot_${ENV}"

# Create .env file
cat > .env << EOF
# Environment
APP_ENVIRONMENT=${ENV}

# Database credentials
POSTGRES_USER=$RANDOM_USER
POSTGRES_PASSWORD=$RANDOM_PASSWORD
POSTGRES_DB=$DB_NAME

# Connection string (used by the application)
DATABASE_URL=postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@postgres:5432/\${POSTGRES_DB}

# Application settings
APP_NAME="Trading Bot Manager"
DEBUG=$([ "$ENV" == "dev" ] && echo "true" || echo "false")

# Environment creation timestamp
ENVIRONMENT_CREATED="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
EOF

# Print the generated credentials (only show during setup)
echo "Environment file created for: $ENV"
echo "Database User: $RANDOM_USER"
echo "Database Name: $DB_NAME"
echo "Database Password: $RANDOM_PASSWORD"
echo ""
echo "These credentials have been saved to .env"

# Set appropriate file permissions
chmod 600 .env

# Create a backup of the credentials
CREDENTIALS_BACKUP="credentials_backup_${ENV}_$(date +%Y%m%d_%H%M%S).txt"
cat > "$CREDENTIALS_BACKUP" << EOF
Trading Bot Manager Credentials (${ENV})
Created on $(date -u +"%Y-%m-%d %H:%M:%S UTC")
===============================
Environment: $ENV
Database User: $RANDOM_USER
Database Name: $DB_NAME
Database Password: $RANDOM_PASSWORD
EOF

chmod 600 "$CREDENTIALS_BACKUP"

echo ""
echo "A backup of your credentials has been saved to $CREDENTIALS_BACKUP"
echo "Please store this file securely and then delete it once you've saved the credentials elsewhere."