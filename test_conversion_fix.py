#!/usr/bin/env python3
"""
Test conversion with Chatterbox engine to verify the fix
"""

import sys
import os
sys.path.insert(0, '.')

from abogen.utils import load_config, save_config
from abogen.conversion import ConversionThread
from PyQt5.QtCore import QCoreApplication
import tempfile
import time

def test_chatterbox_conversion():
    print("=== Testing Chatterbox TTS Conversion ===")
    
    # Set up test configuration
    config = load_config()
    config["tts_engine"] = "chatterbox"
    config["chatterbox_server_url"] = "http://localhost:8004"
    save_config(config)
    
    # Create a temporary text file
    test_text = "Hello, this is a test of the Chatterbox TTS integration."
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_text)
        test_file = f.name
    
    try:
        print(f"Created test file: {test_file}")
        print(f"Test text: {test_text}")
        
        # Create Qt application
        app = QCoreApplication([])
        
        # Set up conversion parameters
        lang_code = "e"  # English
        speed = 1.0
        voice = "predefined:Abigail.wav"  # Use a Chatterbox voice
        save_option = "desktop"
        output_folder = None
        subtitle_mode = "Disabled"
        output_format = "mp3"
        
        print(f"Using voice: {voice}")
        print("Starting conversion with Chatterbox engine...")
        
        # Create conversion thread
        # Note: np_module and kpipeline_class should be None for Chatterbox
        conversion_thread = ConversionThread(
            file_name=test_file,
            lang_code=lang_code,
            speed=speed,
            voice=voice,
            save_option=save_option,
            output_folder=output_folder,
            subtitle_mode=subtitle_mode,
            output_format=output_format,
            np_module=None,  # Not needed for Chatterbox
            kpipeline_class=None,  # Not needed for Chatterbox
            use_gpu=False,  # Not relevant for Chatterbox
            total_char_count=len(test_text),  # Add character count
        )
        
        # Set up signal handlers
        conversion_finished = False
        conversion_error = None
        
        def on_conversion_finished(result, output_path):
            nonlocal conversion_finished
            conversion_finished = True
            print(f"✅ Conversion finished! Output: {output_path}")
        
        def on_log_updated(message):
            if isinstance(message, tuple):
                text, is_success = message
                status = "✅" if is_success else "❌"
                print(f"LOG {status}: {text}")
            else:
                print(f"LOG: {message}")
        
        conversion_thread.conversion_finished.connect(on_conversion_finished)
        conversion_thread.log_updated.connect(on_log_updated)
        
        # Set additional attributes that the GUI normally sets
        conversion_thread.display_path = test_file
        conversion_thread.file_size_str = "56 bytes"
        conversion_thread.max_subtitle_words = 50
        conversion_thread.replace_single_newlines = False
        conversion_thread.separate_chapters_format = False
        conversion_thread.subtitle_format = "ass_centered_narrow"
        
        # Start conversion
        conversion_thread.start()
        
        # Wait for completion (with timeout)
        start_time = time.time()
        timeout = 30  # 30 seconds
        
        while not conversion_finished and (time.time() - start_time) < timeout:
            app.processEvents()
            time.sleep(0.1)
        
        if conversion_finished:
            print("🎉 Test completed successfully!")
            return True
        else:
            print("❌ Test timed out or failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        try:
            os.unlink(test_file)
        except:
            pass

if __name__ == "__main__":
    success = test_chatterbox_conversion()
    sys.exit(0 if success else 1)
