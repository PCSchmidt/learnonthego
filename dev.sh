#!/bin/bash
# LearnOnTheGo Development Script - Phase 1 AI Integration
# Ensures consistent Docker-based development environment

set -e

echo "🚀 LearnOnTheGo Phase 1 AI Integration Development"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Function to show usage
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services (backend, frontend, database)"
    echo "  backend   Start only backend services"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      Show logs for all services"
    echo "  shell     Open shell in backend container"
    echo "  build     Rebuild all containers"
    echo "  clean     Stop and remove all containers/volumes"
    echo "  status    Show running services"
    echo "  test      Run backend tests"
    echo ""
}

# Parse command
case "${1:-start}" in
    "start")
        echo "🔧 Starting LearnOnTheGo development environment..."
        docker-compose up -d
        echo "✅ Services started!"
        echo ""
        echo "📍 Backend API: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🐘 Database: localhost:5432"
        echo ""
        echo "🔍 View logs: ./dev.sh logs"
        ;;
    
    "backend")
        echo "🔧 Starting backend services only..."
        docker-compose up -d backend db redis
        echo "✅ Backend services started!"
        echo "📍 Backend API: http://localhost:8000"
        echo "📚 API Docs: http://localhost:8000/docs"
        ;;
    
    "stop")
        echo "🛑 Stopping all services..."
        docker-compose down
        echo "✅ All services stopped!"
        ;;
    
    "restart")
        echo "🔄 Restarting all services..."
        docker-compose down
        docker-compose up -d
        echo "✅ Services restarted!"
        ;;
    
    "logs")
        echo "📋 Showing logs for all services..."
        docker-compose logs -f
        ;;
    
    "shell")
        echo "🐚 Opening shell in backend container..."
        docker-compose exec backend bash
        ;;
    
    "build")
        echo "🔨 Rebuilding all containers..."
        docker-compose build --no-cache
        echo "✅ Containers rebuilt!"
        ;;
    
    "clean")
        echo "🧹 Cleaning up containers and volumes..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        echo "✅ Cleanup complete!"
        ;;
    
    "status")
        echo "📊 Service Status:"
        docker-compose ps
        ;;
    
    "test")
        echo "🧪 Running backend tests..."
        docker-compose exec backend python -m pytest
        ;;
    
    "help"|"-h"|"--help")
        show_help
        ;;
    
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac
