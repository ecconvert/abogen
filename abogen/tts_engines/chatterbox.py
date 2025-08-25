"""Chatterbox TTS Engine implementation for Abogen."""

import requests
import json
import base64
import re
import time
from typing import List, Dict, Any, Iterator, Optional
from .base import TTSEngine, AudioResult, AudioToken
try:
    import numpy as np
except ImportError:
    np = None


class ChatterboxEngine(TTSEngine):
    """Chatterbox TTS Server implementation."""
    
    def __init__(self, server_url: str, timeout: float = 30.0):
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self._available_voices = None
        self._connection_tested = False
    
    def _test_connection(self):
        """Test connection to Chatterbox server."""
        try:
            response = requests.get(f"{self.server_url}/api/ui/initial-data", timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to Chatterbox server at {self.server_url}: {e}")
    
    def _refresh_voices(self):
        """Refresh available voices from server."""
        try:
            # Get predefined voices
            response = requests.get(f"{self.server_url}/get_predefined_voices", timeout=self.timeout)
            response.raise_for_status()
            predefined = response.json()
            
            # Get reference files for cloning
            response = requests.get(f"{self.server_url}/get_reference_files", timeout=self.timeout)
            response.raise_for_status()
            reference = response.json()
            
            # Combine both lists with prefixes for clarity
            voices = []
            for voice in predefined:
                voices.append(f"predefined:{voice.get('filename', voice.get('display_name', 'unknown'))}")
            
            for ref_file in reference:
                voices.append(f"reference:{ref_file}")
            
            self._available_voices = voices
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not refresh voices from Chatterbox server: {e}")
            self._available_voices = []
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices."""
        if self._available_voices is None:
            if not self._connection_tested:
                self._test_connection()
                self._connection_tested = True
            self._refresh_voices()
        return self._available_voices
    
    def _split_text_into_chunks(self, text: str, split_pattern: str, chunk_size: int = 300) -> List[str]:
        """Split text into manageable chunks."""
        # Split by pattern first (usually newlines)
        segments = re.split(split_pattern, text)
        
        chunks = []
        current_chunk = ""
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
                
            # If adding this segment would exceed chunk size, finalize current chunk
            if current_chunk and len(current_chunk) + len(segment) + 1 > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = segment
            else:
                if current_chunk:
                    current_chunk += " " + segment
                else:
                    current_chunk = segment
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text]
    
    def _synthesize_chunk(self, text: str, voice: str, speed: float = 1.0) -> Dict[str, Any]:
        """Synthesize a single chunk of text."""
        # Parse voice format
        voice_mode = "predefined"
        voice_id = None
        
        if voice.startswith("predefined:"):
            voice_mode = "predefined"
            voice_id = voice[11:]  # Remove "predefined:" prefix
        elif voice.startswith("reference:"):
            voice_mode = "clone"
            voice_id = voice[10:]  # Remove "reference:" prefix
        else:
            # Default to predefined
            voice_mode = "predefined"
            voice_id = voice
        
        payload = {
            "text": text,
            "voice_mode": voice_mode,
            "output_format": "wav",
            "split_text": False,  # We handle chunking ourselves
            "speed_factor": speed,
            "seed": 42,  # Use consistent seed for reproducibility
        }
        
        if voice_mode == "predefined":
            payload["predefined_voice_id"] = voice_id
        else:
            payload["reference_audio_filename"] = voice_id
        
        try:
            response = requests.post(
                f"{self.server_url}/tts",
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Get audio data as bytes
            audio_bytes = response.content
            
            # Convert to numpy array (assuming WAV format)
            if np is not None:
                # Simple WAV parsing - skip header (44 bytes) and convert to float32
                wav_data = audio_bytes[44:]  # Skip WAV header
                audio_array = np.frombuffer(wav_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                # Fallback if numpy not available
                audio_array = list(audio_bytes)
            
            return {
                "audio": audio_array,
                "sample_rate": 24000,  # Chatterbox default
                "text": text
            }
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to synthesize audio: {e}")
    
    def _create_simple_tokens(self, text: str, audio_duration: float) -> List[AudioToken]:
        """Create simple token timing based on text length."""
        words = text.split()
        if not words:
            return []
        
        tokens = []
        time_per_word = audio_duration / len(words)
        
        for i, word in enumerate(words):
            start_time = i * time_per_word
            end_time = (i + 1) * time_per_word
            
            tokens.append(AudioToken(
                text=word,
                whitespace=" " if i < len(words) - 1 else "",
                start_ts=start_time,
                end_ts=end_time
            ))
        
        return tokens
    
    def generate(self, text: str, voice: str, speed: float = 1.0, 
                split_pattern: str = r"\n+") -> Iterator[AudioResult]:
        """Generate audio from text with timing information."""
        # Split text into manageable chunks
        chunks = self._split_text_into_chunks(text, split_pattern)
        
        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Synthesize this chunk
            result = self._synthesize_chunk(chunk, voice, speed)
            
            # Calculate audio duration
            audio_array = result["audio"]
            sample_rate = result["sample_rate"]
            
            if np is not None and hasattr(audio_array, '__len__'):
                duration = len(audio_array) / sample_rate
            else:
                # Fallback duration estimation
                duration = len(chunk) * 0.1  # Rough estimate: 0.1 seconds per character
            
            # Create simple token timing
            tokens = self._create_simple_tokens(chunk, duration)
            
            yield AudioResult(
                audio=audio_array,
                graphemes=chunk,
                tokens=tokens
            )
    
    def supports_voice_mixing(self) -> bool:
        """Chatterbox doesn't support voice mixing like Kokoro."""
        return False
    
    def get_device(self) -> str:
        """Get device information from server."""
        try:
            response = requests.get(f"{self.server_url}/api/ui/initial-data", timeout=10)
            response.raise_for_status()
            data = response.json()
            # Extract device info if available in config
            return "gpu"  # Assume GPU if server is running
        except:
            return "unknown"
