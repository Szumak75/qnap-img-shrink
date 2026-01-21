#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_app.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for App class.
"""

import pytest
from pathlib import Path

from qimgshrink.main import App, Config

# Get default values from Config class
_DEFAULT_CONFIG = Config()
DEFAULT_WRK_DIR = _DEFAULT_CONFIG.wrk_dir
DEFAULT_MAX_SIZE = _DEFAULT_CONFIG.max_size
DEFAULT_QUALITY = _DEFAULT_CONFIG.quality
del _DEFAULT_CONFIG


class TestAppInit:
    """Test suite for App initialization."""

    def test_app_initialization(self):
        """Test App initialization creates Config."""
        app = App()
        assert app.config is not None
        assert isinstance(app.config, Config)

    def test_app_has_default_config_values(self):
        """Test that App has default configuration values."""
        app = App()
        assert app.config.wrk_dir == DEFAULT_WRK_DIR
        assert app.config.max_size == DEFAULT_MAX_SIZE
        assert app.config.quality == DEFAULT_QUALITY


class TestAppConfig:
    """Test suite for App.config property."""

    def test_config_property_returns_config(self):
        """Test config property returns Config instance."""
        app = App()
        config = app.config
        assert isinstance(config, Config)

    def test_config_is_same_instance(self):
        """Test that config property returns same instance."""
        app = App()
        config1 = app.config
        config2 = app.config
        assert config1 is config2


class TestAppRun:
    """Test suite for App.run() method."""

    def test_run_method_exists(self):
        """Test that run method exists and is callable."""
        app = App()
        assert hasattr(app, "run")
        assert callable(app.run)

    def test_run_method_executes_without_error(self):
        """Test that run method executes without error.

        Note: App.run() loads default config file, so we test with
        a valid working directory.
        """
        import os

        app = App()

        # Create working directory if it doesn't exist
        wrk_dir = DEFAULT_WRK_DIR
        os.makedirs(wrk_dir, exist_ok=True)

        try:
            # Should not raise any exception
            app.run()
        finally:
            # Clean up: try to remove if we created it and it's empty
            try:
                if os.path.exists(wrk_dir) and not os.listdir(wrk_dir):
                    os.rmdir(wrk_dir)
            except (OSError, PermissionError):
                pass  # Directory not empty or can't be removed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# #[EOF]#######################################################################
