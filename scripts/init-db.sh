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

if [[ "$valid" == false ]]; then
    echo "Error: Invalid environment. Please use one of: ${valid_environments[*]}"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Create SQL initialization script
cat > init-db.sql << EOF
-- Create application roles
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;

-- Grant basic connect permissions
GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;

-- Grant read permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

-- Grant write permissions
GRANT app_readonly TO app_readwrite;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

-- Create application user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
        CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
    END IF;
END
\$\$;

-- Grant appropriate role to application user
GRANT app_readwrite TO ${POSTGRES_USER};

-- Set search path
ALTER ROLE ${POSTGRES_USER} SET search_path TO public;

-- Additional production settings
$([ "$ENV" = "prod" ] && echo "
ALTER SYSTEM SET max_connections = '100';
ALTER SYSTEM SET ssl = 'on';
")
EOF

echo "Database initialization script created"