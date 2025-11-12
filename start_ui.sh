#!/bin/bash
# Start Flask API and Vite frontend concurrently

# Ensure Python dependencies are installed
if [ ! -d ".pythonlibs" ]; then
    echo "Setting up Python environment..."
    uv sync
fi

# Activate virtual environment
source .pythonlibs/bin/activate

# Setup cleanup trap before starting services
trap 'echo "Shutting down..."; kill $API_PID 2>/dev/null; exit' EXIT INT TERM

# Start Flask API in background
echo "Starting Flask API on port 3001..."
python3 api.py &
API_PID=$!

# Wait for API to start
sleep 3

# Start Vite frontend (runs in foreground)
echo "Starting Vite frontend on port 5000..."
npm run dev
