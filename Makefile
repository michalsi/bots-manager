# Define color codes
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

# Define emojis
CHECK_MARK=\xE2\x9C\x85
CROSS_MARK=\xE2\x9D\x8C
WARNING=\xE2\x9A\xA0

.PHONY: setup validate init-db clean

# Default environment
ENV ?= dev

setup:
	@echo -e "${BLUE}Setting up the $(ENV) environment...${NC}"
	./scripts/setup-env.sh $(ENV)
	@echo -e "${GREEN}Setup complete! ${CHECK_MARK}${NC}"


validate:
	@echo -e "${BLUE}Validating the environment...${NC}"
	./scripts/validate-env.sh
	@echo -e "${GREEN}Validation successful! ${CHECK_MARK}${NC}"


init-db:
	@echo -e "${BLUE}Initializing the database for $(ENV)...${NC}"
	./scripts/init-db.sh $(ENV)
	@echo -e "${GREEN}Database initialized! ${CHECK_MARK}${NC}"


clean:
	@echo -e "${YELLOW}Cleaning up sensitive files...${NC}"
	rm -f .env credentials_backup_*.txt init-db.sql
	@echo -e "${GREEN}Cleanup complete! ${CHECK_MARK}${NC}"

error:
	@echo -e "${RED}An error occurred! ${CROSS_MARK}${NC}"

# Full setup
all: clean setup validate init-db
	@echo "Setup complete for $(ENV) environment"