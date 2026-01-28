@echo off
echo Starting Clinical Protocol AI Backend...
cd /d "%~dp0backend"
echo Backend starting on http://localhost:8000
uvicorn main:app --host 0.0.0.0 --port 8000 --reload