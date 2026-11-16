@echo off
rem Py Master portal launcher: creates a private environment on first run, then opens the portal.
setlocal
cd /d "%~dp0"

set "PYCMD="
where py >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD (where python >nul 2>nul && set "PYCMD=python")
if not defined PYCMD (
  echo Python is not installed yet. Follow SETUP.md first, then run this file again.
  pause
  exit /b 1
)

if not exist ".venv-portal\Scripts\python.exe" (
  echo First run: creating the portal environment ^(takes a few minutes, once^)...
  %PYCMD% -m venv .venv-portal || (echo Could not create the environment. & pause & exit /b 1)
  ".venv-portal\Scripts\python.exe" -m pip install --upgrade pip --quiet
  ".venv-portal\Scripts\python.exe" -m pip install -r requirements-portal.txt || (echo Install failed. Check your internet connection and run again. & pause & exit /b 1)
)

".venv-portal\Scripts\python.exe" portal\run.py %*
endlocal
