#!/usr/bin/env python3
"""
Test TTS conversion with the Gettysburg Address
This will test the modular TTS system with a real text file.
"""
import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from abogen.conversion import ConversionThread
from abogen.tts_engines.factory import create_tts_engine

def test_gettysburg_tts():
    """Test TTS conversion with the Gettysburg Address"""
    print("🎯 Testing TTS with Gettysburg Address")
    print("=" * 50)
    
    # Read the Gettysburg Address (short version for testing)
    input_file = "/Users/jose/Projects/abogen/test_gettysburg_short.txt"
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    print(f"📖 Text length: {len(text_content)} characters")
    print(f"📝 First 100 chars: {text_content[:100]}...")
    
    # Create output file path
    output_file = "/Users/jose/Projects/abogen/gettysburg_short_audio.mp3"
    
    # Test configuration for Chatterbox
    config = {
        "tts_engine": "chatterbox",
        "chatterbox_voice": "predefined:Alexander.wav",  # Male voice for Lincoln
        "server_url": "http://localhost:8004",  # Chatterbox server URL
        "output_format": "mp3",
        "sample_rate": 24000,
        "timeout": 60.0,  # Increase timeout to 60 seconds
    }
    
    print(f"🔧 Configuration:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    try:
        # Test engine creation
        print("\n🚀 Testing TTS Engine Creation...")
        engine = create_tts_engine("chatterbox", **config)
        print(f"✅ Engine created: {type(engine).__name__}")
        
        # Test a small synthesis first
        print("\n🎵 Testing small synthesis...")
        test_text = "Four score and seven years ago"
        audio_results = list(engine.generate(test_text, "predefined:Alexander.wav"))
        if audio_results:
            first_result = audio_results[0]
            print(f"✅ Test synthesis successful: {len(first_result.audio)} samples at {first_result.sample_rate}Hz")
        else:
            print("❌ No audio results generated")
            return False
        
        # Now test the full conversion
        print("\n📻 Starting full Gettysburg Address conversion...")
        print("This may take a minute or two...")
        
        # Create conversion thread
        conversion = ConversionThread(
            file_name=input_file,  # Use the text file path
            lang_code="en",  # English language code
            speed=1.0,
            voice="predefined:Alexander.wav",
            save_option="Save to file",
            output_folder=os.path.dirname(output_file),
            subtitle_mode="Disabled",
            output_format="mp3",
            np_module=None,  # Not needed for Chatterbox
            kpipeline_class=None,  # Not needed for Chatterbox
            start_time=None,
            total_char_count=len(text_content),
            use_gpu=False,  # Not relevant for Chatterbox
            from_queue=False
        )
        
        # Set additional attributes that GUI normally sets
        conversion.display_path = input_file
        conversion.file_size_str = f"{len(text_content)} characters"
        conversion.replace_single_newlines = True
        conversion.replace_double_newlines = True
        conversion.replace_triple_newlines = True
        
        # Add progress callback
        def progress_callback(current, message=""):
            print(f"📈 Progress: {current} chars processed - {message}")
        
        def log_callback(message):
            print(f"📝 Log: {message}")
            
        def error_callback(message):
            print(f"❌ Error: {message}")
        
        def finished_callback(result, output_path):
            print(f"🎉 Conversion finished! Output: {output_path}")
        
        conversion.progress_updated.connect(progress_callback)
        conversion.log_updated.connect(log_callback)
        conversion.conversion_finished.connect(finished_callback)
        
        # Run conversion
        conversion.run()
        
        # Check results
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"🎉 SUCCESS! Audio file created: {output_file}")
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"🎵 You can now play the audio file to hear Lincoln's Gettysburg Address!")
            return True
        else:
            print(f"❌ FAILED! Audio file not created: {output_file}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED! Exception during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gettysburg_tts()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Gettysburg Address TTS Test: PASSED")
        print("🔊 Check the generated audio file: gettysburg_audio.mp3")
    else:
        print("❌ Gettysburg Address TTS Test: FAILED")
    sys.exit(0 if success else 1)
