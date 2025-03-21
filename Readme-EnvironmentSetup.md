# Environment Setup Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Environment Types](#environment-types)
- [Local Development Setup](#local-development-setup)
- [Updating Environment Variables](#Updating-environment-variables)
- [Higher Environment Setup](#higher-environment-setup)
- [Docker Architecture](#docker-architecture)
- [Database Management](#database-management)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

This project uses Docker and Docker Compose for containerization, ensuring consistent environments across development,
staging, and production. The environment setup is managed through a series of shell scripts that handle configuration,
initialization, and maintenance tasks.

## Prerequisites

Required software:

- Docker (20.10.x or higher)
- Docker Compose (2.x or higher)
- Python 3.8+
- Poetry (Python dependency management)
- Bash shell (for running scripts)

To verify your installations:

```bash
docker --version
docker-compose --version
python --version
poetry --version
```

## Project Structure

```
├── docker-compose.yml          # Base Docker configuration
├── docker-compose.override.yml # Development-specific overrides
├── docker-compose.test.yml     # Testing configuration
├── scripts/
│   ├── setup-env.sh           # Environment configuration
│   ├── init-db.sh            # Database initialization
│   ├── cleanup-docker.sh     # Docker cleanup utility
│   ├── reset-dev-environment.sh # Dev environment reset
│   ├── run_tests.sh         # Test runner
│   └── validate-env.sh      # Environment validator
├── src/                     # Application source code
└── tests/                  # Test files
```

## Environment Types

The project supports three environment types:

- `dev`: Local development environment
- `stg`: Staging environment
- `prod`: Production environment

Each environment type has specific configurations and security measures:

| Feature              | Dev | Staging | Production |
|----------------------|-----|---------|------------|
| Debug Mode           | ✅   | ❌       | ❌          |
| Volume Mounts        | ✅   | ❌       | ❌          |
| Port Exposure        | ✅   | Limited | Limited    |
| SSL Enforcement      | ❌   | ✅       | ✅          |
| Database Persistence | ✅   | ✅       | ✅          |

## Local Development Setup

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Create and set up development environment
./scripts/reset-dev-environment.sh
```

This script will:

- Clean up any existing Docker resources
- Generate new secure credentials
- Create necessary environment files
- Initialize the database
- Start all required services

### 2. Verify Setup

Check if all services are running:

```bash
docker-compose ps
```

Expected output:

```
NAME                    STATUS              PORTS
trading_bot_postgres    Up                  0.0.0.0:5432->5432/tcp
trading_bot_backend     Up                  0.0.0.0:8000->8000/tcp
trading_bot_frontend    Up                  0.0.0.0:8501->8501/tcp
```

## Updating Environment Variables

When you modify the `.env` file, you need to update the running containers to reflect these changes. Use the
`update-env.sh` script to manage this process:

### Usage Examples

1. **Update all services:**

```bash
./scripts/update-env.sh --all
```

2. **Update specific service:**

```bash
./scripts/update-env.sh --service backend
```

3. **Update with validation:**

```bash
./scripts/update-env.sh --all --validate
```

### Common Scenarios

1. **Database credential changes:**

```bash
# Update postgres service first, then dependent services
./scripts/update-env.sh -s postgres
./scripts/update-env.sh -s backend
```

2. **API configuration changes:**

```bash
# Update only backend service
./scripts/update-env.sh -s backend
```

3. **Debug mode changes:**

```bash
# Update all services to reflect debug mode changes
./scripts/update-env.sh --all
```

### Important Notes

- Some environment changes might require a full service restart
- Database credential changes might require additional configuration steps
- Always validate critical environment changes before applying them
- Consider the impact on running applications when updating variables
- Some changes might require database migrations or additional setup

### Troubleshooting

If services fail to start after environment updates:

1. Check the logs:

```bash
docker-compose logs [service_name]
```

2. Validate environment configuration:

```bash
./scripts/validate-env.sh
```

3. Try a complete reset if needed:

```bash
./scripts/reset-dev-environment.sh
```

### 3. Common Development Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Rebuild services
docker-compose up -d --build

# Reset environment completely
./scripts/reset-dev-environment.sh
```

## Higher Environment Setup

### Staging Environment

```bash
# Generate staging environment configuration
./scripts/setup-env.sh stg

# Initialize database with staging settings
./scripts/init-db.sh stg

# Validate environment
./scripts/validate-env.sh
```

### Production Environment

```bash
# Generate production environment configuration
./scripts/setup-env.sh prod

# Initialize database with production settings
./scripts/init-db.sh prod

# Validate environment
./scripts/validate-env.sh
```

## Docker Architecture

### Container Organization

- **postgres**: PostgreSQL database server
    - Port: 5432
    - Volume: Persistent data storage
    - Environment: Configured via .env file

- **backend**: Application backend service
    - Port: 8000
    - Dependencies: postgres
    - Environment: Configured via .env file

- **frontend**: Application frontend service
    - Port: 8501
    - Dependencies: backend
    - Environment: Configured via .env file

### Volume Management

The project uses named volumes for data persistence:

```yaml
volumes:
  postgres_data:    # Database files
```

In development, volumes are mounted for live code updates:

```yaml
volumes:
  - ./src:/app/src  # Code mounting
```

## Database Management

### Connection Details

- Development database is accessible at: `postgresql://localhost:5432`
- Credentials are stored in `.env` file
- Connection string format: `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}`

### Database Initialization

The `init-db.sh` script handles:

- Role creation
- Permission setup
- Default schema creation
- Environment-specific configurations

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Reset environment
   ./scripts/reset-dev-environment.sh
   
   # Check database logs
   docker-compose logs postgres
   ```

2. **Services Won't Start**
   ```bash
   # Check service status
   docker-compose ps
   
   # View detailed logs
   docker-compose logs -f
   
   # Rebuild services
   docker-compose up -d --build
   ```

3. **Volume Persistence Issues**
   ```bash
   # Remove volumes and recreate
   docker-compose down -v
   ./scripts/reset-dev-environment.sh
   ```

### Validation

Use the validation script to check environment configuration:

```bash
./scripts/validate-env.sh
```

## Best Practices

1. **Environment Management**
    - Never commit `.env` files to version control
    - Use `setup-env.sh` for generating environment configurations
    - Keep backup of credentials in secure location

2. **Development Workflow**
    - Use `docker-compose.override.yml` for local customizations
    - Run tests before committing changes
    - Regular cleanup of unused Docker resources

3. **Security**
    - Regularly rotate database credentials
    - Use different credentials for each environment
    - Limit port exposure in production

4. **Monitoring**
    - Regularly check container logs
    - Monitor database performance
    - Keep track of disk usage for volumes