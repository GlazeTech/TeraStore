#!/bin/bash

# Initialize an empty string to store names of failed tests
failed_tests=""

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Determine which OS you're on
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  HASH_CMD="sha256sum"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  HASH_CMD="shasum -a 256"
else
  echo "Unsupported OS."
  exit 1
fi

# File to store the last hash
last_hash_file="./last_pyproject.toml_hash.txt"

# Hash the pyproject.toml file
current_hash=$($HASH_CMD ./backend/pyproject.toml | awk '{print $1}')

# Read the last hash if the file exists
if [ -f "$last_hash_file" ]; then
  last_hash=$(cat $last_hash_file)
else
  last_hash=""
fi

run_test() {
  if $1; then
    echo -e "${GREEN}$1 passed${NC}"
  else
    echo -e "${RED}$1 failed${NC}"
    failed_tests+="$1 "
  fi
}

# Start services
echo -e "${YELLOW}Starting services...${NC}"

# Build if the hashes don't match or if it's the first time
if [ "$current_hash" != "$last_hash" ]; then
  echo -e "${YELLOW}Detected changes in pyproject.toml, rebuilding...${NC}"
  docker compose -f ./docker-compose-test.yml -f ./docker-compose-test-local.yml build
  echo $current_hash > $last_hash_file
else
  echo -e "${YELLOW}No changes detected in pyproject.toml, using cached image if available...${NC}"
fi

docker compose -f ./docker-compose-test.yml -f ./docker-compose-test-local.yml up --detach

run_test ./scripts/run_black.sh
run_test ./scripts/run_ruff.sh
run_test ./scripts/run_mypy.sh
run_test ./scripts/run_pytest.sh

# Stop services
echo "Stopping services..."
docker compose -f ./docker-compose-test.yml -f ./docker-compose-test-local.yml down

# Check for failed tests
if [ -z "$failed_tests" ]; then
  echo -e "${GREEN}All checks passed locally!${NC}"
else
  echo -e "${RED}The following checks failed: $failed_tests${NC}"
  exit 1
fi
