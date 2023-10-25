#!/bin/bash
echo "Running Mypy..."
docker-compose -f ./docker-compose-test.yml exec -T backend-test mypy . || exit 1
