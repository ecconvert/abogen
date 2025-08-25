# Next Session Pickup Prompt

## Quick Context
You're working on Abogen, a Python TTS audiobook generator that was being modularized to support both Kokoro TTS and Chatterbox TTS Server. The modular TTS system is mostly complete, but the GUI voice preview is broken.

## Immediate Task
**Fix the broken `preview_voice` method in `abogen/gui.py`**

The method is located at lines 2381-2617 and is severely malformed with broken indentation, unreachable code, and threading issues. It crashes the GUI when users try to preview voices.

## What Works
- ✅ TTS engine detection (Chatterbox detected correctly)
- ✅ Voice list fetching (30 Chatterbox voices loaded)
- ✅ Main GUI loads and displays
- ✅ Voice dropdown populates correctly

## What's Broken
- ❌ Voice preview crashes with NSWindow/threading error
- ❌ Method has 240+ lines of malformed code after line 2410
- ❌ Old Kokoro logic mixed with new modular approach

## Quick Fix Needed
Replace the entire `preview_voice` method (lines 2381-2617) in `abogen/gui.py` with the clean implementation from `BUG_REPORT_GUI_PREVIEW.md`.

## Test Commands
```bash
# Verify Chatterbox running
cd /Users/jose/Projects/Chatterbox-TTS-Server && ./status.sh

# Test integration works
cd /Users/jose/Projects/abogen && python test_gui_integration.py

# Test GUI doesn't crash after fix
python -m abogen.main
```

## Files to Check
- `abogen/gui.py` - Main file to fix
- `BUG_REPORT_GUI_PREVIEW.md` - Detailed bug report
- `test_gui_integration.py` - Working integration test

## Expected Outcome
After the fix, clicking the preview button should show an informative dialog instead of crashing, and users can proceed with actual TTS conversion using the Start button.

## Current Status
All modular TTS infrastructure is complete and working. This is just a GUI cleanup task to remove broken code and replace it with a simple, safe implementation.
