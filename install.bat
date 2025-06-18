@echo off
setlocal enabledelayedexpansion

echo === FUT Application Docker Installer ===
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% equ 0 (
    set "IS_ADMIN=true"
    echo Running with administrator privileges
) else (
    set "IS_ADMIN=false"
    echo Running without administrator privileges
)
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not in PATH
    echo Please install Docker Desktop first: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker daemon is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Build the Docker image
echo Building fut application...
docker build -t fut-app .
if %errorlevel% neq 0 (
    echo Error: Failed to build Docker image
    pause
    exit /b 1
)

REM Create the wrapper script
echo Installing fut command...

REM Define possible installation directories
set "SYSTEM_DIR=C:\Windows\System32"
set "USER_DIR=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps"
set "LOCAL_DIR=%LOCALAPPDATA%\Programs"

REM Create the batch file content
(
echo @echo off
echo setlocal
echo.
echo if "%%~1"=="gui" ^(
echo     echo Starting GUI mode...
echo     echo Web interface will be available at: http://localhost:8501
echo     echo Press Ctrl+C to stop the server
echo     echo.
echo     docker run --rm -it -p 8501:8501 fut-app gui
echo ^) else ^(
echo     docker run --rm -it fut-app %%*
echo ^)
) > fut.bat

REM Try installation based on privileges
set "INSTALLED=false"

if "!IS_ADMIN!"=="true" (
    REM Try system directory first if admin
    copy fut.bat "%SYSTEM_DIR%\fut.bat" >nul 2>&1
    if !errorlevel! equ 0 (
        echo Command installed to %SYSTEM_DIR%\fut.bat ^(system-wide^)
        set "INSTALLED=true"
    )
)

if "!INSTALLED!"=="false" (
    REM Try WindowsApps directory ^(user-specific, no admin needed^)
    if not exist "%USER_DIR%" mkdir "%USER_DIR%" >nul 2>&1
    copy fut.bat "%USER_DIR%\fut.bat" >nul 2>&1
    if !errorlevel! equ 0 (
        echo Command installed to %USER_DIR%\fut.bat ^(user-specific^)
        set "INSTALLED=true"
    )
)

if "!INSTALLED!"=="false" (
    REM Try local programs directory
    if not exist "%LOCAL_DIR%" mkdir "%LOCAL_DIR%" >nul 2>&1
    copy fut.bat "%LOCAL_DIR%\fut.bat" >nul 2>&1
    if !errorlevel! equ 0 (
        echo Command installed to %LOCAL_DIR%\fut.bat ^(user-specific^)
        echo Note: You may need to add %LOCAL_DIR% to your PATH
        set "INSTALLED=true"
    )
)

if "!INSTALLED!"=="false" (
    REM Fallback: leave in current directory
    echo Warning: Could not install to standard directories
    echo The fut.bat file has been created in the current directory
    echo You can either:
    echo   1. Run "fut" from this directory
    echo   2. Manually copy fut.bat to a directory in your PATH
    echo   3. Add this directory to your PATH
    set "INSTALLED=partial"
)

if "!INSTALLED!"=="true" (
    REM Clean up local copy
    del fut.bat >nul 2>&1
    
    echo.
    echo Installation complete!
    echo.
    echo Usage:
    echo   fut --help          # Show help
    echo   fut gui            # Start web interface at http://localhost:8501
    echo   fut template       # Create template  
    echo   fut configuracoes  # Configuration menu
    echo   fut ^<other-args^>   # Run other commands
    echo.
    echo Note: You may need to restart Command Prompt for the command to be recognized
) else (
    echo.
    echo Installation completed with warnings - see messages above
)

echo.
pause