#!/bin/bash
# Start Flask API and Vite frontend concurrently
python3 api.py > /tmp/api.log 2>&1 &
API_PID=$!

# Wait for API to start
echo "Starting Flask API..."
sleep 5

# Start Vite frontend
echo "Starting Vite frontend..."
npm run dev

# Cleanup on exit
trap "kill $API_PID" EXIT
