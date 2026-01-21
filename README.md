# QNAP Image Shrink

A Python application for batch resizing and compressing images with metadata preservation.

## Features

- **Recursive directory scanning** - finds all images in specified directory
- **Smart resizing** - proportionally resize images exceeding max dimension
- **Format-specific compression**:
  - JPEG: configurable quality with optimization
  - PNG: maximum compression with interlacing
  - Support for BMP, TIFF formats
- **Metadata preservation** - maintains file permissions, owner, and group
- **Test mode** - analyze without modifying files
- **Comprehensive statistics** - detailed conversion reports

## Requirements

- Python 3.11 or 3.12
- Dependencies listed in `requirements.txt`

## Installation

```bash
# Clone repository
git clone <repository-url>
cd qnap-img-shrink

# Option 1: Using launcher script (recommended)
# Script will automatically create venv and install dependencies
./bin/qimgshrink --help

# Option 2: Manual setup with Poetry
poetry install
poetry run python -m qimgshrink.main --help

# Option 3: Manual setup with pip
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m qimgshrink.main --help
```

## Usage

### Using launcher script (recommended)

```bash
# Normal mode - process images
./bin/qimgshrink

# Test mode - analyze without modifications
./bin/qimgshrink -t

# Help
./bin/qimgshrink --help
```

### System-wide Installation

To make the script available system-wide, create a symlink:

```bash
# Option 1: For all users (requires root)
sudo ln -s /path/to/qnap-img-shrink/bin/qimgshrink /usr/local/bin/qimgshrink

# Option 2: For current user only
mkdir -p ~/.local/bin
ln -s /path/to/qnap-img-shrink/bin/qimgshrink ~/.local/bin/qimgshrink
# Make sure ~/.local/bin is in your PATH

# Then use from anywhere:
qimgshrink --help
qimgshrink -t
```

**Note:** The launcher script properly resolves symlinks, so it will always find the correct project directory and virtual environment, regardless of where the symlink is located.

### Direct execution

```bash
# With Poetry
poetry run python -m qimgshrink.main
poetry run python -m qimgshrink.main -t

# With activated venv
source .venv/bin/activate
python -m qimgshrink.main
python -m qimgshrink.main -t
```

## Configuration

Edit `etc/config.yaml`:

```yaml
wrk_dir: "/path/to/images/"
max_size: 1920
quality: 85
```

- `wrk_dir`: Directory to scan for images (absolute path)
- `max_size`: Maximum dimension for longest side in pixels
- `quality`: JPEG quality (1-100), 85 is recommended

## Testing

```bash
# Run all tests
poetry run pytest tests/

# Run with coverage
poetry run pytest tests/ --cov=qimgshrink

# Run specific test file
poetry run pytest tests/test_converter.py -v
```

## Development

```bash
# Install dev dependencies
poetry install --with dev

# Format code
poetry run black .

# Run linter
poetry run pycodestyle qimgshrink/

# Type checking
poetry run mypy qimgshrink/
```

## Project Structure

```
qnap-img-shrink/
├── bin/
│   └── qimgshrink          # Launcher script
├── etc/
│   └── config.yaml         # Configuration file
├── qimgshrink/
│   ├── __init__.py
│   ├── main.py             # Main application & Config
│   ├── files.py            # FileFind & ImageFileInfo
│   └── converter.py        # Converter & ConversionStats
├── tests/
│   ├── test_app.py
│   ├── test_config.py
│   ├── test_converter.py
│   └── test_file_find.py
├── pyproject.toml          # Poetry configuration
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

## Architecture

The application follows the jsktoolbox patterns:

- **BData**: Base class for data containers
- **ReadOnlyClass**: Metaclass for constant key classes
- **Raise.error()**: Structured error handling

Key classes:

- `Config`: Application configuration with YAML loading
- `FileFind`: Recursive image file discovery
- `ImageFileInfo`: Container for file metadata (BData)
- `Converter`: Image processing engine
- `ConversionStats`: Statistics tracking (BData)
- `App`: Main application orchestrator

## License

See LICENSE file for details.

## Author

Jacek 'Szumak' Kotlarski - szumak@virthost.pl
