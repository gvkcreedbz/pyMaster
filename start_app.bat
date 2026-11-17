@echo off
rem ==========================================================================================================
rem  start_app.bat  -  ONE double-click to run Py Master (Python course) and/or Java Master (Java course).
rem  Works on a Windows PC with nothing installed (no VS Code, no Python, no Java): the first run downloads a
rem  private copy of what is missing into this folder (no admin rights). After that it starts in seconds.
rem
rem    start_app.bat                 asks which course (Python / Java / both)
rem    start_app.bat py              Python course  -> http://127.0.0.1:8765/
rem    start_app.bat java            Java course    -> http://127.0.0.1:8766/
rem    start_app.bat both            both courses
rem    add  --no-browser             do not open the browser
rem ==========================================================================================================
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title Py Master / Java Master
set "PYVER=3.13.9"
set "WHICH="
set "NOBROWSER="

:args
if "%~1"=="" goto args_done
if /i "%~1"=="py" set "WHICH=py"
if /i "%~1"=="python" set "WHICH=py"
if /i "%~1"=="java" set "WHICH=java"
if /i "%~1"=="both" set "WHICH=both"
if /i "%~1"=="--no-browser" set "NOBROWSER=--no-browser"
if /i "%~1"=="-h" goto help
if /i "%~1"=="--help" goto help
if /i "%~1"=="/?" goto help
shift
goto args
:args_done

