# Abogen TTS Audiobook Generator - Docker Container
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # GUI dependencies
    python3-pyqt5 \
    python3-pyqt5.qtmultimedia \
    qtbase5-dev \
    qtmultimedia5-dev \
    # Audio dependencies
    ffmpeg \
    pulseaudio \
    alsa-utils \
    # X11 dependencies for GUI
    xvfb \
    x11-apps \
    x11-utils \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    # Build dependencies
    build-essential \
    pkg-config \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GUI
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1
ENV QT_GRAPHICSSYSTEM=native

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for input/output
RUN mkdir -p /app/input /app/output /app/cache

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 abogen && \
    chown -R abogen:abogen /app
USER abogen

# Expose GUI port (if using VNC - optional)
EXPOSE 5900

# Default command
CMD ["python", "-m", "abogen.main"]
