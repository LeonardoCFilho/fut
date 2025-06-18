@echo off
setlocal enabledelayedexpansion

REM Check if the first argument is 'gui'
if "%1"=="gui" (
    echo Starting GUI mode...
    echo Web interface will be available at: http://localhost:8501
    echo Press Ctrl+C to stop the server
    echo.
    
    REM Stop any existing containers using port 8501
    echo Checking for existing containers on port 8501...
    for /f "tokens=*" %%i in ('docker ps -q --filter "publish=8501" 2^>nul') do (
        set "existing_containers=%%i"
    )
    
    if defined existing_containers (
        echo Stopping existing containers: !existing_containers!
        docker stop !existing_containers!
        docker rm !existing_containers!
        timeout /t 2 /nobreak >nul
    )
    
    REM Generate timestamp for container name
    for /f "tokens=2 delims==" %%i in ('wmic OS Get localdatetime /value') do set "dt=%%i"
    set "timestamp=%dt:~0,8%-%dt:~8,6%"
    set "container_name=fut-gui-%timestamp%"
    
    REM Start container with explicit port mapping
    echo Starting container with command:
    echo docker run --rm --name !container_name! -p 8501:8501 fut-app gui
    echo.
    
    REM Run the container
    docker run --rm --name "!container_name!" -p 8501:8501 fut-app gui
    
) else (
    REM For all other commands, run normally
    echo Running command: docker run --rm -it fut-app %*
    docker run --rm -it fut-app %*
)