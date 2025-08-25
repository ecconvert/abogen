# Cross-Platform Docker Setup for Abogen + Your Chatterbox Fork

This setup allows you to:
1. ✅ Build and use your local Chatterbox fork (`ecconvert/chatterbox-tts-server`)
2. ✅ Work on both macOS and Windows without conflicts
3. ✅ Switch between local build and public images easily

## Quick Start

### Option 1: Build Your Local Chatterbox Fork (Recommended)

**Prerequisites:**
1. Clone your Chatterbox fork alongside Abogen:
   ```bash
   cd ..
   git clone https://github.com/ecconvert/chatterbox-tts-server.git
   cd abogen
   ```

2. **On macOS/Linux:**
   ```bash
   ./start-abogen-unified.sh --build-local
   ```

3. **On Windows (PowerShell):**
   ```powershell
   .\start-abogen-windows.ps1 -BuildLocal
   ```

### Option 2: Use Public Image (Fallback)

**On macOS/Linux:**
```bash
./start-abogen-unified.sh --use-public
```

**On Windows:**
```powershell
.\start-abogen-windows.ps1 -UsePublicImage
```

## File Structure

```
your-projects/
├── abogen/                          # This repository
│   ├── docker-compose.unified.yml   # Cross-platform compose
│   ├── docker-compose.windows.yml   # Windows-specific
│   ├── .env.macos                   # macOS configuration
│   ├── .env.windows                 # Windows configuration
│   ├── .env.public                  # Public image config
│   ├── Dockerfile                   # Original (macOS/Linux)
│   ├── Dockerfile.windows           # Windows-specific
│   ├── start-abogen-unified.sh      # Cross-platform script
│   └── start-abogen-windows.ps1     # Windows script
└── chatterbox-tts-server/           # Your fork (clone here)
    ├── Dockerfile
    ├── requirements.txt
    └── ...
```

## How It Works

### Platform Detection
- **macOS**: Uses X11 forwarding, native Docker
- **Windows**: Uses VNC/web interface, no X11
- **Linux**: Similar to macOS

### Build Options
- **Local Build**: Builds Chatterbox from your `../chatterbox-tts-server` fork
- **Public Image**: Uses `bhimrazy/chatterbox-tts:latest` from Docker Hub

### Environment Files
Each platform has its own environment configuration:
- `.env.macos` - macOS with X11 support
- `.env.windows` - Windows with VNC/web GUI
- `.env.public` - Cross-platform with public image

## Access Points

Once running, you can access:
- **Abogen Web GUI**: http://localhost:5800
- **Abogen VNC**: localhost:5900 (if needed)
- **Chatterbox Web UI**: http://localhost:8004

## macOS vs Windows Compatibility

### macOS Setup (Won't Be Affected)
- Your existing `start-abogen.sh` still works
- Original `docker-compose.yml` unchanged
- X11 forwarding for native GUI experience

### Windows Setup (New)
- Uses separate Windows-specific files
- Web-based GUI instead of X11
- VNC fallback option

### Files That DON'T Conflict
- `docker-compose.unified.yml` - New unified approach
- `docker-compose.windows.yml` - Windows-only
- `.env.*` files - Platform-specific configs
- `Dockerfile.windows` - Windows-specific build
- `start-abogen-windows.ps1` - Windows script

### Files That Are Original/Unchanged
- `docker-compose.yml` - Your original macOS setup
- `Dockerfile` - Your original build (enhanced but compatible)
- `start-abogen.sh` - Your original macOS script

## Building Your Local Chatterbox Fork

### Why Build Locally?
- Use your custom modifications
- Test changes before pushing
- No dependency on public Docker Hub images
- Full control over the build process

### Requirements for Local Build
1. Your Chatterbox fork cloned at `../chatterbox-tts-server`
2. Docker with enough disk space (builds can be large)
3. Good internet connection (downloads models during first run)

### Build Process
1. Detects your local fork automatically
2. Builds Chatterbox image from your source
3. Builds Abogen with platform-specific settings
4. Links them together with proper networking

## Troubleshooting

### Common Issues

**"Chatterbox repository not found"**
```bash
cd ..
git clone https://github.com/ecconvert/chatterbox-tts-server.git
cd abogen
```

**Windows X11 Errors**
- Use the Windows-specific scripts (they avoid X11)
- Access via web browser at http://localhost:5800

**macOS XQuartz Issues**
```bash
# Install XQuartz if needed
brew install --cask xquartz
# Allow localhost connections
xhost +localhost
```

**Build Failures**
- Check Docker has enough disk space
- Ensure stable internet connection
- Try `docker system prune` to free space

### Switching Between Builds

**From Public to Local:**
```bash
# macOS/Linux
./start-abogen-unified.sh --build-local

# Windows
.\start-abogen-windows.ps1 -BuildLocal
```

**From Local to Public:**
```bash
# macOS/Linux  
./start-abogen-unified.sh --use-public

# Windows
.\start-abogen-windows.ps1 -UsePublicImage
```

## Advanced Usage

### Manual Docker Compose
```bash
# Build local Chatterbox on macOS
docker-compose --env-file .env.macos -f docker-compose.unified.yml up --build

# Use public image on Windows
docker-compose --env-file .env.windows -f docker-compose.unified.yml up
```

### Custom Environment
Copy and modify an `.env.*` file for custom setups:
```bash
cp .env.macos .env.custom
# Edit .env.custom
docker-compose --env-file .env.custom -f docker-compose.unified.yml up
```

## Benefits

✅ **Cross-Platform**: Same setup works on macOS, Windows, Linux
✅ **Local Development**: Build and test your Chatterbox changes
✅ **No Conflicts**: Windows files don't affect macOS setup
✅ **Flexible**: Switch between local/public builds easily
✅ **Isolated**: Each platform uses appropriate GUI method
✅ **Future-Proof**: Easy to update either component independently