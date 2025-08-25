"""Kokoro TTS Engine implementation (legacy compatibility)."""

import re
from typing import List, Iterator
from .base import TTSEngine, AudioResult, AudioToken


class KokoroEngine(TTSEngine):
    """Kokoro TTS Engine wrapper for legacy compatibility."""
    
    def __init__(self, kpipeline_class, lang_code: str, device: str = "cuda"):
        self.kpipeline_class = kpipeline_class
        self.lang_code = lang_code
        self.device = device
        self._pipeline = None
        self._init_pipeline()
    
    def _init_pipeline(self):
        """Initialize the Kokoro pipeline."""
        self._pipeline = self.kpipeline_class(
            lang_code=self.lang_code,
            repo_id="hexgrad/Kokoro-82M",
            device=self.device
        )
    
    def get_available_voices(self) -> List[str]:
        """Get list of available Kokoro voices."""
        # Kokoro voices are determined by the voice parameter passed to generate
        # This is a simplified list - in practice, Kokoro supports many voices
        return [
            "af", "af_bella", "af_nicole", "af_sarah", "af_sky",
            "am_adam", "am_michael", "bf_emma", "bf_isabella", "bm_george", "bm_lewis"
        ]
    
    def generate(self, text: str, voice: str, speed: float = 1.0, 
                split_pattern: str = r"\n+") -> Iterator[AudioResult]:
        """Generate audio using Kokoro pipeline."""
        # Handle voice formulas if needed
        from abogen.voice_formulas import get_new_voice
        from abogen.is_nvidia import is_nvidia_gpu_available
        
        loaded_voice = voice
        if "*" in voice:
            use_gpu = self.device != "cpu"
            loaded_voice = get_new_voice(self._pipeline, voice, use_gpu)
        
        # Use Kokoro's native generation
        for result in self._pipeline(
            text,
            voice=loaded_voice,
            speed=speed,
            split_pattern=split_pattern
        ):
            # Convert Kokoro result to our standard format
            tokens = []
            if hasattr(result, 'tokens'):
                for tok in result.tokens:
                    tokens.append(AudioToken(
                        text=tok.text,
                        whitespace=getattr(tok, 'whitespace', ''),
                        start_ts=getattr(tok, 'start_ts', None),
                        end_ts=getattr(tok, 'end_ts', None)
                    ))
            
            yield AudioResult(
                audio=result.audio,
                graphemes=result.graphemes,
                tokens=tokens
            )
    
    def supports_voice_mixing(self) -> bool:
        """Kokoro supports voice mixing through formulas."""
        return True
    
    def get_device(self) -> str:
        """Get the device being used."""
        return self.device
