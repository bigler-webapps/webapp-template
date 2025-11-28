@echo off
setlocal ENABLEDELAYEDEXPANSION

echo [INFO] Running local Docker setup...

:: 0. Load PIP_TOKEN from .env.local
if not exist .env.local (
    echo [ERROR] .env.local not found in %CD%.
    echo         Please create a file .env.local with a line:
    echo         PIP_TOKEN=ghp_your_token_here
    exit /B 1
)

set PIP_TOKEN=

for /f "usebackq tokens=1,2 delims==" %%A in (".env.local") do (
    if /I "%%A"=="PIP_TOKEN" set PIP_TOKEN=%%B
)

if "%PIP_TOKEN%"=="" (
    echo [ERROR] PIP_TOKEN is not set in .env.local.
    echo         Add a line like:
    echo         PIP_TOKEN=ghp_your_token_here
    exit /B 1
)



:: 2. Generate .env (Backend config)
echo [INFO] Generating .env...
python "..\webapp-management\src\django_core\scripts\generate_env.py" --env local
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to generate .env file.
    EXIT /B %ERRORLEVEL%
)

:: 3. Create .npmrc.github for Docker build (secret file)
echo [INFO] Creating .npmrc.github for Docker build...
(
    echo @michabigler:registry=https://npm.pkg.github.com
    echo //npm.pkg.github.com/:_authToken=%PIP_TOKEN%
    echo always-auth=true
) > .npmrc.github

:: 4. Enable BuildKit (required for --mount=type=secret)
set DOCKER_BUILDKIT=1

:: 5. Build
echo [INFO] Building containers...
docker-compose build
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] docker-compose build failed.
    del .npmrc.github >NUL 2>&1
    EXIT /B %ERRORLEVEL%
)

:: 5. Start
echo [INFO] Starting containers...
docker-compose up -d
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] docker-compose up failed.
    del .npmrc.github >NUL 2>&1
    EXIT /B %ERRORLEVEL%
)

:: 6. Run migrations
echo [INFO] Running migrations...
docker-compose exec backend python manage.py migrate
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] manage.py migrate failed.
    del .npmrc.github >NUL 2>&1
    EXIT /B %ERRORLEVEL%
)


:: 7. Cleanup
echo [INFO] Cleaning up .npmrc.github...
del .npmrc.github >NUL 2>&1

echo [INFO] Done.
endlocal
