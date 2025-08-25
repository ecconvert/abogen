# Abogen Windows Docker Startup Script
# This script handles Windows-specific Docker issues and sets up Chatterbox TTS

param(
    [switch]$BuildLocal,
    [switch]$UsePublicImage,
    [switch]$Help
)

if ($Help) {
    Write-Host "Abogen Windows Docker Startup Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -BuildLocal     : Build Chatterbox from your local fork"
    Write-Host "  -UsePublicImage : Use a public Chatterbox image (default)"
    Write-Host "  -Help           : Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\start-abogen-windows.ps1                # Use public image"
    Write-Host "  .\start-abogen-windows.ps1 -BuildLocal    # Build from local fork"
    exit 0
}

Write-Host "🚀 Starting Abogen with Windows-compatible Docker setup..." -ForegroundColor Green

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker version > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Determine which setup to use
if ($BuildLocal) {
    Write-Host "🔨 Building Chatterbox from local fork..." -ForegroundColor Yellow
    
    # Check if chatterbox directory exists
    if (-not (Test-Path "../chatterbox-tts-server")) {
        Write-Host "❌ Chatterbox repository not found at ../chatterbox-tts-server" -ForegroundColor Red
        Write-Host "Please clone your fork first:" -ForegroundColor Yellow
        Write-Host "  cd .."
        Write-Host "  git clone https://github.com/ecconvert/chatterbox-tts-server.git"
        Write-Host "  cd abogen"
        exit 1
    }
    
    # Create docker-compose with local build
    $composeContent = @"
version: '3.8'

services:
  chatterbox-tts:
    build: 
      context: ../chatterbox-tts-server
      dockerfile: Dockerfile
    container_name: chatterbox-tts-server
    ports:
      - "8004:8004"
    volumes:
      - chatterbox_models:/app/models
      - chatterbox_cache:/app/cache
      - chatterbox_hf_cache:/app/hf_cache
    environment:
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  abogen:
    build: 
      context: .
      dockerfile: Dockerfile.windows
    container_name: abogen-app
    depends_on:
      - chatterbox-tts
    ports:
      - "5800:5800"
      - "5900:5900"
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./cache:/app/cache
    environment:
      - CHATTERBOX_SERVER_URL=http://chatterbox-tts:8004
      - VNC_RESOLUTION=1920x1080
    restart: unless-stopped

volumes:
  chatterbox_models:
  chatterbox_cache:
  chatterbox_hf_cache:
"@
    
} else {
    Write-Host "📦 Using public Chatterbox image..." -ForegroundColor Yellow
    
    # Use the existing windows compose file
    if (-not (Test-Path "docker-compose.windows.yml")) {
        Write-Host "❌ Windows Docker Compose file not found!" -ForegroundColor Red
        exit 1
    }
    $composeFile = "docker-compose.windows.yml"
}

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.windows.yml down 2>$null

# Pull/build images
if ($BuildLocal) {
    Write-Host "🔨 Building images (this may take several minutes)..." -ForegroundColor Yellow
    $composeContent | Out-File -FilePath "docker-compose.temp.yml" -Encoding UTF8
    docker-compose -f docker-compose.temp.yml build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        Remove-Item "docker-compose.temp.yml" -ErrorAction SilentlyContinue
        exit 1
    }
    $composeFile = "docker-compose.temp.yml"
} else {
    Write-Host "📦 Pulling public images..." -ForegroundColor Yellow
    docker-compose -f docker-compose.windows.yml pull
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Some images couldn't be pulled, will build locally..." -ForegroundColor Yellow
    }
    $composeFile = "docker-compose.windows.yml"
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose -f $composeFile up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services!" -ForegroundColor Red
    Remove-Item "docker-compose.temp.yml" -ErrorAction SilentlyContinue
    exit 1
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
$chatterboxRunning = docker ps --filter "name=chatterbox-tts-server" --filter "status=running" -q
$abogenRunning = docker ps --filter "name=abogen-app" --filter "status=running" -q

if ($chatterboxRunning -and $abogenRunning) {
    Write-Host "✅ All services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access Abogen GUI:" -ForegroundColor Cyan
    Write-Host "   Web Interface: http://localhost:5800" -ForegroundColor White
    Write-Host "   VNC Client:    localhost:5900" -ForegroundColor White
    Write-Host ""
    Write-Host "🗣️  Chatterbox TTS Server:" -ForegroundColor Cyan
    Write-Host "   Web Interface: http://localhost:8004" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Useful commands:" -ForegroundColor Cyan
    Write-Host "   View logs:     docker-compose -f $composeFile logs -f" -ForegroundColor White
    Write-Host "   Stop services: docker-compose -f $composeFile down" -ForegroundColor White
    Write-Host "   Restart:       docker-compose -f $composeFile restart" -ForegroundColor White
    
    # Try to open the web interface
    try {
        Start-Process "http://localhost:5800"
        Write-Host "🌐 Opening web interface in browser..." -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Couldn't auto-open browser. Please navigate to http://localhost:5800 manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Some services failed to start!" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose -f $composeFile logs" -ForegroundColor Yellow
}

# Cleanup temp file
Remove-Item "docker-compose.temp.yml" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "📖 For troubleshooting, see: https://github.com/ecconvert/abogen#windows" -ForegroundColor Cyan