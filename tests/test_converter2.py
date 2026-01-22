#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_converter2.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for Converter2 class (ImageMagick-based).
"""

import pytest
from pathlib import Path
import tempfile
import os
from PIL import Image

from qimgshrink.converter2 import Converter2
from qimgshrink.converter import ConversionStats
from qimgshrink.files import ImageFileInfo


class TestConverter2Init:
    """Test suite for Converter2 initialization."""

    def test_converter2_initialization(self) -> None:
        """Test Converter2 initialization with valid parameters."""
        converter = Converter2(max_size=1920, quality=85)

        assert converter.max_size == 1920
        assert converter.quality == 85
        assert converter.test_mode is False
        assert isinstance(converter.stats, ConversionStats)

    def test_converter2_with_test_mode(self) -> None:
        """Test Converter2 initialization with test mode."""
        converter = Converter2(max_size=1920, quality=85, test_mode=True)

        assert converter.test_mode is True


class TestConverter2ImageMagick:
    """Test ImageMagick availability check."""

    def test_imagemagick_available(self) -> None:
        """Test that ImageMagick is available on system."""
        import subprocess

        try:
            result = subprocess.run(
                ["convert", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("ImageMagick not installed")


class TestConverter2Convert:
    """Test suite for Converter2.convert() method."""

    def create_test_image(self, path: Path, size: tuple = (3000, 2000)) -> None:
        """Helper to create test image."""
        img = Image.new("RGB", size, "red")
        img.save(path, "JPEG")

    def create_image_file_info(self, path: Path) -> ImageFileInfo:
        """Helper to create ImageFileInfo object."""
        stat = os.stat(path)

        return ImageFileInfo(
            path=str(path),
            permissions=stat.st_mode & 0o777,
            uid=stat.st_uid,
            gid=stat.st_gid,
            size=stat.st_size,
        )

    def test_convert_large_jpeg_image(self) -> None:
        """Test converting large JPEG image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "large.jpg"
            self.create_test_image(image_path, size=(3000, 2000))

            info = self.create_image_file_info(image_path)
            converter = Converter2(max_size=1920, quality=85)

            result = converter.convert(info)

            assert result is True
            assert converter.stats.processed_files == 1
            assert converter.stats.skipped_files == 0

            # Check that image was resized
            from PIL import Image

            with Image.open(image_path) as img:
                assert max(img.size) == 1920

    def test_convert_small_image_skipped(self) -> None:
        """Test that small images are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "small.jpg"
            self.create_test_image(image_path, size=(800, 600))

            info = self.create_image_file_info(image_path)
            converter = Converter2(max_size=1920, quality=85)

            result = converter.convert(info)

            assert result is False
            assert converter.stats.processed_files == 0
            assert converter.stats.skipped_files == 1

    def test_convert_in_test_mode(self) -> None:
        """Test that test mode doesn't modify files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "test.jpg"
            self.create_test_image(image_path, size=(3000, 2000))

            original_size = image_path.stat().st_size
            original_mtime = image_path.stat().st_mtime

            info = self.create_image_file_info(image_path)
            converter = Converter2(max_size=1920, quality=85, test_mode=True)

            result = converter.convert(info)

            assert result is True
            assert converter.stats.processed_files == 1

            # File should not be modified
            assert image_path.stat().st_size == original_size
            assert image_path.stat().st_mtime == original_mtime

    def test_convert_png_image(self) -> None:
        """Test converting PNG image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "large.png"
            img = Image.new("RGB", (2500, 1800), "blue")
            img.save(image_path, "PNG")

            info = self.create_image_file_info(image_path)
            converter = Converter2(max_size=1920, quality=85)

            result = converter.convert(info)

            assert result is True
            assert converter.stats.processed_files == 1

            # Check that image was resized
            with Image.open(image_path) as img:
                assert max(img.size) == 1920


class TestConverter2Integration:
    """Integration tests for Converter2."""

    def test_converter2_with_multiple_images(self) -> None:
        """Test Converter2 with multiple images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test images
            for i in range(3):
                img_path = Path(tmpdir) / f"image{i}.jpg"
                img = Image.new("RGB", (2500, 1800), "red")
                img.save(img_path, "JPEG")

            converter = Converter2(max_size=1920, quality=85)

            # Process all images
            for img_path in Path(tmpdir).glob("*.jpg"):
                stat = os.stat(img_path)

                info = ImageFileInfo(
                    path=str(img_path),
                    permissions=stat.st_mode & 0o777,
                    uid=stat.st_uid,
                    gid=stat.st_gid,
                    size=stat.st_size,
                )
                converter.convert(info)

            assert converter.stats.processed_files == 3
            assert converter.stats.total_files == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# #[EOF]#######################################################################
