#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_converter_new.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for new Converter class with ImageFileInfo API.
"""

import pytest
from pathlib import Path
import tempfile
import os
from PIL import Image

from qimgshrink.converter import Converter, ConversionStats
from qimgshrink.files import ImageFileInfo


class TestConversionStats:
    """Test suite for ConversionStats class."""

    def test_stats_initialization(self):
        """Test ConversionStats initialization."""
        stats = ConversionStats()
        assert stats.processed_files == 0
        assert stats.skipped_files == 0
        assert stats.size_before == 0
        assert stats.size_after == 0

    def test_add_processed(self):
        """Test adding processed file statistics."""
        stats = ConversionStats()
        stats.add_processed(1000, 500)

        assert stats.processed_files == 1
        assert stats.size_before == 1000
        assert stats.size_after == 500
        assert stats.saved_bytes == 500
        assert stats.compression_ratio == 50.0

    def test_add_skipped(self):
        """Test adding skipped file count."""
        stats = ConversionStats()
        stats.add_skipped()

        assert stats.skipped_files == 1
        assert stats.total_files == 1

    def test_compression_ratio_zero_size(self):
        """Test compression ratio with zero size."""
        stats = ConversionStats()
        assert stats.compression_ratio == 0.0

    def test_str_representation(self):
        """Test string representation of stats."""
        stats = ConversionStats()
        stats.add_processed(1000, 700)
        stats.add_skipped()

        str_repr = str(stats)
        assert "Total files: 2" in str_repr
        assert "Processed: 1" in str_repr
        assert "Skipped: 1" in str_repr


class TestConverterInit:
    """Test suite for Converter initialization."""

    def test_init_with_valid_parameters(self):
        """Test initialization with valid parameters."""
        converter = Converter(max_size=1920, quality=85)
        assert converter.max_size == 1920
        assert converter.quality == 85
        assert isinstance(converter.stats, ConversionStats)

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

    def test_stats_property(self):
        """Test stats property access."""
        converter = Converter(max_size=1024, quality=75)
        assert isinstance(converter.stats, ConversionStats)


class TestConverterConvert:
    """Test suite for Converter.convert() method."""

    def create_test_image(
        self, path: Path, size: tuple = (2000, 1500), format: str = "JPEG"
    ):
        """Helper method to create test images."""
        img = Image.new("RGB", size, color="red")
        img.save(path, format=format)

    def create_image_file_info(self, path: Path) -> ImageFileInfo:
        """Helper to create ImageFileInfo from file."""
        stat_info = path.stat()

        return ImageFileInfo(
            path=str(path.absolute()),
            permissions=stat_info.st_mode & 0o777,
            uid=stat_info.st_uid,
            gid=stat_info.st_gid,
            size=stat_info.st_size,
        )

    def test_convert_large_jpeg_image(self):
        """Test converting large JPEG image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "large.jpg")
            self.create_test_image(test_file, size=(3000, 2000))

            img_info = self.create_image_file_info(test_file)
            original_size = img_info.size

            converter = Converter(max_size=1920, quality=85)
            result = converter.convert(img_info)

            assert result is True  # Was processed
            assert test_file.exists()

            # Check new size
            with Image.open(test_file) as im:
                assert im.width <= 1920
                assert im.height <= 1920

            # Check file was compressed
            new_size = test_file.stat().st_size
            assert new_size < original_size

    def test_convert_large_png_image(self):
        """Test converting large PNG image with interlace."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "large.png")
            self.create_test_image(test_file, size=(3000, 2000), format="PNG")

            img_info = self.create_image_file_info(test_file)

            converter = Converter(max_size=1920, quality=85)
            result = converter.convert(img_info)

            assert result is True
            assert test_file.exists()

            with Image.open(test_file) as im:
                assert im.width <= 1920
                assert im.height <= 1920

    def test_convert_small_image_skipped(self):
        """Test that small images are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "small.jpg")
            self.create_test_image(test_file, size=(800, 600))

            img_info = self.create_image_file_info(test_file)
            original_size = img_info.size

            converter = Converter(max_size=1920, quality=85)
            result = converter.convert(img_info)

            assert result is False  # Was skipped
            assert test_file.stat().st_size == original_size  # Unchanged

    def test_convert_maintains_aspect_ratio(self):
        """Test that conversion maintains aspect ratio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.jpg")
            # Create 2:1 aspect ratio image
            self.create_test_image(test_file, size=(3000, 1500))

            img_info = self.create_image_file_info(test_file)

            converter = Converter(max_size=1920, quality=85)
            converter.convert(img_info)

            with Image.open(test_file) as im:
                aspect_ratio = im.width / im.height
                assert abs(aspect_ratio - 2.0) < 0.01

    def test_convert_portrait_image(self):
        """Test converting portrait-oriented image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "portrait.jpg")
            self.create_test_image(test_file, size=(1500, 3000))

            img_info = self.create_image_file_info(test_file)

            converter = Converter(max_size=1920, quality=85)
            converter.convert(img_info)

            with Image.open(test_file) as im:
                assert im.height <= 1920
                assert im.width <= 1920
                assert im.height > im.width  # Still portrait

    def test_convert_preserves_permissions(self):
        """Test that conversion preserves file permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.jpg")
            self.create_test_image(test_file, size=(3000, 2000))

            # Set specific permissions
            os.chmod(test_file, 0o644)

            img_info = self.create_image_file_info(test_file)

            converter = Converter(max_size=1920, quality=85)
            converter.convert(img_info)

            # Check permissions preserved
            new_perms = test_file.stat().st_mode & 0o777
            assert new_perms == 0o644

    def test_convert_updates_statistics(self):
        """Test that conversion updates statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.jpg")
            self.create_test_image(test_file, size=(3000, 2000))

            img_info = self.create_image_file_info(test_file)

            converter = Converter(max_size=1920, quality=85)
            converter.convert(img_info)

            assert converter.stats.processed_files == 1
            assert converter.stats.size_before > 0
            assert converter.stats.size_after > 0

    def test_convert_no_read_access(self):
        """Test conversion fails with no read access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.jpg")
            self.create_test_image(test_file, size=(3000, 2000))

            # Remove read permissions
            os.chmod(test_file, 0o000)

            img_info = self.create_image_file_info(test_file)

            converter = Converter(max_size=1920, quality=85)

            with pytest.raises(PermissionError):
                converter.convert(img_info)

            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_convert_different_quality_settings(self):
        """Test that different quality settings affect file size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two identical files
            file1 = Path(tmpdir, "high.jpg")
            file2 = Path(tmpdir, "low.jpg")

            self.create_test_image(file1, size=(3000, 2000))
            self.create_test_image(file2, size=(3000, 2000))

            info1 = self.create_image_file_info(file1)
            info2 = self.create_image_file_info(file2)

            # Convert with different qualities
            converter_high = Converter(max_size=1920, quality=95)
            converter_low = Converter(max_size=1920, quality=50)

            converter_high.convert(info1)
            converter_low.convert(info2)

            size_high = file1.stat().st_size
            size_low = file2.stat().st_size

            # Lower quality should result in smaller file
            assert size_low < size_high


