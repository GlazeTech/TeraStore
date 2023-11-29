#!/bin/sh
# Start backend server in backend container
docker compose -f ./docker-compose-test.yml exec -T --detach backend-test python asgi.py --lifespan INTEGRATION_TEST

# Run tests from frontend container
docker compose -f ./docker-compose-test.yml exec -T frontend-test npm run test

# Kill the backend server when we're done testing
docker compose -f ./docker-compose-test.yml exec backend-test sh -c "ps aux | grep 'python asgi.py --lifespan INTEGRATION_TEST' | grep -v grep | awk '{print \$2}' | xargs -r kill"