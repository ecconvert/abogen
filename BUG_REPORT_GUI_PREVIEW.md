# Bug Report: GUI Voice Preview Method Broken

## Status: CRITICAL - GUI crashes on voice preview

**Date:** August 25, 2025  
**Reporter:** Development Session  
**Priority:** High  
**Component:** abogen/gui.py - preview_voice method  

## Problem Summary

The `preview_voice` method in `abogen/gui.py` is severely broken due to malformed code edits during the modular TTS integration. The method has:

1. **Broken indentation** - Code blocks are incorrectly nested
2. **Orphaned code** - Unreachable code fragments after return statements  
3. **Mixed logic** - Old Kokoro TTS logic mixed with new modular TTS approach
4. **Threading issues** - NSWindow/main thread crashes on macOS

## Current Symptoms

- **GUI Crash**: `python -m abogen.main` crashes with NSWindow error when preview button is clicked
- **Wrong Voices**: GUI shows Kokoro voices even when Chatterbox TTS is detected
- **Threading Error**: Main thread violation on macOS when attempting preview
- **Code Structure**: Method is ~240 lines long with unreachable code after line 2410

## Working Components

✅ **Engine Detection**: TTS engine detection works (Chatterbox detected correctly)  
✅ **Voice List**: Voice fetching from Chatterbox API works (30 voices returned)  
✅ **GUI Layout**: Main GUI loads and displays correctly  
✅ **Voice Dropdown**: Populates with correct Chatterbox voices  

## Files Affected

- `abogen/gui.py` - Lines 2381-2617 (preview_voice method)
- Backup available: `abogen/gui.py.backup` (if created)

## Test Evidence

```bash
# This works - confirms Chatterbox integration
python test_gui_integration.py
# Output: "Chatterbox detected, 30 voices loaded"

# This crashes - GUI preview broken
python -m abogen.main
# Click preview button -> NSWindow crash
```

## Root Cause

During the modular TTS integration, the `preview_voice` method was partially updated to show an informative message dialog, but the old Kokoro TTS preview logic was left in place after the dialog code, creating:

1. Unreachable code after `msg.exec_()`
2. Broken indentation mixing message box code with old preview logic
3. Threading conflicts between PyQt5 message boxes and Kokoro audio processing

## Technical Details

- **Line 2381**: Method starts correctly
- **Lines 2381-2410**: Clean message box implementation (GOOD)
- **Lines 2411+**: Broken indentation with old Kokoro logic (BAD)
- **Expected End**: Should end around line 2410 after `msg.exec_()`
- **Actual End**: Method bleeds to line 2617 with broken code

## Recommended Fix

**SIMPLE APPROACH** (Recommended):
1. **Replace entire method** with clean, simple implementation
2. **Keep only** the informative message box (lines 2381-2410)
3. **Remove all** old Kokoro preview logic (lines 2411-2617)
4. **Add TODO** for future modular preview implementation

**COMPLEX APPROACH** (Future):
- Implement full modular preview system using TTS engine factory
- Add proper threading for preview audio
- Support both Kokoro and Chatterbox preview

## Next Session Pickup

The method should be replaced with this clean implementation:

```python
def preview_voice(self):
    """Simplified preview for modular TTS system."""
    # Get current engine and voice selection
    engine_id = self.engine_combo.currentData()
    if not engine_id:
        self._show_error_message_box("Preview Error", "No TTS engine selected.")
        return

    voice_data = self.voice_combo.currentData()
    if not voice_data:
        self._show_error_message_box("Preview Error", "No voice selected.")
        return

    # Show informative message
    from PyQt5.QtWidgets import QMessageBox
    
    msg = QMessageBox(self)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Voice Preview")
    msg.setText(f"Voice preview temporarily disabled during modular TTS integration.\n\n"
               f"Selected Engine: {self.engine_combo.currentText()}\n"
               f"Selected Voice: {voice_data}\n\n"
               f"Voice synthesis will work during actual conversion.\n"
               f"Click 'Start' to test with actual text processing.")
    msg.addButton(QMessageBox.Ok)
    msg.exec_()
```

## Environment Context

- **OS**: macOS (threading sensitive)
- **Python**: Virtual environment with PyQt5
- **TTS Server**: Chatterbox running on localhost:8000
- **Working Directory**: `/Users/jose/Projects/abogen`

## Test Commands for Next Session

```bash
# Verify Chatterbox still running
cd /Users/jose/Projects/Chatterbox-TTS-Server && ./status.sh

# Test integration (should work)
cd /Users/jose/Projects/abogen && python test_gui_integration.py

# Test GUI after fix (should not crash)
python -m abogen.main
```
