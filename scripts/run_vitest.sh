#!/bin/sh
# Start backend server in backend container
docker compose -f ./docker-compose-test.yml exec -T --detach backend-test python asgi.py --lifespan INTEGRATION_TEST

# Run tests from frontend container; store the exit code in a variable
docker compose -f ./docker-compose-test.yml exec -T frontend-test npm run test
TEST_EXIT_CODE=$?

# Kill the backend server when we're done testing
docker compose -f ./docker-compose-test.yml exec backend-test sh -c "ps aux | grep 'python asgi.py --lifespan INTEGRATION_TEST' | grep -v grep | awk '{print \$2}' | xargs -r kill"

# Exit with the exit code of the failed test command, if any
if [ $TEST_EXIT_CODE -ne 0 ]; then
  exit $TEST_EXIT_CODE
else
  exit 0  # Or any other default exit code if all commands were successful
fi
