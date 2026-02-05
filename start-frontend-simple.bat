@echo off
echo.
echo ========================================
echo Clinical Protocol AI - Frontend Server
echo ========================================
echo.
cd /d "%~dp0frontend"

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if npm packages are installed
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
)

echo.
echo Starting frontend server on http://localhost:3000
echo Backend should be running on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.

REM Start frontend
set BROWSER=none
set GENERATE_SOURCEMAP=false
call npm start