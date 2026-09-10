@echo off
REM Start local development environment using Docker Compose on Windows

cd /d "%~dp0\.."

IF NOT EXIST .env (
    echo ⚠️ .env file not found. Copying from .env.example...
    copy .env.example .env
)

docker compose -f docker-compose.dev.yml up --build %*
