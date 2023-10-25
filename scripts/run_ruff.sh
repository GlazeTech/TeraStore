#!/bin/bash
echo "Running Ruff..."
docker-compose -f ./docker-compose-test.yml exec -T backend-test ruff check . || exit 1
