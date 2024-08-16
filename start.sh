#!/bin/bash

# Run the first Node.js script in the background
node index.js &

# Run the second Node.js script
node radar/index.js &

# Wait for all background jobs to finish
wait

# Keep the container running
exec "$@"