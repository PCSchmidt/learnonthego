@echo off
REM LearnOnTheGo Development Script
REM Docker-based development environment

echo LearnOnTheGo Development Environment
echo =====================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Parse command
set "command=%~1"
if "%command%"=="" set "command=start"

if "%command%"=="start" (
    echo 🔧 Starting LearnOnTheGo development environment...
    docker-compose up -d
    echo ✅ Services started!
    echo.
    echo 📍 Backend API: http://localhost:8000
    echo 📚 API Docs: http://localhost:8000/docs
    echo 🌐 Frontend: http://localhost:3000
    echo 🐘 Database: localhost:5432
    echo.
    echo 🔍 View logs: dev.bat logs
    goto :end
)

if "%command%"=="backend" (
    echo 🔧 Starting backend services only...
    docker-compose up -d backend db redis
    echo ✅ Backend services started!
    echo 📍 Backend API: http://localhost:8000
    echo 📚 API Docs: http://localhost:8000/docs
    goto :end
)

if "%command%"=="stop" (
    echo 🛑 Stopping all services...
    docker-compose down
    echo ✅ All services stopped!
    goto :end
)

if "%command%"=="restart" (
    echo 🔄 Restarting all services...
    docker-compose down
    docker-compose up -d
    echo ✅ Services restarted!
    goto :end
)

if "%command%"=="logs" (
    echo 📋 Showing logs for all services...
    docker-compose logs -f
    goto :end
)

if "%command%"=="shell" (
    echo 🐚 Opening shell in backend container...
    docker-compose exec backend bash
    goto :end
)

if "%command%"=="build" (
    echo 🔨 Rebuilding all containers...
    docker-compose build --no-cache
    echo ✅ Containers rebuilt!
    goto :end
)

if "%command%"=="clean" (
    echo 🧹 Cleaning up containers and volumes...
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo ✅ Cleanup complete!
    goto :end
)

if "%command%"=="status" (
    echo 📊 Service Status:
    docker-compose ps
    goto :end
)

if "%command%"=="test" (
    echo 🧪 Running backend tests...
    docker-compose exec backend python -m pytest
    goto :end
)

if "%command%"=="help" (
    goto :help
)

echo ❌ Unknown command: %command%
goto :help

:help
echo Usage: dev.bat [COMMAND]
echo.
echo Commands:
echo   start     Start all services (backend, frontend, database)
echo   backend   Start only backend services
echo   stop      Stop all services
echo   restart   Restart all services
echo   logs      Show logs for all services
echo   shell     Open shell in backend container
echo   build     Rebuild all containers
echo   clean     Stop and remove all containers/volumes
echo   status    Show running services
echo   test      Run backend tests
echo.

:end
