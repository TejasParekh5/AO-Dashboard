#!/bin/bash

echo "Starting Cybersecurity KPI Dashboard with Smart Suggestion System..."
echo
echo "This script will start both the suggestion API and the dashboard"
echo

# Check for Python environment
if [ -d ".venv" ]; then
    PYTHON_CMD="./.venv/bin/python"
    echo "Using virtual environment at .venv"
else
    PYTHON_CMD="python"
    echo "Using system Python (virtual environment not found)"
fi

echo "1. Make sure you have installed all required packages:"
echo "   pip install -r requirements_enhanced.txt"
echo

echo "2. Starting the Smart Suggestion API..."
# Start the API in the background
$PYTHON_CMD suggestion_api.py &
API_PID=$!
echo "   API started with PID: $API_PID"
echo

# Wait for API to initialize
echo "   Waiting for API to initialize..."
sleep 5

echo "3. Starting the Enhanced Dashboard..."
echo "   Opening dashboard at http://127.0.0.1:8050/"
echo
# Start the dashboard in the background
$PYTHON_CMD enhanced_dashboard.py &
DASH_PID=$!
echo "   Dashboard started with PID: $DASH_PID"
echo

echo "Both services are running. You can access the dashboard at:"
echo "http://127.0.0.1:8050/"
echo

echo "Press Ctrl+C to shut down both services..."
echo

# Function to clean up when script is terminated
cleanup() {
    echo
    echo "Shutting down services..."
    kill $API_PID
    kill $DASH_PID
    echo "Services stopped."
    exit 0
}

# Register the cleanup function to be called on script termination
trap cleanup INT TERM

# Keep the script running
while true; do
    sleep 1
done
