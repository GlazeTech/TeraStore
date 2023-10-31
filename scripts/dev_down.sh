#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping dev containers...${NC}"

docker compose -f ./docker-compose-dev.yml stop

echo -e "${GREEN}Dev containers stopped.${NC}"