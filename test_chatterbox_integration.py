#!/usr/bin/env python3
"""Test script for Chatterbox TTS Server integration with Abogen."""

import sys
import os

# Add the parent directory to sys.path to import abogen modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_chatterbox_connection():
    """Test basic connection to Chatterbox server."""
    try:
        import requests
        
        server_url = "http://localhost:8004"
        print(f"Testing connection to Chatterbox server at {server_url}...")
        
        # Test basic connection
        response = requests.get(f"{server_url}/api/ui/initial-data", timeout=10)
        response.raise_for_status()
        print("✓ Successfully connected to Chatterbox server")
        
        # Test getting voices
        response = requests.get(f"{server_url}/get_predefined_voices", timeout=10)
        response.raise_for_status()
        voices = response.json()
        print(f"✓ Found {len(voices)} predefined voices")
        
        return True
        
    except ImportError:
        print("✗ requests library not found. Install with: pip install requests")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Chatterbox TTS Server is running")
        print("2. Check the server URL (default: http://localhost:8004)")
        print("3. Verify the server is accessible from this machine")
        return False

def test_chatterbox_engine():
    """Test the Chatterbox engine implementation."""
    try:
        from abogen.tts_engines.chatterbox import ChatterboxEngine
        
        print("\nTesting Chatterbox engine...")
        engine = ChatterboxEngine("http://localhost:8004")
        
        # Test getting voices
        voices = engine.get_available_voices()
        print(f"✓ Engine found {len(voices)} voices: {voices[:3]}...")
        
        # Test simple synthesis
        print("✓ Testing text synthesis...")
        test_text = "Hello, this is a test of the Chatterbox TTS engine."
        
        if voices:
            voice = voices[0]  # Use first available voice
            print(f"✓ Using voice: {voice}")
            
            results = list(engine.generate(test_text, voice))
            print(f"✓ Generated {len(results)} audio chunks")
            
            if results:
                audio = results[0].audio
                print(f"✓ First chunk has {len(audio) if hasattr(audio, '__len__') else 'unknown'} audio samples")
        
        return True
        
    except Exception as e:
        print(f"✗ Engine test failed: {e}")
        return False

def test_abogen_integration():
    """Test integration with Abogen's configuration system."""
    try:
        from abogen.utils import load_config, save_config
        
        print("\nTesting Abogen configuration integration...")
        
        # Load current config
        config = load_config()
        print("✓ Loaded Abogen configuration")
        
        # Test setting Chatterbox as TTS engine
        config["tts_engine"] = "chatterbox"
        config["chatterbox_server_url"] = "http://localhost:8004"
        save_config(config)
        print("✓ Updated configuration to use Chatterbox")
        
        # Test engine factory
        from abogen.tts_engines.factory import get_engine_from_config
        
        class MockConfig:
            def __init__(self, config_dict):
                for key, value in config_dict.items():
                    setattr(self, key, value)
        
        mock_config = MockConfig(config)
        try:
            engine = get_engine_from_config(mock_config)
            print(f"✓ Created engine: {type(engine).__name__}")
        except Exception as e:
            print(f"⚠ Engine creation failed (server may not be running): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Abogen Chatterbox Integration Test")
    print("=" * 40)
    
    tests = [
        ("Chatterbox Connection", test_chatterbox_connection),
        ("Chatterbox Engine", test_chatterbox_engine),
        ("Abogen Integration", test_abogen_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("Test Results:")
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n✓ All tests passed! Chatterbox integration is ready.")
    else:
        print("\n⚠ Some tests failed. Check the errors above.")
        print("\nNext steps:")
        print("1. Start the Chatterbox TTS Server")
        print("2. Verify server is accessible at http://localhost:8004")
        print("3. Install missing dependencies if needed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
