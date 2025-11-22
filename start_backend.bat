@echo off
echo ============================================================
echo FLUD Backend Server Startup Script
echo ============================================================
echo.

cd flood_model

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting backend server...
echo Server will be available at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py

pause

