#!/bin/bash

# AI-Ops Platform Deployment Script
# Usage: ./deploy.sh [start|stop|restart|logs|status|build]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="aiops"
COMPOSE_FILE="docker-compose.yml"

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Determine docker compose command
get_compose_cmd() {
    if docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

COMPOSE_CMD=$(get_compose_cmd)

start() {
    print_status "Starting AI-Ops Platform..."

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        print_warning "Please update .env file with your production values!"
    fi

    $COMPOSE_CMD -f $COMPOSE_FILE up -d

    print_status "Waiting for services to be healthy..."
    sleep 10

    print_status "AI-Ops Platform started successfully!"
    echo ""
    echo "=========================================="
    echo "  Frontend: http://localhost:7026"
    echo "  Backend:  http://localhost:7027"
    echo "  API Docs: http://localhost:7027/api/docs"
    echo "=========================================="
}

stop() {
    print_status "Stopping AI-Ops Platform..."
    $COMPOSE_CMD -f $COMPOSE_FILE down
    print_status "AI-Ops Platform stopped."
}

restart() {
    print_status "Restarting AI-Ops Platform..."
    stop
    start
}

build() {
    print_status "Building AI-Ops Platform containers..."
    $COMPOSE_CMD -f $COMPOSE_FILE build --no-cache
    print_status "Build completed."
}

logs() {
    SERVICE=${2:-""}
    if [ -z "$SERVICE" ]; then
        $COMPOSE_CMD -f $COMPOSE_FILE logs -f
    else
        $COMPOSE_CMD -f $COMPOSE_FILE logs -f $SERVICE
    fi
}

status() {
    print_status "AI-Ops Platform Status:"
    echo ""
    $COMPOSE_CMD -f $COMPOSE_FILE ps
    echo ""

    # Check health endpoints
    print_status "Checking service health..."

    if curl -s http://localhost:7027/health > /dev/null 2>&1; then
        echo -e "Backend:  ${GREEN}HEALTHY${NC}"
    else
        echo -e "Backend:  ${RED}UNHEALTHY${NC}"
    fi

    if curl -s http://localhost:7026/health > /dev/null 2>&1; then
        echo -e "Frontend: ${GREEN}HEALTHY${NC}"
    else
        echo -e "Frontend: ${RED}UNHEALTHY${NC}"
    fi
}

update() {
    print_status "Updating AI-Ops Platform..."

    # Pull latest code (if using git)
    if [ -d ".git" ]; then
        print_status "Pulling latest code..."
        git pull
    fi

    # Rebuild and restart
    build
    restart

    print_status "Update completed."
}

backup() {
    print_status "Creating database backup..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    docker exec aiops-postgres pg_dump -U aiops aiops_db > "backups/$BACKUP_FILE"
    print_status "Backup created: backups/$BACKUP_FILE"
}

# Main
check_requirements

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    build)
        build
        ;;
    logs)
        logs "$@"
        ;;
    status)
        status
        ;;
    update)
        update
        ;;
    backup)
        mkdir -p backups
        backup
        ;;
    *)
        echo "AI-Ops Platform Deployment Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|build|logs|status|update|backup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  build   - Rebuild all containers"
        echo "  logs    - View logs (optionally specify service: logs backend)"
        echo "  status  - Check service status"
        echo "  update  - Pull latest code and rebuild"
        echo "  backup  - Create database backup"
        exit 1
        ;;
esac
