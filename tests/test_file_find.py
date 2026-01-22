#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_file_find.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Unit tests for FileFind class.
"""

import pytest
from pathlib import Path
import tempfile
import os

from qimgshrink.files import FileFind, ImageFileInfo


class TestImageFileInfo:
    """Test suite for ImageFileInfo class."""

    def test_image_file_info_creation(self):
        """Test ImageFileInfo object creation."""
        info = ImageFileInfo(
            path="/test/image.jpg",
            permissions=0o644,
            uid=1000,
            gid=100,
            size=1024,
        )

        assert info.path == "/test/image.jpg"
        assert info.permissions == 0o644
        assert info.uid == 1000
        assert info.gid == 100
        assert info.size == 1024

    def test_permissions_str_property(self):
        """Test permissions string representation."""
        info = ImageFileInfo(
            path="/test/image.jpg",
            permissions=0o644,
            uid=1000,
            gid=100,
            size=100,
        )

        assert info.permissions_str == "644"

    def test_repr_method(self):
        """Test __repr__ method."""
        info = ImageFileInfo(
            path="/test/image.jpg",
            permissions=0o755,
            uid=1000,
            gid=100,
            size=2048,
        )

        repr_str = repr(info)
        assert "ImageFileInfo" in repr_str
        assert "/test/image.jpg" in repr_str
        assert "uid=1000" in repr_str
        assert "gid=100" in repr_str

    def test_str_method(self):
        """Test __str__ method."""
        info = ImageFileInfo(
            path="/test/image.jpg",
            permissions=0o644,
            uid=1000,
            gid=100,
            size=1024,
        )

        str_repr = str(info)
        assert "/test/image.jpg" in str_repr
        assert "uid=1000" in str_repr
        assert "gid=100" in str_repr
        assert "644" in str_repr
        assert "1024 bytes" in str_repr


class TestFileFindInit:
    """Test suite for FileFind initialization."""

    def test_init_with_valid_path(self):
        """Test initialization with valid directory path."""
        finder = FileFind("/tmp")
        assert finder.wrk_dir == "/tmp"

    def test_wrk_dir_property(self):
        """Test working directory property access."""
        test_path = "/test/directory"
        finder = FileFind(test_path)
        assert finder.wrk_dir == test_path


class TestFileFindImages:
    """Test suite for FileFind.find_images() method."""

    def test_find_images_in_empty_directory(self):
        """Test finding images in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            finder = FileFind(tmpdir)
            images = finder.find_images()
            assert images == []

    def test_find_jpg_images(self):
        """Test finding JPG images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "image1.jpg").touch()
            Path(tmpdir, "image2.JPG").touch()
            Path(tmpdir, "image3.jpeg").touch()
            Path(tmpdir, "document.txt").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 3
            assert all(isinstance(img, ImageFileInfo) for img in images)
            paths = [img.path for img in images]
            assert any("image1.jpg" in p for p in paths)
            assert any("image2.JPG" in p for p in paths)
            assert any("image3.jpeg" in p for p in paths)
            assert not any("document.txt" in p for p in paths)

    def test_find_png_images(self):
        """Test finding PNG images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "photo.png").touch()
            Path(tmpdir, "PHOTO2.PNG").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 2
            assert all(isinstance(img, ImageFileInfo) for img in images)
            paths = [img.path for img in images]
            assert any("photo.png" in p for p in paths)
            assert any("PHOTO2.PNG" in p for p in paths)

    def test_find_bmp_images(self):
        """Test finding BMP images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "bitmap.bmp").touch()
            Path(tmpdir, "BITMAP2.BMP").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 2
            paths = [img.path for img in images]
            assert any("bitmap.bmp" in p for p in paths)

    def test_find_tiff_images(self):
        """Test finding TIFF images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "image.tiff").touch()
            Path(tmpdir, "image2.tif").touch()
            Path(tmpdir, "IMAGE3.TIFF").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 3
            paths = [img.path for img in images]
            assert any("image.tiff" in p for p in paths)
            assert any("image2.tif" in p for p in paths)

    def test_find_images_in_subdirectories(self):
        """Test finding images in subdirectories recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            subdir1 = Path(tmpdir, "subdir1")
            subdir2 = Path(tmpdir, "subdir2")
            nested = Path(tmpdir, "subdir1", "nested")

            subdir1.mkdir()
            subdir2.mkdir()
            nested.mkdir()

            # Create test files
            Path(tmpdir, "root.jpg").touch()
            Path(subdir1, "sub1.png").touch()
            Path(subdir2, "sub2.bmp").touch()
            Path(nested, "nested.tiff").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 4
            paths = [img.path for img in images]
            assert any("root.jpg" in p for p in paths)
            assert any("sub1.png" in p for p in paths)
            assert any("sub2.bmp" in p for p in paths)
            assert any("nested.tiff" in p for p in paths)

    def test_find_images_mixed_extensions(self):
        """Test finding images with different extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "photo.jpg").touch()
            Path(tmpdir, "image.png").touch()
            Path(tmpdir, "bitmap.bmp").touch()
            Path(tmpdir, "scan.tiff").touch()
            Path(tmpdir, "document.pdf").touch()
            Path(tmpdir, "text.txt").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 4
            paths = [img.path for img in images]
            assert not any("document.pdf" in p for p in paths)
            assert not any("text.txt" in p for p in paths)

    def test_find_images_case_insensitive(self):
        """Test case-insensitive extension matching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "lower.jpg").touch()
            Path(tmpdir, "upper.JPG").touch()
            Path(tmpdir, "mixed.JpG").touch()
            Path(tmpdir, "png_lower.png").touch()
            Path(tmpdir, "png_upper.PNG").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 5

    def test_find_images_returns_absolute_paths(self):
        """Test that returned paths are absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "image.jpg").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 1
            assert Path(images[0].path).is_absolute()

    def test_find_images_returns_sorted_list(self):
        """Test that returned list is sorted by path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "zebra.jpg").touch()
            Path(tmpdir, "apple.png").touch()
            Path(tmpdir, "middle.bmp").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            paths = [img.path for img in images]
            assert paths == sorted(paths)

    def test_find_images_includes_metadata(self):
        """Test that ImageFileInfo includes file metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.jpg")
            test_file.touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 1
            img_info = images[0]

            # Verify metadata is present
            assert img_info.uid is not None
            assert img_info.gid is not None
            assert isinstance(img_info.permissions, int)
            assert img_info.size >= 0
            assert img_info.permissions_str is not None

    def test_find_images_nonexistent_directory(self):
        """Test finding images in non-existent directory raises error."""
        finder = FileFind("/nonexistent/directory/path")

        with pytest.raises(FileNotFoundError):
            finder.find_images()

    def test_find_images_file_instead_of_directory(self):
        """Test finding images when path is a file, not directory."""
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile_path = tmpfile.name

        try:
            finder = FileFind(tmpfile_path)
            with pytest.raises(NotADirectoryError):
                finder.find_images()
        finally:
            os.unlink(tmpfile_path)

    def test_find_images_ignores_directories_with_image_extensions(self):
        """Test that directories with image-like names are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with image extension in name
            fake_dir = Path(tmpdir, "folder.jpg")
            fake_dir.mkdir()

            # Create real image
            Path(tmpdir, "real.jpg").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            # Should find only the real file, not the directory
            assert len(images) == 1
            assert "real.jpg" in images[0].path.path.path

    def test_supported_extensions_constant(self):
        """Test that SUPPORTED_EXTENSIONS contains expected values."""
        expected = {".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".png"}
        assert FileFind.SUPPORTED_EXTENSIONS == expected


class TestFileFindIntegration:
    """Integration tests for FileFind with Config."""

    def test_find_images_with_config_wrk_dir(self):
        """Test integration with Config class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.jpg").touch()
            Path(tmpdir, "test.png").touch()

            from qimgshrink.main import Config

            config = Config()
            config.wrk_dir = tmpdir

            finder = FileFind(config.wrk_dir)
            images = finder.find_images()

            assert len(images) == 2
            assert all(isinstance(img, ImageFileInfo) for img in images)

    """Test suite for FileFind initialization."""

    def test_init_with_valid_path(self) -> None:
        """Test initialization with valid directory path."""
        finder = FileFind("/tmp")
        assert finder.wrk_dir == "/tmp"

    def test_wrk_dir_property(self) -> None:
        """Test working directory property access."""
        test_path = "/test/directory"
        finder = FileFind(test_path)
        assert finder.wrk_dir == test_path


