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

# File to store the last hashes
last_hash_file_frontend="./.last_package.json_hash.txt"
last_hash_file_backend="./.last_pyproject.toml_hash.txt"

# Hash the pyproject.toml file
current_hash_frontend=$($HASH_CMD ./frontend/package.json | awk '{print $1}')
current_hash_backend=$($HASH_CMD ./backend/pyproject.toml | awk '{print $1}')

# Read the last hash if the file exists
if [ -f "$last_hash_file_frontend" ]; then
  last_hash_frontend=$(cat $last_hash_file_frontend)
else
  last_hash_backend=""
fi

if [ -f "$last_hash_file_backend" ]; then
  last_hash_backend=$(cat $last_hash_file_backend)
else
  last_hash_backend=""
fi

# Start services
echo "Starting services..."

# Build if the hashes don't match or if it's the first time
if [ "$current_hash_backend" != "$last_hash_backend" ] || [ "$current_hash_frontend" != "$last_hash_frontend" ]; then
  echo -e "${YELLOW}Detected changes in pyproject.toml and/or package.json, rebuilding...${NC}"
  docker compose -f ./docker-compose-dev.yml down -v
  docker compose -f ./docker-compose-dev.yml build
  echo $current_hash_frontend > $last_hash_file_frontend
  echo $current_hash_backend > $last_hash_file_backend
else
  echo -e "${YELLOW}No changes detected in pyproject.toml or package.json. Using cached images if available...${NC}"
fi

if ! docker compose -f ./docker-compose-dev.yml start; then
  echo -e "${YELLOW}Docker start failed. Probably cached images do not exist. Building...${NC}"
  docker compose -f ./docker-compose-dev.yml up --detach
fi

echo -e "${GREEN}Dev services started.${NC}"