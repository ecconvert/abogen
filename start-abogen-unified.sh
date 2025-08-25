#!/bin/bash
# Abogen TTS - Cross-Platform Docker Startup Script
# Supports building local Chatterbox fork and works on macOS/Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
BUILD_LOCAL=false
USE_PUBLIC=false
PLATFORM=""
ENV_FILE=""

# Help function
show_help() {
    echo -e "${GREEN}Abogen Cross-Platform Docker Setup${NC}"
    echo "======================================"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --build-local    Build Chatterbox from your local fork"
    echo "  --use-public     Use a public Chatterbox image"
    echo "  --platform NAME  Force platform (macos, linux, windows)"
    echo "  --help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --build-local     # Build from ../chatterbox-tts-server"
    echo "  $0 --use-public      # Use public image"
    echo "  $0                   # Auto-detect and build local if available"
    echo ""
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build-local)
            BUILD_LOCAL=true
            shift
            ;;
        --use-public)
            USE_PUBLIC=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            ;;
    esac
done

echo -e "${BLUE}🐳 Abogen Cross-Platform Docker Setup${NC}"
echo "========================================"

# Detect platform if not specified
if [[ -z "$PLATFORM" ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        PLATFORM="windows"
    else
        echo -e "${YELLOW}⚠️  Unknown platform, defaulting to linux${NC}"
        PLATFORM="linux"
    fi
fi

echo -e "${CYAN}📱 Platform: $PLATFORM${NC}"

# Check if Docker is running
echo -e "${BLUE}🔍 Checking Docker...${NC}"
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check for Docker Compose
if ! command -v docker-compose >/dev/null 2>&1; then
    if ! docker compose version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose not found${NC}"
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Determine build strategy
if [[ "$USE_PUBLIC" == "true" ]]; then
    echo -e "${BLUE}📦 Using public Chatterbox image${NC}"
    ENV_FILE=".env.public"
elif [[ "$BUILD_LOCAL" == "true" ]]; then
    echo -e "${BLUE}🔨 Building Chatterbox from local fork${NC}"
    # Check if local fork exists
    if [[ ! -d "../chatterbox-tts-server" ]]; then
        echo -e "${RED}❌ Chatterbox repository not found at ../chatterbox-tts-server${NC}"
        echo -e "${YELLOW}Please clone your fork first:${NC}"
        echo "  cd .."
        echo "  git clone https://github.com/ecconvert/chatterbox-tts-server.git"
        echo "  cd abogen"
        exit 1
    fi
    
    if [[ "$PLATFORM" == "macos" ]]; then
        ENV_FILE=".env.macos"
    elif [[ "$PLATFORM" == "windows" ]]; then
        ENV_FILE=".env.windows"
    else
        ENV_FILE=".env.macos"  # Use macOS config for Linux too
    fi
else
    # Auto-detect: try local first, fall back to public
    if [[ -d "../chatterbox-tts-server" ]]; then
        echo -e "${BLUE}🔨 Auto-detected local Chatterbox fork, building locally${NC}"
        BUILD_LOCAL=true
        if [[ "$PLATFORM" == "macos" ]]; then
            ENV_FILE=".env.macos"
        elif [[ "$PLATFORM" == "windows" ]]; then
            ENV_FILE=".env.windows"
        else
            ENV_FILE=".env.macos"
        fi
    else
        echo -e "${BLUE}📦 No local fork found, using public image${NC}"
        ENV_FILE=".env.public"
    fi
fi

# Create directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p input output cache shared

# Platform-specific setup
if [[ "$PLATFORM" == "macos" ]]; then
    echo -e "${BLUE}🍎 macOS setup...${NC}"
    if command -v xhost >/dev/null 2>&1; then
        xhost +localhost >/dev/null 2>&1 || echo -e "${YELLOW}⚠️  Could not set X11 permissions${NC}"
    else
        echo -e "${YELLOW}⚠️  XQuartz not found. GUI may not work properly.${NC}"
        echo -e "${YELLOW}   Install XQuartz: https://www.xquartz.org/${NC}"
    fi
    export DISPLAY=${DISPLAY:-:0}
elif [[ "$PLATFORM" == "linux" ]]; then
    echo -e "${BLUE}🐧 Linux setup...${NC}"
    xhost +local:docker >/dev/null 2>&1 || echo -e "${YELLOW}⚠️  Could not set X11 permissions${NC}"
    export DISPLAY=${DISPLAY:-:0}
fi

# Stop existing containers
echo -e "${BLUE}🛑 Stopping existing containers...${NC}"
$DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml down 2>/dev/null || true

# Build/Pull images
if [[ "$BUILD_LOCAL" == "true" ]]; then
    echo -e "${BLUE}🔨 Building images (this may take several minutes)...${NC}"
    $DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml build --no-cache
else
    echo -e "${BLUE}📦 Pulling images...${NC}"
    $DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml pull
fi

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
$DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml up -d

# Wait for services
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 15

# Check service status
echo -e "${BLUE}📊 Service Status:${NC}"
if docker ps | grep -q "chatterbox-tts-server"; then
    echo -e "${GREEN}✅ Chatterbox TTS Server: Running${NC}"
    CHATTERBOX_OK=true
else
    echo -e "${RED}❌ Chatterbox TTS Server: Not running${NC}"
    CHATTERBOX_OK=false
fi

if docker ps | grep -q "abogen-app"; then
    echo -e "${GREEN}✅ Abogen Application: Running${NC}"
    ABOGEN_OK=true
else
    echo -e "${RED}❌ Abogen Application: Not running${NC}"
    ABOGEN_OK=false
fi

# Show results
echo ""
if [[ "$CHATTERBOX_OK" == "true" && "$ABOGEN_OK" == "true" ]]; then
    echo -e "${GREEN}🎉 All services started successfully!${NC}"
    echo "====================================="
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo -e "   Abogen Web UI:    ${GREEN}http://localhost:5800${NC}"
    echo -e "   Abogen VNC:       ${GREEN}localhost:5900${NC}"
    echo -e "   Chatterbox Web:   ${GREEN}http://localhost:8004${NC}"
    echo ""
    echo -e "${CYAN}📁 File Locations:${NC}"
    echo -e "   Input:  ${GREEN}./input${NC}   (place your files here)"
    echo -e "   Output: ${GREEN}./output${NC}  (generated audiobooks)"
    echo -e "   Shared: ${GREEN}./shared${NC}  (container file access)"
    echo ""
    echo -e "${CYAN}🔧 Management:${NC}"
    echo -e "   View logs:    ${WHITE}$DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml logs -f${NC}"
    echo -e "   Stop:         ${WHITE}$DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml down${NC}"
    echo -e "   Restart:      ${WHITE}$DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml restart${NC}"
    
    # Try to open web interface
    if command -v open >/dev/null 2>&1; then  # macOS
        open http://localhost:5800 2>/dev/null &
    elif command -v xdg-open >/dev/null 2>&1; then  # Linux
        xdg-open http://localhost:5800 2>/dev/null &
    fi
    
else
    echo -e "${RED}❌ Some services failed to start${NC}"
    echo -e "${YELLOW}Check logs: $DOCKER_COMPOSE --env-file $ENV_FILE -f docker-compose.unified.yml logs${NC}"
fi

echo ""
echo -e "${GREEN}✨ Setup complete!${NC}"