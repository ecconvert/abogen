"""Base TTS Engine interface for Abogen."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class AudioToken:
    """Represents a token with timing information."""
    text: str
    whitespace: str = ""
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None


@dataclass
class AudioResult:
    """Represents the result of TTS synthesis."""
    audio: np.ndarray
    graphemes: str
    tokens: List[AudioToken]
    sample_rate: int = 22050
    
    @property
    def duration(self) -> float:
        """Calculate the duration of the audio in seconds."""
        return len(self.audio) / self.sample_rate


class TTSEngine(ABC):
    """Abstract base class for TTS engines."""
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Get list of available voices."""
        pass
    
    @abstractmethod
    def generate(self, text: str, voice: str, speed: float = 1.0, 
                split_pattern: str = r"\n+") -> Iterator[AudioResult]:
        """Generate audio from text with timing information."""
        pass
    
    @abstractmethod
    def supports_voice_mixing(self) -> bool:
        """Check if engine supports voice mixing/formulas."""
        pass
    
    @abstractmethod
    def get_device(self) -> str:
        """Get the device being used (cpu, cuda, mps)."""
        pass
    
    def __call__(self, text: str, voice: str, speed: float = 1.0, 
                 split_pattern: str = r"\n+") -> Iterator[AudioResult]:
        """Make the engine callable like Kokoro KPipeline."""
        return self.generate(text, voice, speed, split_pattern)
