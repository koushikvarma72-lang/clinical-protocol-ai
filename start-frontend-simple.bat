@echo off
echo Starting React frontend...
cd /d "%~dp0frontend"
set BROWSER=none
set GENERATE_SOURCEMAP=false
npm start