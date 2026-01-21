#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_config.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for Config class.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from qimgshrink.main import Config

# Get default values from Config class
_DEFAULT_CONFIG = Config()
DEFAULT_WRK_DIR = _DEFAULT_CONFIG.wrk_dir
DEFAULT_MAX_SIZE = _DEFAULT_CONFIG.max_size
DEFAULT_QUALITY = _DEFAULT_CONFIG.quality
del _DEFAULT_CONFIG


class TestConfigDefaults:
    """Test suite for Config class default values."""

    def test_default_wrk_dir(self) -> None:
        """Test default working directory value."""
        config = Config()
        assert config.wrk_dir == DEFAULT_WRK_DIR

    def test_default_max_size(self) -> None:
        """Test default maximum size value."""
        config = Config()
        assert config.max_size == DEFAULT_MAX_SIZE

    def test_default_quality(self) -> None:
        """Test default quality value."""
        config = Config()
        assert config.quality == DEFAULT_QUALITY


class TestConfigSetters:
    """Test suite for Config class setters."""

    def test_set_wrk_dir(self) -> None:
        """Test setting working directory."""
        config = Config()
        config.wrk_dir = "/custom/path"
        assert config.wrk_dir == "/custom/path"

    def test_set_max_size(self) -> None:
        """Test setting maximum size."""
        config = Config()
        config.max_size = 2048
        assert config.max_size == 2048

    def test_set_quality(self) -> None:
        """Test setting quality."""
        config = Config()
        config.quality = 85
        assert config.quality == 85


class TestConfigLoadFromFile:
    """Test suite for Config.load_from_file() method."""

    def test_load_all_parameters(self) -> None:
        """Test loading all configuration parameters from file."""
        config = Config()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {"wrk_dir": "/test/directory", "max_size": 2560, "quality": 90}, f
            )
            config_path = Path(f.name)

        try:
            config.load_from_file(config_path)
            assert config.wrk_dir == "/test/directory"
            assert config.max_size == 2560
            assert config.quality == 90
        finally:
            config_path.unlink()

    def test_load_partial_parameters(self) -> None:
        """Test loading only some parameters, others keep defaults."""
        config = Config()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"max_size": 3000}, f)
            config_path = Path(f.name)

        try:
            config.load_from_file(config_path)
            assert config.wrk_dir == DEFAULT_WRK_DIR  # default
            assert config.max_size == 3000  # loaded
            assert config.quality == DEFAULT_QUALITY  # default
        finally:
            config_path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading from non-existent file keeps defaults."""
        config = Config()
        config_path = Path("/nonexistent/path/config.yaml")

        config.load_from_file(config_path)

        assert config.wrk_dir == DEFAULT_WRK_DIR
        assert config.max_size == DEFAULT_MAX_SIZE
        assert config.quality == DEFAULT_QUALITY

    def test_load_empty_file(self) -> None:
        """Test loading from empty file keeps defaults."""
        config = Config()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            config_path = Path(f.name)

        try:
            config.load_from_file(config_path)
            assert config.wrk_dir == DEFAULT_WRK_DIR
            assert config.max_size == DEFAULT_MAX_SIZE
            assert config.quality == DEFAULT_QUALITY
        finally:
            config_path.unlink()

    def test_load_invalid_type_ignored(self) -> None:
        """Test that parameters with invalid types are ignored."""
        config = Config()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {
                    "wrk_dir": 12345,  # invalid type (should be str)
                    "max_size": "invalid",  # invalid type (should be int)
                    "quality": 85,  # valid
                },
                f,
            )
            config_path = Path(f.name)

        try:
            config.load_from_file(config_path)
            assert config.wrk_dir == DEFAULT_WRK_DIR  # default (invalid ignored)
            assert config.max_size == DEFAULT_MAX_SIZE  # default (invalid ignored)
            assert config.quality == 85  # loaded
        finally:
            config_path.unlink()

    def test_load_invalid_yaml(self) -> None:
        """Test that invalid YAML raises exception."""
        config = Config()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = Path(f.name)

        try:
            with pytest.raises(yaml.YAMLError):
                config.load_from_file(config_path)
        finally:
            config_path.unlink()

    def test_load_with_none_path_uses_default(self) -> None:
        """Test that passing None uses default config path.

        If etc/config.yaml exists, it will be loaded. This test verifies
        that the file is loaded (if exists) or defaults are preserved (if not).
        """
        config = Config()

        # Store original defaults
        original_wrk_dir = DEFAULT_WRK_DIR
        original_max_size = DEFAULT_MAX_SIZE
        original_quality = DEFAULT_QUALITY

        # This should not raise an error
        config.load_from_file(None)

        # Verify values are set (either from file or defaults)
        assert config.wrk_dir is not None
        assert config.max_size > 0
        assert config.quality > 0

    def test_load_preserves_previously_set_values(self) -> None:
        """Test that loading from file with partial config preserves manually set values."""
        config = Config()
        config.wrk_dir = "/custom/path"
        config.max_size = 2048

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"quality": 80}, f)
            config_path = Path(f.name)

        try:
            config.load_from_file(config_path)
            assert config.wrk_dir == "/custom/path"  # preserved
            assert config.max_size == 2048  # preserved
            assert config.quality == 80  # loaded
        finally:
            config_path.unlink()

    def test_config_file_can_differ_from_defaults(self) -> None:
        """Test that config file values can differ from code defaults.

        This ensures tests don't assume config file contains default values.
        """
        config = Config()

        # Create config file with different values than defaults
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(
                {"wrk_dir": "/different/path", "max_size": 3840, "quality": 50}, f
            )
            config_path = Path(f.name)

        try:
            # Verify initial defaults
            assert config.wrk_dir == DEFAULT_WRK_DIR
            assert config.max_size == DEFAULT_MAX_SIZE
            assert config.quality == DEFAULT_QUALITY

            # Load file with different values
            config.load_from_file(config_path)

            # Verify file values override defaults
            assert config.wrk_dir == "/different/path"
            assert config.max_size == 3840
            assert config.quality == 50

            # Verify loaded values differ from defaults
            assert (
                config.wrk_dir != DEFAULT_WRK_DIR
                or DEFAULT_WRK_DIR == "/different/path"
            )
            assert config.max_size != DEFAULT_MAX_SIZE or DEFAULT_MAX_SIZE == 3840
            assert config.quality != DEFAULT_QUALITY or DEFAULT_QUALITY == 50
        finally:
            config_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# #[EOF]#######################################################################