class TestConverterIntegration:
    """Integration tests for Converter with Config."""

    def test_converter_with_config_parameters(self):
        """Test Converter using Config parameters."""
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


class TestConverterTestMode:
    """Tests for Converter test mode functionality."""

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

    def test_converter_test_mode_initialization(self) -> None:
        """Test Converter can be initialized with test mode."""
        converter = Converter(max_size=1920, quality=85, test_mode=True)

        assert converter.test_mode is True
        assert converter.max_size == 1920
        assert converter.quality == 85

    def test_converter_test_mode_default_false(self) -> None:
        """Test Converter test mode defaults to False."""
        converter = Converter(max_size=1920, quality=85)

        assert converter.test_mode is False

    def test_convert_in_test_mode_doesnt_modify_file(self) -> None:
        """Test convert() in test mode doesn't modify files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create large test image
            image_path = Path(tmpdir) / "test_image.jpg"
            self.create_test_image(image_path, size=(3000, 2000))

            # Get original file info
            original_size = image_path.stat().st_size
            original_mtime = image_path.stat().st_mtime

            # Create ImageFileInfo
            info = self.create_image_file_info(image_path)

            # Convert in test mode
            converter = Converter(max_size=1920, quality=85, test_mode=True)
            result = converter.convert(info)

            # File should be marked as "would be processed"
            assert result is True

            # File should not be modified
            assert image_path.stat().st_size == original_size
            assert image_path.stat().st_mtime == original_mtime

            # Statistics should still be updated
            assert converter.stats.processed_files == 1
            assert converter.stats.size_before > 0
            assert converter.stats.size_after > 0

    def test_convert_in_test_mode_updates_statistics(self) -> None:
        """Test convert() in test mode updates statistics correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create large test image
            image_path = Path(tmpdir) / "large.jpg"
            self.create_test_image(image_path, size=(2500, 1800))

            info = self.create_image_file_info(image_path)

            # Convert in test mode
            converter = Converter(max_size=1920, quality=85, test_mode=True)
            converter.convert(info)

            # Verify statistics
            assert converter.stats.processed_files == 1
            assert converter.stats.skipped_files == 0
            assert converter.stats.total_files == 1
            assert converter.stats.size_before > 0
            assert converter.stats.size_after < converter.stats.size_before
            assert converter.stats.saved_bytes > 0


# #[EOF]#######################################################################
