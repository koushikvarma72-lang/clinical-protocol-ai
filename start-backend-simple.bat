REM Invoke-WebRequest -Uri "http://localhost:8001/clear-database" -Method Post -UseBasicParsing | Select-Object -ExpandProperty Content
@echo off
echo.
echo ========================================
echo Clinical Protocol AI - Backend Server
echo ========================================
echo.
cd /d "%~dp0backend"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

echo.
echo Starting backend server on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.

REM Start backend on port 8001 (matching frontend config)
python main.py