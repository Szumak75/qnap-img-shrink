#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_converter_factory.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for converter factory.
"""

import pytest

from qimgshrink.converter_factory import create_converter
from qimgshrink.converter import Converter
from qimgshrink.converter2 import Converter2


class TestConverterFactory:
    """Test suite for converter factory."""

    def test_create_converter_default(self) -> None:
        """Test factory creates a converter with default preference."""
        converter = create_converter(1920, 85)

        # Should create either Converter or Converter2
        assert isinstance(converter, (Converter, Converter2))
        assert converter.max_size == 1920
        assert converter.quality == 85

    def test_create_converter_prefer_imagemagick(self) -> None:
        """Test factory with ImageMagick preference."""
        try:
            converter = create_converter(1920, 85, prefer_imagemagick=True)
            assert isinstance(converter, (Converter, Converter2))
        except RuntimeError:
            pytest.skip("No converter implementation available")

    def test_create_converter_with_test_mode(self) -> None:
        """Test factory creates converter with test mode."""
        converter = create_converter(1920, 85, test_mode=True)

        assert converter.test_mode is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# #[EOF]#######################################################################