class TestFileFindImages:
    """Test suite for FileFind.find_images() method."""

    def test_find_images_in_empty_directory(self) -> None:
        """Test finding images in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            finder = FileFind(tmpdir)
            images = finder.find_images()
            assert images == []

    def test_find_jpg_images(self) -> None:
        """Test finding JPG images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "image1.jpg").touch()
            Path(tmpdir, "image2.JPG").touch()
            Path(tmpdir, "image3.jpeg").touch()
            Path(tmpdir, "document.txt").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 3
            assert any("image1.jpg" in img.path for img in images)
            assert any("image2.JPG" in img.path for img in images)
            assert any("image3.jpeg" in img.path for img in images)
            assert not any("document.txt" in img.path for img in images)

    def test_find_png_images(self) -> None:
        """Test finding PNG images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "photo.png").touch()
            Path(tmpdir, "PHOTO2.PNG").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 2
            assert any("photo.png" in img.path for img in images)
            assert any("PHOTO2.PNG" in img.path for img in images)

    def test_find_bmp_images(self) -> None:
        """Test finding BMP images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "bitmap.bmp").touch()
            Path(tmpdir, "BITMAP2.BMP").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 2
            assert any("bitmap.bmp" in img.path for img in images)

    def test_find_tiff_images(self) -> None:
        """Test finding TIFF images."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "image.tiff").touch()
            Path(tmpdir, "image2.tif").touch()
            Path(tmpdir, "IMAGE3.TIFF").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 3
            assert any("image.tiff" in img.path for img in images)
            assert any("image2.tif" in img.path for img in images)

    def test_find_images_in_subdirectories(self) -> None:
        """Test finding images in subdirectories recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            subdir1 = Path(tmpdir, "subdir1")
            subdir2 = Path(tmpdir, "subdir2")
            nested = Path(tmpdir, "subdir1", "nested")

            subdir1.mkdir()
            subdir2.mkdir()
            nested.mkdir()

            # Create test files
            Path(tmpdir, "root.jpg").touch()
            Path(subdir1, "sub1.png").touch()
            Path(subdir2, "sub2.bmp").touch()
            Path(nested, "nested.tiff").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 4
            assert any("root.jpg" in img.path for img in images)
            assert any("sub1.png" in img.path for img in images)
            assert any("sub2.bmp" in img.path for img in images)
            assert any("nested.tiff" in img.path for img in images)

    def test_find_images_mixed_extensions(self) -> None:
        """Test finding images with different extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "photo.jpg").touch()
            Path(tmpdir, "image.png").touch()
            Path(tmpdir, "bitmap.bmp").touch()
            Path(tmpdir, "scan.tiff").touch()
            Path(tmpdir, "document.pdf").touch()
            Path(tmpdir, "text.txt").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 4
            assert not any("document.pdf" in img.path for img in images)
            assert not any("text.txt" in img.path for img in images)

    def test_find_images_case_insensitive(self) -> None:
        """Test case-insensitive extension matching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "lower.jpg").touch()
            Path(tmpdir, "upper.JPG").touch()
            Path(tmpdir, "mixed.JpG").touch()
            Path(tmpdir, "png_lower.png").touch()
            Path(tmpdir, "png_upper.PNG").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 5

    def test_find_images_returns_absolute_paths(self) -> None:
        """Test that returned paths are absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "image.jpg").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            assert len(images) == 1
            assert Path(images[0].path).is_absolute()

    def test_find_images_returns_sorted_list(self) -> None:
        """Test that returned list is sorted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "zebra.jpg").touch()
            Path(tmpdir, "apple.png").touch()
            Path(tmpdir, "middle.bmp").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            paths = [img.path for img in images]
            assert paths == sorted(paths)

    def test_find_images_nonexistent_directory(self) -> None:
        """Test finding images in non-existent directory raises error."""
        finder = FileFind("/nonexistent/directory/path")

        with pytest.raises(FileNotFoundError):
            finder.find_images()

    def test_find_images_file_instead_of_directory(self) -> None:
        """Test finding images when path is a file, not directory."""
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile_path = tmpfile.name

        try:
            finder = FileFind(tmpfile_path)
            with pytest.raises(NotADirectoryError):
                finder.find_images()
        finally:
            os.unlink(tmpfile_path)

    def test_find_images_ignores_directories_with_image_extensions(self) -> None:
        """Test that directories with image-like names are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with image extension in name
            fake_dir = Path(tmpdir, "folder.jpg")
            fake_dir.mkdir()

            # Create real image
            Path(tmpdir, "real.jpg").touch()

            finder = FileFind(tmpdir)
            images = finder.find_images()

            # Should find only the real file, not the directory
            assert len(images) == 1
            assert "real.jpg" in images[0].path

    def test_supported_extensions_constant(self) -> None:
        """Test that SUPPORTED_EXTENSIONS contains expected values."""
        expected = {".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".png"}
        assert FileFind.SUPPORTED_EXTENSIONS == expected


class TestFileFindIntegration:
    """Integration tests for FileFind with Config."""

    def test_find_images_with_config_wrk_dir(self) -> None:
        """Test integration with Config class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.jpg").touch()
            Path(tmpdir, "test.png").touch()

            from qimgshrink.main import Config

            config = Config()
            config.wrk_dir = tmpdir

            finder = FileFind(config.wrk_dir)
            images = finder.find_images()

            assert len(images) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# #[EOF]#######################################################################
