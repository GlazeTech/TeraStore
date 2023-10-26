#!/bin/bash

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

# Start services
echo "Starting services..."

# Build if the hashes don't match or if it's the first time
if [ "$current_hash" != "$last_hash" ]; then
  echo -e "${YELLOW}Detected changes in pyproject.toml, rebuilding...${NC}"
  docker compose -f ./docker-compose-dev.yml build
  echo $current_hash > $last_hash_file
else
  echo -e "${YELLOW}No changes detected in pyproject.toml, using cached image...${NC}"
fi

docker compose -f ./docker-compose-dev.yml up --detach
