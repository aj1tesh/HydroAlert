#!/bin/bash

echo "============================================================"
echo "FLUD Backend Server Startup Script"
echo "============================================================"
echo ""

cd flood_model

echo "Checking Python installation..."
python3 --version || python --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    exit 1
fi

echo ""
echo "Starting backend server..."
echo "Server will be available at http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 api_server.py || python api_server.py

