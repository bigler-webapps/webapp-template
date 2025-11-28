@echo off
setlocal ENABLEDELAYEDEXPANSION

echo [INFO] Running local Docker setup...

:: 1. Generate .env (Backend config)
echo [INFO] Generating .env...
generate-env --env local
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to generate .env file.
    EXIT /B %ERRORLEVEL%
)
:: 2. Enable BuildKit (optional, falls du es im Dockerfile nutzt)
set DOCKER_BUILDKIT=1

:: 3. Build
echo [INFO] Building containers...
docker-compose build
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] docker-compose build failed.
    EXIT /B %ERRORLEVEL%
)

:: 4. Start
echo [INFO] Starting containers...
docker-compose up
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] docker-compose up failed.
    EXIT /B %ERRORLEVEL%
)

