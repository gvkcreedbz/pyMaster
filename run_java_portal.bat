@echo off
rem Java Master portal launcher (http://127.0.0.1:8766/). Same app as Py Master, Java course inside.
rem Needs a JDK 21: see java\SETUP.md  (or run:  python _dev_tools\fetch_java_libs.py --jdk)
setlocal
cd /d "%~dp0"
call run_portal.bat --track java %*
endlocal
