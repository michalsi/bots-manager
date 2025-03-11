#!/bin/bash

# Required environment variables
REQUIRED_VARS=(
    "APP_ENVIRONMENT"
    "POSTGRES_USER"
    "POSTGRES_PASSWORD"
    "POSTGRES_DB"
    "DATABASE_URL"
    "APP_NAME"
    "DEBUG"
)

# Valid environments
valid_environments=("dev" "stg" "prod")

# Load .env file if it exists
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Check each required variable
MISSING_VARS=0
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "Error: $VAR is not set"
        MISSING_VARS=$((MISSING_VARS+1))
    fi
done

# Validate environment
valid=false
for env in "${valid_environments[@]}"; do
    if [[ "$env" == "$APP_ENVIRONMENT" ]]; then
        valid=true
        break
    fi
done

if [[ "$valid" == false ]]; then
    echo "Error: APP_ENVIRONMENT must be one of: ${valid_environments[*]}"
    MISSING_VARS=$((MISSING_VARS+1))
fi

# Validate database URL format
if [[ ! "$DATABASE_URL" =~ ^postgresql://.*:.*@.*:[0-9]+/.*$ ]]; then
    echo "Error: DATABASE_URL format is invalid"
    MISSING_VARS=$((MISSING_VARS+1))
fi

# Validate database name format
if [[ ! "$POSTGRES_DB" =~ ^trading_bot_(dev|stg|prod)$ ]]; then
    echo "Error: POSTGRES_DB format is invalid. Expected: trading_bot_<environment>"
    MISSING_VARS=$((MISSING_VARS+1))
fi

# Environment-specific validations
if [ "$APP_ENVIRONMENT" = "prod" ]; then
    if [ "$DEBUG" = "true" ]; then
        echo "Warning: DEBUG is set to true in production environment"
    fi
fi

# Check if any variables are missing or invalid
if [ $MISSING_VARS -gt 0 ]; then
    echo "Found $MISSING_VARS missing or invalid configuration items"
    exit 1
else
    echo "Environment validation successful"
    exit 0
fi