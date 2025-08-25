"""TTS Engine factory for Abogen."""

from typing import Union
from .base import TTSEngine
from .kokoro import KokoroEngine
from .chatterbox import ChatterboxEngine


def create_tts_engine(engine_type: str, **kwargs) -> TTSEngine:
    """Create a TTS engine instance.
    
    Args:
        engine_type: Either "kokoro" or "chatterbox"
        **kwargs: Engine-specific configuration
        
    Returns:
        TTSEngine instance
    """
    if engine_type == "kokoro":
        return KokoroEngine(
            kpipeline_class=kwargs["kpipeline_class"],
            lang_code=kwargs["lang_code"],
            device=kwargs.get("device", "cuda")
        )
    elif engine_type == "chatterbox":
        return ChatterboxEngine(
            server_url=kwargs["server_url"],
            timeout=kwargs.get("timeout", 30.0)
        )
    else:
        raise ValueError(f"Unknown TTS engine type: {engine_type}")


def get_engine_from_config(config, **kokoro_kwargs) -> TTSEngine:
    """Create TTS engine based on configuration.
    
    Args:
        config: Configuration object with TTS engine settings
        **kokoro_kwargs: Additional Kokoro-specific parameters
        
    Returns:
        TTSEngine instance
    """
    engine_type = getattr(config, "tts_engine", "kokoro")
    
    if engine_type == "chatterbox":
        server_url = getattr(config, "chatterbox_server_url", "http://localhost:8004")
        timeout = getattr(config, "chatterbox_timeout", 30.0)
        
        return ChatterboxEngine(
            server_url=server_url,
            timeout=timeout
        )
    else:
        # Default to Kokoro for backward compatibility
        return KokoroEngine(**kokoro_kwargs)
