#!/bin/bash
echo "Running Pytest..."
docker compose -f ./docker-compose-test.yml exec -T backend-test pytest --cov=api --cov-report term --cov-fail-under=90 || exit 1
