#!/bin/bash
echo "Running Pytest..."
docker-compose -f ./docker-compose-test.yml exec -T backend-test pytest || exit 1
