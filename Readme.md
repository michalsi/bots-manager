install dependencies with:
```bash
poetry install --with backend  # Installs backend dependencies
poetry install --with frontend # Installs frontend dependencies
```
And run your application parts with:
```bash
poetry run start-backend
poetry run start-frontend
```

## Environment Setup
1. Set up the environment:
   ```bash
   # For development (default)
   make all
   # For production
   make all ENV=prod

2. Validate the environment:
   ```bash
   make validate
   ```

3. Initialize the database:
   ```bash
   make init-db
   ```

4. Clean up sensitive files:
   ```bash
   make clean
   ```

## Environment Files

- `.env` - Contains environment-specific configuration
- `.env.example` - Template for environment configuration (safe to commit)
- `credentials_backup_*.txt` - Backup of generated credentials (delete after securing credentials)

## Directory Structure
```
trading-bot-manager/
├── docker-compose.yml
├── docker-compose.override.yml  # Development overrides
├── docker-compose.prod.yml      # Production settings
├── Makefile
├── scripts/
│   ├── setup-env.sh
│   ├── validate-env.sh
│   └── init-db.sh
├── src/
│   ├── backend/
│   └── frontend/
└── .gitignore
```

## Environment Types

- `dev` - Local development environment
- `stg` - Testing environment (optional)
- `prod` - Production environment

## Security Notes

1. Never commit `.env` or credential backup files to the repository
2. Delete credential backups after securing the information
3. Use different credentials for each environment
4. Production environments should have additional security measures

Usage workflow:

1. Initial setup:
```bash
# Clone repository
git clone <repository-url>
cd trading-bot-manager

# Install dependencies
poetry install

# Setup development environment
make all

# Start services
docker-compose up -d
```

2. Daily development:
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

3. Working with different environments:
```bash
# Setup production environment
make all ENV=production

# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

4. Database operations:
```bash
# Reinitialize database
make init-db

# Connect to database
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
```