#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_converter.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for Converter class.
"""

import pytest
from pathlib import Path
import tempfile
from PIL import Image

from qimgshrink.converter import Converter


class TestConverterInit:
    """Test suite for Converter initialization."""

    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        converter = Converter(max_size=1920, quality=85)
        assert converter.max_size == 1920
        assert converter.quality == 85

    def test_init_with_different_values(self):
        """Test initialization with different values."""
        converter = Converter(max_size=2560, quality=95)
        assert converter.max_size == 2560
        assert converter.quality == 95


class TestConverterProperties:
    """Test suite for Converter properties."""

    def test_max_size_property(self):
        """Test max_size property access."""
        converter = Converter(max_size=1024, quality=90)
        assert converter.max_size == 1024

    def test_quality_property(self):
        """Test quality property access."""
        converter = Converter(max_size=1024, quality=75)
        assert converter.quality == 75


class TestConverterConvert:
    """Test suite for Converter.convert() method."""

    def create_test_image(
        self, path: Path, size: tuple = (2000, 1500), format: str = "JPEG"
    ):
        """Helper method to create test images."""
        img = Image.new("RGB", size, color="red")
        img.save(path, format=format)

    def test_convert_large_image_to_smaller(self):
        """Test converting large image to smaller size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.jpg")
            output_path = Path(tmpdir, "output.jpg")

            # Create large test image
            self.create_test_image(input_path, size=(2000, 1500))

            # Convert
            converter = Converter(max_size=1000, quality=85)
            converter.convert(str(input_path), str(output_path))

            # Verify output exists
            assert output_path.exists()

            # Verify size is reduced
            with Image.open(output_path) as img:
                assert img.width <= 1000
                assert img.height <= 1000

    def test_convert_maintains_aspect_ratio(self):
        """Test that conversion maintains aspect ratio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.jpg")
            output_path = Path(tmpdir, "output.jpg")

            # Create test image with specific aspect ratio (2:1)
            self.create_test_image(input_path, size=(2000, 1000))

            # Convert
            converter = Converter(max_size=1000, quality=85)
            converter.convert(str(input_path), str(output_path))

            # Verify aspect ratio is maintained
            with Image.open(output_path) as img:
                aspect_ratio = img.width / img.height
                assert abs(aspect_ratio - 2.0) < 0.01  # Allow small tolerance

    def test_convert_small_image_unchanged(self):
        """Test that small images are not upscaled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.jpg")
            output_path = Path(tmpdir, "output.jpg")

            # Create small test image
            original_size = (500, 300)
            self.create_test_image(input_path, size=original_size)

            # Convert with larger max_size
            converter = Converter(max_size=1920, quality=85)
            converter.convert(str(input_path), str(output_path))

            # Verify size is not increased
            with Image.open(output_path) as img:
                assert img.width <= original_size[0]
                assert img.height <= original_size[1]

    def test_convert_portrait_image(self):
        """Test converting portrait-oriented image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.jpg")
            output_path = Path(tmpdir, "output.jpg")

            # Create portrait image (taller than wide)
            self.create_test_image(input_path, size=(1000, 2000))

            # Convert
            converter = Converter(max_size=1000, quality=85)
            converter.convert(str(input_path), str(output_path))

            # Verify output exists and respects max_size
            with Image.open(output_path) as img:
                assert img.width <= 1000
                assert img.height <= 1000

    def test_convert_square_image(self):
        """Test converting square image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.jpg")
            output_path = Path(tmpdir, "output.jpg")

            # Create square image
            self.create_test_image(input_path, size=(1500, 1500))

            # Convert
            converter = Converter(max_size=800, quality=85)
            converter.convert(str(input_path), str(output_path))

            # Verify square aspect is maintained
            with Image.open(output_path) as img:
                assert abs(img.width - img.height) <= 1  # Should be nearly equal

    def test_convert_different_quality_settings(self):
        """Test conversion with different quality settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.jpg")
            output_high = Path(tmpdir, "output_high.jpg")
            output_low = Path(tmpdir, "output_low.jpg")

            self.create_test_image(input_path, size=(1000, 1000))

            # Convert with high quality
            converter_high = Converter(max_size=800, quality=95)
            converter_high.convert(str(input_path), str(output_high))

            # Convert with low quality
            converter_low = Converter(max_size=800, quality=50)
            converter_low.convert(str(input_path), str(output_low))

            # Both should exist
            assert output_high.exists()
            assert output_low.exists()

            # Lower quality should result in smaller file size
            size_high = output_high.stat().st_size
            size_low = output_low.stat().st_size
            assert size_low < size_high

    def test_convert_nonexistent_input_file(self):
        """Test conversion with non-existent input file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "nonexistent.jpg")
            output_path = Path(tmpdir, "output.jpg")

            converter = Converter(max_size=1000, quality=85)

            with pytest.raises(FileNotFoundError):
                converter.convert(str(input_path), str(output_path))

    def test_convert_invalid_image_file(self):
        """Test conversion with invalid image file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "invalid.jpg")
            output_path = Path(tmpdir, "output.jpg")

            # Create invalid image file
            with open(input_path, "w") as f:
                f.write("This is not an image")

            converter = Converter(max_size=1000, quality=85)

            with pytest.raises(Exception):  # PIL raises various exceptions
                converter.convert(str(input_path), str(output_path))

    def test_convert_png_image(self):
        """Test converting PNG image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir, "input.png")
            output_path = Path(tmpdir, "output.png")

            self.create_test_image(input_path, size=(2000, 1500), format="PNG")

            converter = Converter(max_size=1000, quality=85)
            converter.convert(str(input_path), str(output_path))

            assert output_path.exists()
            with Image.open(output_path) as img:
                assert img.width <= 1000
                assert img.height <= 1000


class TestConverterIntegration:
    """Integration tests for Converter with Config."""

    def test_converter_with_config_parameters(self):
        """Test Converter using Config parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from qimgshrink.main import Config

            config = Config()
            config.max_size = 1024
            config.quality = 90

            converter = Converter(max_size=config.max_size, quality=config.quality)

            assert converter.max_size == 1024
            assert converter.quality == 90


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# #[EOF]#######################################################################
