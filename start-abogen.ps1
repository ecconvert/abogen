# Abogen TTS - Docker Startup Script (Windows)
# PowerShell script for Windows with NVIDIA GPU support

param(
    [switch]$NoGUI,
    [switch]$Verbose
)

# Configuration
$ChatterboxImage = "ecconvert/chatterbox-tts-server:latest"
$ComposeFile = "docker-compose.yml"

# Colors for Windows Terminal
function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    $colors = @{
        "Red" = "Red"
        "Green" = "Green" 
        "Yellow" = "Yellow"
        "Blue" = "Cyan"
        "White" = "White"
    }
    Write-Host $Text -ForegroundColor $colors[$Color]
}

Write-ColorText "🐳 Abogen TTS Docker Startup (Windows)" "Blue"
Write-ColorText "======================================" "Blue"

# Check if Docker Desktop is running
try {
    docker info | Out-Null
    Write-ColorText "✅ Docker Desktop is running" "Green"
} catch {
    Write-ColorText "❌ Docker Desktop is not running. Please start Docker Desktop and try again." "Red"
    Write-ColorText "You can download it from: https://www.docker.com/products/docker-desktop/" "Yellow"
    exit 1
}

# Check for NVIDIA Docker support
try {
    docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi | Out-Null
    Write-ColorText "✅ NVIDIA GPU support detected" "Green"
} catch {
    Write-ColorText "⚠️  NVIDIA GPU support not detected. Install NVIDIA Container Toolkit:" "Yellow"
    Write-ColorText "   https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html" "Yellow"
}

# Check Docker Compose
$DockerCompose = "docker-compose"
try {
    & $DockerCompose version | Out-Null
} catch {
    Write-ColorText "⚠️  docker-compose not found, trying 'docker compose'" "Yellow"
    $DockerCompose = "docker compose"
}

# Create necessary directories
Write-ColorText "📁 Creating directories..." "Blue"
$directories = @("input", "output", "cache")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-ColorText "   Created: $dir" "Green"
    }
}

# Check if Chatterbox TTS image exists
Write-ColorText "📦 Checking Chatterbox TTS Server image..." "Blue"
try {
    docker image inspect $ChatterboxImage | Out-Null
    Write-ColorText "✅ Chatterbox image found" "Green"
} catch {
    Write-ColorText "⬇️  Pulling Chatterbox TTS Server image..." "Yellow"
    try {
        docker pull $ChatterboxImage
        Write-ColorText "✅ Chatterbox image pulled successfully" "Green"
    } catch {
        Write-ColorText "❌ Failed to pull Chatterbox image. Check internet connection." "Red"
        exit 1
    }
}

# Build Abogen image
Write-ColorText "🔨 Building Abogen image..." "Blue"
try {
    & $DockerCompose build abogen
    Write-ColorText "✅ Abogen image built successfully" "Green"
} catch {
    Write-ColorText "❌ Failed to build Abogen image" "Red"
    exit 1
}

# Start services
Write-ColorText "🚀 Starting services..." "Blue"
try {
    & $DockerCompose up -d
    Write-ColorText "✅ Services started" "Green"
} catch {
    Write-ColorText "❌ Failed to start services" "Red"
    exit 1
}

# Wait for services
Write-ColorText "⏳ Waiting for services to initialize..." "Blue"
Start-Sleep -Seconds 15

# Check service status
Write-ColorText "📊 Service Status:" "Blue"
$chatterboxRunning = docker ps --filter "name=chatterbox-tts-server" --format "table {{.Names}}" | Select-String "chatterbox"
$abogenRunning = docker ps --filter "name=abogen-app" --format "table {{.Names}}" | Select-String "abogen"

if ($chatterboxRunning) {
    Write-ColorText "✅ Chatterbox TTS Server: Running" "Green"
} else {
    Write-ColorText "❌ Chatterbox TTS Server: Not running" "Red"
}

if ($abogenRunning) {
    Write-ColorText "✅ Abogen Application: Running" "Green"
} else {
    Write-ColorText "❌ Abogen Application: Not running" "Red"
}

# Show information
Write-ColorText "" "White"
Write-ColorText "🎉 Startup complete!" "Green"
Write-ColorText "======================================" "Blue"
Write-ColorText "🌐 Chatterbox Web UI: http://localhost:8004" "Blue"
Write-ColorText "📁 Input folder: .\input" "Blue"  
Write-ColorText "📁 Output folder: .\output" "Blue"
Write-ColorText "" "White"
Write-ColorText "📋 Next steps:" "Yellow"
Write-ColorText "1. Place your text/ebook files in the .\input folder" "White"
Write-ColorText "2. Access the Chatterbox web UI to verify it's working" "White"
Write-ColorText "3. Run Abogen GUI: docker-compose exec abogen python -m abogen.main" "White"
Write-ColorText "4. Generated audiobooks will appear in .\output folder" "White"
Write-ColorText "" "White"
Write-ColorText "🔧 Management commands:" "Blue"
Write-ColorText "• View logs: $DockerCompose logs -f" "White"
Write-ColorText "• Stop services: $DockerCompose down" "White"
Write-ColorText "• Restart: $DockerCompose restart" "White"
Write-ColorText "• Open GUI: $DockerCompose exec abogen python -m abogen.main" "White"
Write-ColorText "" "White"

if (!$NoGUI) {
    Write-ColorText "🖥️  Note: GUI in Docker on Windows requires X Server (e.g., VcXsrv)" "Yellow"
    Write-ColorText "   Alternative: Use the web interface or run Abogen natively on Windows" "Yellow"
}

Write-ColorText "✨ Setup complete! Happy audiobook generation!" "Green"
