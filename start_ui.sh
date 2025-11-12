#!/bin/bash
# Start Flask API and Vite frontend concurrently

# Activate virtual environment and start Flask API
source .pythonlibs/bin/activate
python3 api.py &
API_PID=$!

# Wait for API to start
echo "Starting Flask API on port 3001..."
sleep 3

# Start Vite frontend
echo "Starting Vite frontend on port 5000..."
npm run dev

# Cleanup on exit
trap "kill $API_PID" EXIT
