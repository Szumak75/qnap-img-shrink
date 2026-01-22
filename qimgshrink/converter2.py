# -*- coding: utf-8 -*-
"""
converter2.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: ImageMagick-based converter implementation (alternative to Pillow).
"""

from inspect import currentframe
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise

from qimgshrink.files import ImageFileInfo
from qimgshrink.converter import ConversionStats


class _Keys(object, metaclass=ReadOnlyClass):
    """Class containing constant keys for converter configuration."""

    MAX_SIZE: str = "__max_size__"
    QUALITY: str = "__quality__"
    STATS: str = "__stats__"
    TEST_MODE: str = "__test_mode__"


class Converter2(BData):
    """ImageMagick-based image converter class.

    Alternative implementation using external 'convert' command from ImageMagick
    instead of Pillow. Provides the same API as Converter class.

    Requires ImageMagick to be installed on the system.
    """

    def __init__(self, max_size: int, quality: int, test_mode: bool = False) -> None:
        """Initialize Converter2 with configuration.

        ### Arguments:
        * max_size: int - Maximum size for longest image dimension.
        * quality: int - JPEG quality (1-100).
        * test_mode: bool - If True, analyze without modifying files.

        ### Raises:
        * RuntimeError: If ImageMagick is not available.
        """
        # Check if ImageMagick is available
        if not self._check_imagemagick():
            raise Raise.error(
                message="ImageMagick 'convert' and 'identify' commands not found. "
                "Please install ImageMagick.",
                exception=RuntimeError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        self._set_data(key=_Keys.MAX_SIZE, value=max_size, set_default_type=int)
        self._set_data(key=_Keys.QUALITY, value=quality, set_default_type=int)
        self._set_data(
            key=_Keys.STATS, value=ConversionStats(), set_default_type=ConversionStats
        )
        self._set_data(key=_Keys.TEST_MODE, value=test_mode, set_default_type=bool)

    def _check_imagemagick(self) -> bool:
        """Check if ImageMagick tools are available.

        ### Returns:
        bool - True if both 'convert' and 'identify' are available.
        """
        try:
            subprocess.run(
                ["convert", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            subprocess.run(
                ["identify", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            return True
        except FileNotFoundError:
            return False

    @property
    def max_size(self) -> int:
        """Get maximum image dimension.

        ### Returns:
        int - Maximum size in pixels.
        """
        tmp: Optional[int] = self._get_data(key=_Keys.MAX_SIZE)
        if tmp is None:
            raise Raise.error(
                message="Max size not initialized.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def quality(self) -> int:
        """Get JPEG quality setting.

        ### Returns:
        int - Quality value (1-100).
        """
        tmp: Optional[int] = self._get_data(key=_Keys.QUALITY)
        if tmp is None:
            raise Raise.error(
                message="Quality not initialized.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def stats(self) -> ConversionStats:
        """Get conversion statistics.

        ### Returns:
        ConversionStats - Statistics object.
        """
        tmp: Optional[ConversionStats] = self._get_data(key=_Keys.STATS)
        if tmp is None:
            raise Raise.error(
                message="Statistics not initialized.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def test_mode(self) -> bool:
        """Get test mode flag.

        ### Returns:
        bool - True if in test mode.
        """
        tmp: Optional[bool] = self._get_data(key=_Keys.TEST_MODE)
        if tmp is None:
            return False
        return tmp

    def _get_image_dimensions(self, file_path: Path) -> tuple[int, int]:
        """Get image dimensions using ImageMagick identify.

        ### Arguments:
        * file_path: Path - Path to image file.

        ### Returns:
        tuple[int, int] - Width and height in pixels.

        ### Raises:
        * RuntimeError: If identify command fails.
        """
        try:
            result = subprocess.run(
                ["identify", "-format", "%w %h", str(file_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True,
            )
            width_str, height_str = result.stdout.strip().split()
            return int(width_str), int(height_str)
        except (subprocess.CalledProcessError, ValueError) as e:
            raise Raise.error(
                message=f"Failed to get image dimensions: {e}",
                exception=RuntimeError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

    def convert(self, image_info: ImageFileInfo) -> bool:
        """Convert and compress image file using ImageMagick.

        Checks file accessibility, resizes if needed, applies compression
        based on format, and preserves original permissions.

        ### Arguments:
        * image_info: ImageFileInfo - Image file metadata and path.

        ### Returns:
        bool - True if file was processed, False if skipped.

        ### Raises:
        * PermissionError: If file is not readable/writable.
        * RuntimeError: If ImageMagick commands fail.
        """
        file_path = Path(image_info.path)

        # Check read/write access
        if not os.access(file_path, os.R_OK):
            raise Raise.error(
                message=f"No read access to file: {file_path}",
                exception=PermissionError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        if not os.access(file_path, os.W_OK):
            raise Raise.error(
                message=f"No write access to file: {file_path}",
                exception=PermissionError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        try:
            # Get image dimensions
            width, height = self._get_image_dimensions(file_path)
            max_dimension = max(width, height)

            # Check if resize is needed
            if max_dimension <= self.max_size:
                self.stats.add_skipped()
                return False

            # Get file format
            original_format = file_path.suffix.lower().lstrip(".")

            # Create temporary file
            tmp_fd, tmp_path_str = tempfile.mkstemp(
                suffix=file_path.suffix, dir=file_path.parent
            )
            os.close(tmp_fd)
            tmp_path = Path(tmp_path_str)

            try:
                # Build convert command
                convert_cmd = [
                    "convert",
                    str(file_path),
                    "-resize",
                    f"{self.max_size}x{self.max_size}>",  # > means only shrink larger images
                ]

                # Add format-specific options
                if original_format in ["jpg", "jpeg"]:
                    # JPEG: quality setting
                    convert_cmd.extend(["-quality", str(self.quality)])
                elif original_format == "png":
                    # PNG: maximum compression with interlace
                    convert_cmd.extend(
                        ["-quality", "100", "-define", "png:compression-level=9"]
                    )
                    convert_cmd.append("-interlace")
                    convert_cmd.append("PNG")

                # Output file
                convert_cmd.append(str(tmp_path))

                # Execute conversion
                result = subprocess.run(
                    convert_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                # Get file sizes
                size_before = image_info.size
                size_after = tmp_path.stat().st_size

                # In test mode, don't actually replace the file
                if not self.test_mode:
                    # Replace original file (use shutil.move for cross-device compatibility)
                    shutil.move(str(tmp_path), str(file_path))

                    # Restore original permissions
                    os.chmod(file_path, image_info.permissions)

                    # Try to restore owner/group (may require privileges)
                    try:
                        os.chown(file_path, image_info.uid, image_info.gid)
                    except PermissionError:
                        # Cannot restore ownership, skip
                        pass
                else:
                    # Test mode: clean up temporary file
                    tmp_path.unlink()

                # Update statistics
                self.stats.add_processed(size_before, size_after)
                return True

            except subprocess.CalledProcessError as e:
                # Clean up temporary file on error
                if tmp_path.exists():
                    tmp_path.unlink()
                raise Raise.error(
                    message=f"ImageMagick convert failed: {e.stderr.decode()}",
                    exception=RuntimeError,
                    class_name=self._c_name,
                    currentframe=currentframe(),
                )
            except Exception as e:
                # Clean up temporary file on any error
                if tmp_path.exists():
                    tmp_path.unlink()
                raise

        except Exception as e:
            if isinstance(e, (PermissionError, RuntimeError)):
                raise
            raise Raise.error(
                message=f"Failed to convert image {file_path}: {e}",
                exception=type(e),
                class_name=self._c_name,
                currentframe=currentframe(),
            )

    def print_report(self) -> None:
        """Print conversion statistics report to console.

        Displays formatted statistics including total files processed,
        skipped, size comparison, and compression ratio.
        """
        print("\n" + "=" * 60)
        print(str(self.stats))
        print("=" * 60)


# #[EOF]#######################################################################
