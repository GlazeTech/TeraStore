#!/bin/bash
echo "Running Ruff check..."
docker compose -f ./docker-compose-test.yml exec -T backend-test ruff format api --check || exit 1
