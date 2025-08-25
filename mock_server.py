#!/usr/bin/env python3
"""
Mock Chatterbox TTS Server for testing integration
This provides the basic API endpoints that Abogen expects
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
from typing import List, Optional
import time

app = FastAPI(title="Mock Chatterbox TTS Server", version="0.1.0")

# Request models
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    speed: Optional[float] = 1.0
    language: Optional[str] = "en"

class VoiceListResponse(BaseModel):
    voices: List[str]

# Mock voices for testing
MOCK_VOICES = [
    "female_1",
    "male_1", 
    "female_2",
    "male_2",
    "narrator_1"
]

@app.get("/")
async def root():
    """Root endpoint - shows server is running"""
    return {
        "message": "Mock Chatterbox TTS Server",
        "status": "running",
        "version": "mock-0.1.0",
        "endpoints": {
            "voices": "/api/voices",
            "tts": "/api/tts",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "mock"}

@app.get("/api/voices")
async def get_voices():
    """Get available voices"""
    return {"voices": MOCK_VOICES}

@app.get("/get_predefined_voices")
async def get_predefined_voices():
    """Get predefined voices (Chatterbox format)"""
    return MOCK_VOICES

@app.get("/api/ui/initial-data")
async def get_initial_data():
    """Get initial UI data (Chatterbox format)"""
    return {
        "voices": MOCK_VOICES,
        "models": ["mock_model_1", "mock_model_2"],
        "settings": {
            "default_voice": "female_1",
            "default_speed": 1.0,
            "server_version": "mock-0.1.0"
        }
    }

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Mock TTS endpoint - returns fake audio metadata"""
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Simulate processing time
    time.sleep(0.1)
    
    # Mock audio file response (in real server this would be actual audio)
    mock_response = {
        "success": True,
        "message": "TTS completed successfully",
        "audio_url": f"/audio/mock_audio_{int(time.time())}.wav",
        "duration": len(request.text) * 0.05,  # Mock duration based on text length
        "voice_used": request.voice or "default",
        "text_length": len(request.text),
        "processing_time": 0.1,
        "format": "wav",
        "sample_rate": 22050
    }
    
    return mock_response

@app.get("/api/models")
async def get_models():
    """Get available TTS models"""
    return {
        "models": [
            {
                "name": "mock_model_1",
                "description": "Mock TTS Model 1", 
                "languages": ["en", "es"],
                "voices": MOCK_VOICES[:3]
            },
            {
                "name": "mock_model_2", 
                "description": "Mock TTS Model 2",
                "languages": ["en"],
                "voices": MOCK_VOICES[3:]
            }
        ]
    }

if __name__ == "__main__":
    print("🎭 Starting Mock Chatterbox TTS Server...")
    print("📡 Server will be available at: http://localhost:8004")
    print("📖 API documentation: http://localhost:8004/docs")
    print("🔍 Health check: http://localhost:8004/health")
    print("\n🚀 Server starting...")
    
    uvicorn.run(
        "mock_server:app",
        host="0.0.0.0",
        port=8004,
        log_level="info",
        reload=False
    )
