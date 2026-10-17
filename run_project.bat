@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  start "Transportation Python Server" cmd /k py -3 transportation_server.py
) else (
  start "Transportation Python Server" cmd /k python transportation_server.py
)
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000/graph.html"
