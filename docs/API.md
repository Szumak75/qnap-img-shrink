# API Documentation

## Module: qimgshrink.main

### Class: Config

Configuration management class for qimgshrink application.

**Properties:**
- `wrk_dir: str` - Working directory for image scanning
- `max_size: int` - Maximum dimension for image longest side (pixels)
- `quality: int` - JPEG quality (1-100)
- `test_mode: bool` - Test mode flag (no file modifications)

**Methods:**
- `load_from_file(config_path: Optional[Path] = None) -> None` - Load configuration from YAML file

### Class: App

Main application orchestrator.

**Properties:**
- `config: Config` - Configuration instance

**Methods:**
- `run() -> None` - Execute main application logic

### Function: main

```python
def main() -> int
```

CLI entry point with argument parsing.

**Returns:** Exit code (0 for success)

---

## Module: qimgshrink.files

### Class: ImageFileInfo

Container for image file metadata.

**Constructor:**
```python
ImageFileInfo(
    path: str,
    permissions: int,
    owner: str,
    group: str,
    size: int
)
```

**Properties:**
- `path: str` - Absolute file path
- `permissions: int` - File permissions (octal)
- `permissions_str: str` - File permissions (string format)
- `owner: str` - File owner username
- `group: str` - File group name
- `size: int` - File size in bytes

### Class: FileFind

Recursive image file scanner.

**Constructor:**
```python
FileFind(wrk_dir: str)
```

**Properties:**
- `wrk_dir: str` - Working directory

**Methods:**
- `find_images() -> List[ImageFileInfo]` - Find all images recursively

**Supported formats:** JPG, JPEG, PNG, BMP, TIFF, TIF (case-insensitive)

---

## Module: qimgshrink.converter

### Class: ConversionStats

Statistics tracking for image conversions.

**Properties:**
- `processed_files: int` - Number of processed files
- `skipped_files: int` - Number of skipped files
- `size_before: int` - Total size before conversion (bytes)
- `size_after: int` - Total size after conversion (bytes)
- `total_files: int` - Total files processed
- `saved_bytes: int` - Total bytes saved
- `compression_ratio: float` - Compression percentage

**Methods:**
- `add_processed(size_before: int, size_after: int) -> None` - Add processed file stats
- `add_skipped() -> None` - Increment skipped counter

### Class: Converter

Image processing engine.

**Constructor:**
```python
Converter(
    max_size: int,
    quality: int,
    test_mode: bool = False
)
```

**Properties:**
- `max_size: int` - Maximum dimension
- `quality: int` - JPEG quality
- `stats: ConversionStats` - Conversion statistics
- `test_mode: bool` - Test mode flag

**Methods:**
- `convert(image_info: ImageFileInfo) -> bool` - Convert and compress image
  - Returns `True` if processed, `False` if skipped
  - Raises `PermissionError` if no access
  - Raises `OSError` if file operations fail

- `print_report() -> None` - Print statistics report

**Compression Strategy:**
- **JPEG**: Uses quality parameter, optimize=True
- **PNG**: compress_level=9, interlace=True, optimize=True
- **Other**: No specific compression
- **Resizing**: Proportional with LANCZOS resampling

---

## Usage Example

```python
from pathlib import Path
from qimgshrink.main import Config, App
from qimgshrink.files import FileFind
from qimgshrink.converter import Converter

# Configuration
config = Config()
config.wrk_dir = "/path/to/images"
config.max_size = 1920
config.quality = 85
config.test_mode = False

# Find images
finder = FileFind(config.wrk_dir)
images = finder.find_images()

# Process images
converter = Converter(
    max_size=config.max_size,
    quality=config.quality,
    test_mode=config.test_mode
)

for image_info in images:
    try:
        was_processed = converter.convert(image_info)
        if was_processed:
            print(f"Processed: {image_info.path}")
        else:
            print(f"Skipped: {image_info.path}")
    except Exception as e:
        print(f"Error: {image_info.path} - {e}")

# Print statistics
converter.print_report()
```

---

## Type Hints

All public APIs have complete type hints:

```python
from typing import List, Optional
from pathlib import Path

def find_images(self) -> List[ImageFileInfo]: ...
def load_from_file(self, config_path: Optional[Path] = None) -> None: ...
def convert(self, image_info: ImageFileInfo) -> bool: ...
```
