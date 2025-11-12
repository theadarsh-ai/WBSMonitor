#!/bin/bash

echo "Starting Autonomous Project Monitoring System..."

python main.py &
BACKEND_PID=$!

sleep 3

npm run dev

kill $BACKEND_PID 2>/dev/null
