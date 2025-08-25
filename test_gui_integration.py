#!/usr/bin/env python3
"""Test the modular TTS engine integration in GUI."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_gui_engine_detection():
    """Test if the GUI can detect and switch TTS engines."""
    print("Testing GUI engine detection...")
    
    # Test engine detection without GUI (safer)
    available_engines = []
    
    # Check Chatterbox
    try:
        import requests
        response = requests.get("http://localhost:8004/api/ui/initial-data", timeout=5)
        if response.status_code == 200:
            available_engines.append(("chatterbox", "Chatterbox TTS Server"))
            print("✅ Chatterbox TTS Server detected")
    except Exception as e:
        print(f"❌ Chatterbox not available: {e}")
    
    # Check Kokoro
    try:
        import kokoro
        available_engines.append(("kokoro", "Kokoro TTS"))
        print("✅ Kokoro TTS detected")
    except ImportError:
        print("❌ Kokoro not available (expected)")
    
    print(f"\nAvailable engines: {len(available_engines)}")
    for engine_id, engine_name in available_engines:
        print(f"  - {engine_name} ({engine_id})")
    
    return len(available_engines) > 0

def test_chatterbox_voice_loading():
    """Test loading voices from Chatterbox."""
    print("\nTesting Chatterbox voice loading...")
    
    try:
        from abogen.tts_engines.factory import create_tts_engine
        
        engine = create_tts_engine(
            'chatterbox',
            server_url='http://localhost:8004',
            timeout=30.0
        )
        
        voices = engine.get_available_voices()
        print(f"✅ Loaded {len(voices)} voices from Chatterbox")
        
        # Show sample voices
        if voices:
            print("Sample voices:")
            for voice in voices[:5]:
                print(f"  - {voice}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading Chatterbox voices: {e}")
        return False

if __name__ == "__main__":
    print("=== GUI Integration Test ===")
    
    engines_ok = test_gui_engine_detection()
    voices_ok = test_chatterbox_voice_loading()
    
    print(f"\n=== Results ===")
    print(f"Engine Detection: {'✅ PASS' if engines_ok else '❌ FAIL'}")
    print(f"Voice Loading: {'✅ PASS' if voices_ok else '❌ FAIL'}")
    
    if engines_ok and voices_ok:
        print("\n🎉 GUI integration components working!")
        print("The GUI should now work with engine selection and Chatterbox voices.")
    else:
        print("\n⚠️  Some components need debugging.")
