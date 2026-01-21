# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-21

### Added
- Initial release
- Configuration management via YAML file
- Recursive image scanning with support for JPG, PNG, BMP, TIFF formats
- Smart image resizing with aspect ratio preservation
- Format-specific compression:
  - JPEG: configurable quality with optimization
  - PNG: maximum compression with interlacing
- File metadata preservation (permissions, owner, group)
- Test mode for dry-run analysis
- Comprehensive statistics reporting
- CLI interface with argument parsing
- Launcher script with automatic venv setup
- Full test suite (66 tests)
- Complete documentation

### Features
- BData-based architecture using jsktoolbox patterns
- Support for symlinked installation
- Cross-device file operations support
- Detailed error handling and reporting

### Documentation
- README.md with installation and usage instructions
- CONTRIBUTING.md with development guidelines
- Comprehensive docstrings for all modules/classes/functions
- Type hints for all public APIs

[0.1.0]: https://github.com/Szumak75/qnap-img-shrink/releases/tag/v0.1.0
