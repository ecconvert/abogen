#!/bin/bash
# Abogen TTS - Docker Startup Script (Linux/macOS)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CHATTERBOX_IMAGE="ecconvert/chatterbox-tts-server:latest"
COMPOSE_FILE="docker-compose.yml"

echo -e "${BLUE}🐳 Abogen TTS Docker Startup${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  docker-compose not found, trying 'docker compose'${NC}"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p input output cache

# Set up X11 permissions for GUI (Linux/macOS)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${BLUE}🖥️  Setting up X11 permissions...${NC}"
    xhost +local:docker >/dev/null 2>&1 || echo -e "${YELLOW}⚠️  Could not set X11 permissions${NC}"
    export DISPLAY=${DISPLAY:-:0}
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${BLUE}🍎 macOS detected - X11 forwarding may require XQuartz${NC}"
    export DISPLAY=${DISPLAY:-:0}
fi

# Check if Chatterbox TTS image exists or pull it
echo -e "${BLUE}📦 Checking Chatterbox TTS Server image...${NC}"
if ! docker image inspect $CHATTERBOX_IMAGE >/dev/null 2>&1; then
    echo -e "${YELLOW}⬇️  Pulling Chatterbox TTS Server image...${NC}"
    docker pull $CHATTERBOX_IMAGE || {
        echo -e "${RED}❌ Failed to pull Chatterbox image. Please check your internet connection.${NC}"
        exit 1
    }
fi

# Build Abogen image if it doesn't exist
echo -e "${BLUE}🔨 Building Abogen image...${NC}"
$DOCKER_COMPOSE build abogen

# Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
$DOCKER_COMPOSE up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 10

# Check service status
echo -e "${BLUE}📊 Service Status:${NC}"
if docker ps | grep -q "chatterbox-tts-server"; then
    echo -e "${GREEN}✅ Chatterbox TTS Server: Running${NC}"
else
    echo -e "${RED}❌ Chatterbox TTS Server: Not running${NC}"
fi

if docker ps | grep -q "abogen-app"; then
    echo -e "${GREEN}✅ Abogen Application: Running${NC}"
else
    echo -e "${RED}❌ Abogen Application: Not running${NC}"
fi

# Show URLs and next steps
echo ""
echo -e "${GREEN}🎉 Startup complete!${NC}"
echo "=================================="
echo -e "${BLUE}🌐 Chatterbox Web UI:${NC} http://localhost:8004"
echo -e "${BLUE}📁 Input folder:${NC} ./input"
echo -e "${BLUE}📁 Output folder:${NC} ./output"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Place your text/ebook files in the ./input folder"
echo "2. The Abogen GUI should launch automatically"
echo "3. Generated audiobooks will appear in ./output folder"
echo ""
echo -e "${BLUE}🔧 Management commands:${NC}"
echo "• View logs: $DOCKER_COMPOSE logs -f"
echo "• Stop services: $DOCKER_COMPOSE down"
echo "• Restart: $DOCKER_COMPOSE restart"
echo ""

# Launch GUI (attempt)
echo -e "${BLUE}🖥️  Attempting to launch Abogen GUI...${NC}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    $DOCKER_COMPOSE exec abogen python -m abogen.main &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  On macOS, you may need to install XQuartz and run 'xhost +localhost' first${NC}"
    $DOCKER_COMPOSE exec abogen python -m abogen.main &
fi

echo -e "${GREEN}✨ Setup complete! Happy audiobook generation!${NC}"
