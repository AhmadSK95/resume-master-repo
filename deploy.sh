#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Resume Matcher Deployment Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file and add your OPENAI_API_KEY${NC}"
        exit 1
    else
        echo -e "${RED}Error: .env.example not found!${NC}"
        exit 1
    fi
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not set in .env file${NC}"
    exit 1
fi

# Create data directories if they don't exist
echo -e "${GREEN}Creating data directories...${NC}"
mkdir -p data/chroma data/uploads
echo "✓ Data directories created"
echo ""

# Parse command line arguments
COMMAND=${1:-"up"}

case $COMMAND in
    up)
        echo -e "${GREEN}Building and starting containers...${NC}"
        docker-compose up -d --build
        echo ""
        echo -e "${GREEN}✓ Deployment complete!${NC}"
        echo ""
        echo "Services are now running:"
        echo "  - Frontend: http://localhost"
        echo "  - Backend API: http://localhost:5001"
        echo "  - Health Check: http://localhost:5001/api/health"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: ./deploy.sh down"
        ;;
    
    down)
        echo -e "${YELLOW}Stopping and removing containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Containers stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}Restarting containers...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Containers restarted${NC}"
        ;;
    
    logs)
        docker-compose logs -f
        ;;
    
    build)
        echo -e "${GREEN}Building containers (without starting)...${NC}"
        docker-compose build
        echo -e "${GREEN}✓ Build complete${NC}"
        ;;
    
    clean)
        echo -e "${YELLOW}Removing containers, volumes, and images...${NC}"
        read -p "This will remove all data. Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v --rmi all
            echo -e "${GREEN}✓ Cleanup complete${NC}"
        else
            echo "Cleanup cancelled"
        fi
        ;;
    
    status)
        docker-compose ps
        ;;
    
    *)
        echo "Usage: ./deploy.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  up       - Build and start containers (default)"
        echo "  down     - Stop and remove containers"
        echo "  restart  - Restart all containers"
        echo "  logs     - View container logs"
        echo "  build    - Build containers without starting"
        echo "  clean    - Remove all containers, volumes, and images"
        echo "  status   - Show container status"
        ;;
esac
