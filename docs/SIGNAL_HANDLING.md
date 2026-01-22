# Signal Handling - Graceful Interruption

## Overview

The application implements graceful interruption handling via SIGINT (Ctrl+C) signal. This allows users to safely stop processing while ensuring data integrity and proper statistics reporting.

## How It Works

### Signal Handler Registration

The `App` class registers a SIGINT handler during initialization:

```python
class App(BData):
    def __init__(self) -> None:
        # ... other initialization ...
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
```

### Interrupt Flow

1. **User presses Ctrl+C** during processing
2. **Signal handler is invoked**:
   ```python
   def _signal_handler(self, signum: int, frame) -> None:
       print("\n\n*** Interrupt received - finishing current file... ***")
       self._set_data(key=_Keys.INTERRUPTED, value=True)
   ```
3. **Interrupted flag is set** to `True`
4. **Current file conversion continues** to completion
5. **Main loop checks flag** after each file:
   ```python
   for img_info in images:
       if self.interrupted:
           print("\n*** Processing interrupted by user ***")
           break
       # ... process file ...
   ```
6. **Statistics are displayed** for all completed operations
7. **Application exits** with code 130 (standard SIGINT code)

## Behavior Guarantees

### ✅ What IS Guaranteed

- **Current file completion**: File being converted will finish processing
- **No partial conversions**: Temp files cleaned up if interrupted during conversion
- **Statistics accuracy**: Stats reflect all completed operations
- **Clean exit**: Application terminates properly with appropriate exit code
- **No data loss**: Original files remain intact (temp file mechanism)

### ❌ What IS NOT Guaranteed

- **Remaining files processed**: Files not yet started will be skipped
- **Re-running after interrupt**: State is not saved; restart processes from beginning

## Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | All files processed normally |
| 130 | SIGINT | User interrupted with Ctrl+C |
| 1 | Error | Other application errors |

## Example Session

```bash
$ ./bin/qimgshrink

[INFO] QNAP Image Shrink - Launcher
[INFO] Starting application...

Found 10 image(s) to process...
  ✓ Processed: /path/to/image1.jpg
  ✓ Processed: /path/to/image2.jpg
^C

*** Interrupt received - finishing current file... ***
  ✓ Processed: /path/to/image3.jpg    # Current file completes

*** Processing interrupted by user ***

============================================================
Conversion Statistics:
Total files: 3
Processed: 3
Skipped: 0
Size before: 15.2 MB
Size after: 8.7 MB
Saved: 6.5 MB
Compression ratio: 42.8%
============================================================

*** Application terminated by user ***
```

## Technical Implementation

### Interrupted Property

The `App` class provides an `interrupted` property:

```python
@property
def interrupted(self) -> bool:
    """Check if application was interrupted."""
    tmp: Optional[bool] = self._get_data(key=_Keys.INTERRUPTED)
    return tmp if tmp is not None else False
```

### Loop Integration

The main processing loop checks the flag after each file:

```python
for img_info in images:
    # Check BEFORE starting next file
    if self.interrupted:
        print("\n*** Processing interrupted by user ***")
        break
    
    # Process file...
```

### Exit Handling

After loop completion (normal or interrupted):

```python
# Always print statistics
converter.print_report()

# Exit with appropriate code if interrupted
if self.interrupted:
    print("\n*** Application terminated by user ***")
    sys.exit(130)
```

## Testing

The signal handling is tested in `tests/test_app.py`:

```python
def test_app_signal_handler_sets_interrupted(self):
    """Test signal handler sets interrupted flag."""
    app = App()
    assert app.interrupted is False
    
    # Simulate signal
    app._signal_handler(signal.SIGINT, None)
    
    assert app.interrupted is True
```

## Limitations

1. **Single interrupt**: Multiple Ctrl+C presses are handled by first signal only
2. **Thread safety**: Not designed for multi-threaded conversion (current architecture is single-threaded)
3. **Platform specific**: SIGINT behavior may vary on non-Unix systems

## Best Practices

### For Users

- **Press Ctrl+C once** and wait for current file to complete
- **Review statistics** before re-running to avoid duplicate processing
- **Use test mode** first to estimate processing time: `qimgshrink -t`

### For Developers

- **Never disable signal handler** without good reason
- **Always cleanup** temp files in exception handlers
- **Test interruption** at various stages (first file, middle, last file)
- **Document exit codes** in user-facing messages

## See Also

- [README.md](../README.md) - General usage
- [API.md](API.md) - App class documentation
- Python signal module: https://docs.python.org/3/library/signal.html
