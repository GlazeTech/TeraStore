#!/bin/bash
echo "Running Black..."
docker compose -f ./docker-compose-test.yml exec -T backend-test black --check . || exit 1
