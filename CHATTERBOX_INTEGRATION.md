# Chatterbox TTS Integration for Abogen

This implementation adds support for the [Chatterbox TTS Server](https://github.com/devnen/Chatterbox-TTS-Server) as an alternative to the built-in Kokoro engine in Abogen.

## Features

- **Dual Engine Support**: Switch between Kokoro (local) and Chatterbox (server-based) TTS engines
- **Easy Configuration**: Settings menu integration for engine selection and server configuration
- **Voice Management**: Automatic detection of predefined and reference voices from Chatterbox server
- **Backward Compatibility**: Existing Kokoro functionality remains unchanged
- **Chunked Processing**: Large text handling with intelligent splitting for audiobook generation

## Setup Instructions

### 1. Install Chatterbox TTS Server

Follow the setup instructions from the [Chatterbox repository](https://github.com/devnen/Chatterbox-TTS-Server):

```bash
# Clone the repository
git clone https://github.com/devnen/Chatterbox-TTS-Server.git
cd Chatterbox-TTS-Server

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

The server will start on `http://localhost:8004` by default.

### 2. Install requests dependency

Abogen needs the `requests` library for Chatterbox integration:

```bash
pip install requests
```

### 3. Configure Abogen

1. Start Abogen
2. Click the Settings button (⚙️)
3. Select "TTS Engine" > "Chatterbox Server"
4. Configure the server URL if different from default
5. Test the connection

## Usage

### Engine Selection

In Abogen's settings menu:
- **Kokoro (Local)**: Uses the original local TTS engine
- **Chatterbox Server**: Uses the remote Chatterbox server

### Voice Formats

Chatterbox voices are automatically detected and formatted as:
- `predefined:voice_name.wav` - Curated voices from the server
- `reference:audio_file.wav` - Reference files for voice cloning

### Configuration Options

The following settings are added to Abogen's configuration:

```json
{
  "tts_engine": "chatterbox",
  "chatterbox_server_url": "http://localhost:8004",
  "chatterbox_timeout": 30.0
}
```

## Architecture

### TTS Engine Abstraction

The implementation uses an abstraction layer that allows easy switching between engines:

```
abogen/tts_engines/
├── __init__.py
├── base.py          # Abstract TTS engine interface
├── chatterbox.py    # Chatterbox implementation
├── kokoro.py        # Kokoro wrapper
└── factory.py       # Engine factory
```

### Key Components

1. **TTSEngine Base Class**: Common interface for all TTS engines
2. **ChatterboxEngine**: HTTP client for Chatterbox server API
3. **KokoroEngine**: Wrapper for existing Kokoro functionality
4. **Engine Factory**: Creates appropriate engine based on configuration

### Audio Processing Flow

```
Text Input → Engine Selection → Voice Processing → Audio Generation → Subtitle Timing → Output Files
```

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Ensure Chatterbox server is running
   - Check server URL in settings
   - Verify network connectivity

2. **Voice Not Found**
   - Refresh voices in Chatterbox web UI
   - Check predefined voices directory
   - Verify voice file formats (.wav, .mp3)

3. **Audio Quality Issues**
   - Adjust Chatterbox generation parameters
   - Use higher quality reference audio for cloning
   - Check chunk size settings for long texts

### Testing

Run the test script to verify integration:

```bash
python test_chatterbox_integration.py
```

### Logs

Check Abogen's log window and Chatterbox server logs for detailed error information.

## Comparison: Kokoro vs Chatterbox

| Feature | Kokoro | Chatterbox |
|---------|--------|------------|
| Processing | Local GPU/CPU | Remote server |
| Voice Mixing | ✅ Formulas | ❌ Not supported |
| Voice Cloning | ✅ Limited | ✅ Advanced |
| Large Text | ✅ Native | ✅ Chunked |
| Network Required | ❌ Offline | ✅ Server connection |
| Setup Complexity | Low | Medium |
| Performance | Fast (local) | Depends on server |

## Future Enhancements

- [ ] Voice mixing support for Chatterbox
- [ ] Batch processing optimization
- [ ] Advanced timing alignment
- [ ] Multiple server support
- [ ] Automatic fallback between engines
- [ ] Performance monitoring

## Contributing

When contributing to this integration:

1. Maintain backward compatibility with Kokoro
2. Follow the existing code style
3. Update tests for new features
4. Document configuration changes
5. Test with both engines

## License

This integration follows the same license as Abogen (MIT). The Chatterbox TTS Server has its own licensing terms.