if defined WHICH goto have_choice
echo.
echo   ==================================================
echo     Py Master / Java Master  -  your local classroom
echo   ==================================================
echo.
echo     [1]  Python course   (Py Master,   http://127.0.0.1:8765)
echo     [2]  Java course     (Java Master, http://127.0.0.1:8766)
echo     [3]  Both
echo.
choice /c 123 /n /t 20 /d 1 /m "  Press 1, 2 or 3 (1 starts by itself in 20 seconds): "
if errorlevel 3 (set "WHICH=both") else if errorlevel 2 (set "WHICH=java") else (set "WHICH=py")
:have_choice

rem ---- 1. find (or create) a Python that has the portal's packages -------------------------------------------
set "PY="
call :probe ".tools\py\python.exe" && set "PY=%CD%\.tools\py\python.exe"
if not defined PY call :probe ".venv-portal\Scripts\python.exe" && set "PY=%CD%\.venv-portal\Scripts\python.exe"
if defined PY goto have_py

if exist ".tools\py\python.exe" goto portable_setup
set "SYSPY="
for %%C in ("py -3" "python") do if not defined SYSPY (%%~C -c "import sys, venv; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul && set "SYSPY=%%~C")
if not defined SYSPY goto portable_setup

echo.
echo   First run: creating a private environment with the packages the app needs.
echo   This takes a few minutes and needs the internet, once.
if not exist ".venv-portal\Scripts\python.exe" (%SYSPY% -m venv .venv-portal || goto fail_env)
".venv-portal\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv-portal\Scripts\python.exe" -m pip install -r requirements-portal.txt || goto fail_net
set "PY=%CD%\.venv-portal\Scripts\python.exe"
goto have_py

:portable_setup
echo.
echo   First run: this computer has no suitable Python, so a private copy is being set up in the .tools folder.
echo   It needs the internet and a few minutes, once. No administrator rights are needed.
set "ARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARCH=arm64"
if /i "%PROCESSOR_ARCHITECTURE%"=="x86" if not defined PROCESSOR_ARCHITEW6432 set "ARCH=win32"
if not exist ".tools" mkdir ".tools"
if exist ".tools\py\python.exe" goto have_embed
echo   [1/3] Downloading Python %PYVER% ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $ProgressPreference='SilentlyContinue'; Invoke-WebRequest 'https://www.python.org/ftp/python/%PYVER%/python-%PYVER%-embed-%ARCH%.zip' -OutFile '.tools\py.zip' -UseBasicParsing; if (Test-Path '.tools\py') { Remove-Item -Recurse -Force '.tools\py' }; Expand-Archive '.tools\py.zip' '.tools\py' -Force; Remove-Item '.tools\py.zip'; $p=(Get-ChildItem '.tools\py' -Filter 'python*._pth' | Select-Object -First 1).FullName; (Get-Content $p) -replace '#import site','import site' | Set-Content $p -Encoding ascii" || goto fail_net
:have_embed
".tools\py\python.exe" -m pip --version >nul 2>nul && goto have_pip
echo   [2/3] Installing the package installer ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $ProgressPreference='SilentlyContinue'; Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile '.tools\py\get-pip.py' -UseBasicParsing" || goto fail_net
".tools\py\python.exe" ".tools\py\get-pip.py" --no-warn-script-location --quiet || goto fail_net
:have_pip
echo   [3/3] Installing the app's packages (the longest step) ...
".tools\py\python.exe" -m pip install --no-warn-script-location -r requirements-portal.txt || goto fail_net
set "PY=%CD%\.tools\py\python.exe"

:have_py
rem ---- 2. Java course: needs a JDK 21 and a few jars (only when the Java course was chosen) ------------------------
if /i "%WHICH%"=="py" goto launch
call :ensure_java || goto fail_java

:launch
set "PYTHONUTF8=1"
echo.
echo   Starting. Keep this window open while you learn; close it (or press Ctrl+C) to stop the app.
echo.
if /i "%WHICH%"=="py" goto run_py
if /i "%WHICH%"=="java" goto run_java

rem ---- both: Java in its own minimized window, Python in this one ------------------------------------------------
call :running 8766 && goto both_java_up
start "Java Master (8766)" /min "%PY%" -X utf8 -W ignore portal\run.py --track java --no-browser
:both_java_up
if not defined NOBROWSER (timeout /t 6 /nobreak >nul & start "" "http://127.0.0.1:8766/")
goto run_py

:run_py
call :running 8765 && (echo   Py Master is already running: http://127.0.0.1:8765/ & if not defined NOBROWSER start "" "http://127.0.0.1:8765/" & goto done)
echo   Py Master (Python course)  at  http://127.0.0.1:8765/
"%PY%" -X utf8 -W ignore portal\run.py %NOBROWSER%
goto done

:run_java
call :running 8766 && (echo   Java Master is already running: http://127.0.0.1:8766/ & if not defined NOBROWSER start "" "http://127.0.0.1:8766/" & goto done)
echo   Java Master (Java course)  at  http://127.0.0.1:8766/
"%PY%" -X utf8 -W ignore portal\run.py --track java %NOBROWSER%
goto done

:done
endlocal
exit /b 0

rem ---- helpers ----------------------------------------------------------------------------------------------------------
:probe
rem  Does this Python exist and already have the portal's packages?
if not exist "%~1" exit /b 1
"%~1" -c "import fastapi, uvicorn, pydantic, httpx" >nul 2>nul
exit /b %errorlevel%

:running
rem  Is something already listening on this port?
netstat -ano | findstr /r /c:":%~1 .*LISTENING" >nul
exit /b %errorlevel%

:is21
rem  Is the javac given as %1 a JDK 21 or newer?
"%~1" -version >nul 2>nul || exit /b 1
set "JV="
for /f "tokens=2" %%v in ('"%~1" -version 2^>^&1') do set "JV=%%v"
if not defined JV exit /b 1
for /f "delims=." %%m in ("%JV%") do if %%m GEQ 21 exit /b 0
exit /b 1

:ensure_java
if exist ".tools\jdk21\bin\javac.exe" goto use_local_jdk
if defined JAVA_HOME call :is21 "%JAVA_HOME%\bin\javac.exe" && goto java_libs
call :is21 javac && goto use_path_jdk
echo.
echo   Java course: Java 21 was not found, so a private copy is being downloaded (about 190 MB, once).
"%PY%" _dev_tools\fetch_java_libs.py --jdk || exit /b 1
set "JAVA_HOME=%CD%\.tools\jdk21"
:use_local_jdk
set "JAVA_HOME=%CD%\.tools\jdk21"
goto java_libs
:use_path_jdk
set "JAVA_HOME="
:java_libs
if exist "java\lib\sqlite-jdbc-3.46.1.0.jar" if exist "java\lib\junit-platform-console-standalone-1.10.3.jar" exit /b 0
echo   Java course: downloading the small helper libraries (JUnit, SQLite) ...
"%PY%" _dev_tools\fetch_java_libs.py || exit /b 1
exit /b 0

:help
echo.
echo   start_app.bat [py ^| java ^| both] [--no-browser]
echo.
echo     py      Python course  (Py Master)    http://127.0.0.1:8765/
echo     java    Java course    (Java Master)  http://127.0.0.1:8766/
echo     both    both of them
echo     (no option)  asks which one
echo.
echo   First run installs what is missing into this folder (needs the internet once). See README.md.
exit /b 0

:fail_net
echo.
echo   Setup could not finish. The usual reason is no internet connection (it is needed the first time only).
echo   Connect, then double-click start_app.bat again: it continues where it stopped.
echo.
pause
exit /b 1

:fail_env
echo.
echo   Could not create the private environment. Delete the folder .venv-portal and run start_app.bat again.
echo.
pause
exit /b 1

:fail_java
echo.
echo   The Java part could not be set up (it needs the internet the first time). The Python course still works:
echo   run  start_app.bat py
echo.
pause
exit /b 1
