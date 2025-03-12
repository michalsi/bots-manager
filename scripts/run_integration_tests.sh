#!/bin/bash
docker-compose -f docker-compose.test.yml up -d
sleep 5
USE_POSTGRES_TEST_DB=1 pytest tests/ -v
docker-compose -f docker-compose.test.yml down