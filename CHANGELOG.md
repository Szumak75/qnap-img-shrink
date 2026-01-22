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

## [Unreleased]

### Added
- **Converter2**: ImageMagick-based converter implementation
  - Alternative to Pillow for platforms without compilation support
  - Uses external `convert` and `identify` commands
  - Fully API-compatible with original Converter class
  - Format-specific compression for JPEG and PNG
  - Metadata preservation (permissions, uid, gid)
  - Test mode support
- **converter_factory**: Factory function for automatic converter selection
  - `create_converter()` with preference option
  - Automatic fallback between implementations
- **Graceful interruption handling**: Ctrl+C (SIGINT) support
  - Completes current file conversion before exit
  - Displays statistics for completed operations
  - Clean shutdown with exit code 130
  - Signal handler registration in App class
- Documentation: docs/CONVERTER2.md, docs/QNAP_DEPLOYMENT.md
- Tests: 14 additional tests (Converter2 + factory + signal handling)

### Changed
- **BREAKING**: ImageFileInfo now stores uid/gid (int) instead of owner/group (str)
  - Eliminates double translation (uid→name→uid)
  - More reliable on systems with non-standard user/group mappings
  - Fixes potential KeyError issues on QNAP and similar platforms
  - Direct use of numeric IDs for os.chown() operations
- Metadata preservation: Updated to use numeric uid/gid directly
- Launcher script: Early sourcing of QNAP Python3 profile
  - Global environment variable setup
  - Explicit re-export of PATH, PYTHONPATH, LD_LIBRARY_PATH
  - Information message when profile loaded
- Total test count: 80 tests (all passing)
- Documentation updated to reflect uid/gid and signal handling changes

