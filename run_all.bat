@echo off
rem Start BOTH portals: Py Master (8765) and Java Master (8766), each in its own window.
setlocal
cd /d "%~dp0"
start "Py Master (8765)" cmd /c run_portal.bat
timeout /t 3 /nobreak >nul
start "Java Master (8766)" cmd /c run_java_portal.bat --no-browser
timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:8766/"
endlocal
