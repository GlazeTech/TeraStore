#!/bin/bash

# Function to handle termination signals
_term() {
  echo "Caught signal, exiting..."
  exit 0
}

# Trap termination signals
trap _term SIGTERM SIGINT

# Keep alive (replace this with whatever you need to keep the container alive)
tail -f /dev/null & wait $!