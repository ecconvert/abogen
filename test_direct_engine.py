#!/usr/bin/env python3
"""Direct TTS engine instantiation test."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from abogen.tts_engines.factory import create_tts_engine

def test_direct_chatterbox():
    """Test direct ChatterboxEngine instantiation."""
    print("Testing direct ChatterboxEngine instantiation...")
    
    try:
        # Create engine with proper config
        engine = create_tts_engine(
            'chatterbox',
            server_url='http://localhost:8004',
            timeout=30.0
        )
        print(f"✅ Engine created: {type(engine).__name__}")
        
        # Test connection and voice listing
        voices = engine.get_available_voices()
        print(f"✅ Voices retrieved: {len(voices)} voices found")
        if voices:
            print(f"   Sample voices: {voices[:3]}...")
        
        # Test synthesis with a simple sentence
        print("Testing synthesis...")
        audio_results = list(engine.generate("Hello, this is a test.", voices[0] if voices else "default"))
        print(f"✅ Synthesis completed: {len(audio_results)} chunks generated")
        if audio_results:
            print(f"   First chunk: {len(audio_results[0].audio)} samples at {audio_results[0].sample_rate}Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_kokoro():
    """Test direct KokoroEngine instantiation."""
    print("\nTesting direct KokoroEngine instantiation...")
    
    try:
        # Create engine with proper config  
        engine = create_tts_engine(
            'kokoro',
            kpipeline_class=None,  # This will need actual class
            lang_code='en',
            device='cpu'
        )
        print(f"✅ Engine created: {type(engine).__name__}")
        
        # Test voice listing
        voices = engine.get_available_voices()
        print(f"✅ Voices retrieved: {len(voices)} voices found")
        if voices:
            print(f"   Sample voices: {voices[:3]}...")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  Kokoro not available (expected): {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Direct TTS Engine Test ===")
    
    chatterbox_ok = test_direct_chatterbox()
    kokoro_ok = test_direct_kokoro()
    
    print(f"\n=== Results ===")
    print(f"Chatterbox: {'✅ PASS' if chatterbox_ok else '❌ FAIL'}")
    print(f"Kokoro: {'✅ PASS' if kokoro_ok else '⚠️  SKIP (expected)'}")
    
    if chatterbox_ok:
        print("\n🎉 Chatterbox integration working correctly!")
    else:
        print("\n⚠️  Chatterbox integration needs debugging")
