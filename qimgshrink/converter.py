# -*- coding: utf-8 -*-
"""
converter.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026, 10:41:28

Purpose: Image conversion and compression utilities.
"""

from inspect import currentframe
from pathlib import Path
from typing import Optional
import os
import tempfile
import shutil

import PIL.Image as Image

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise

from qimgshrink.files import ImageFileInfo


class _ConversionStatsKeys(object, metaclass=ReadOnlyClass):
    """Keys for ConversionStats data storage."""

    PROCESSED_FILES: str = "__processed_files__"
    SKIPPED_FILES: str = "__skipped_files__"
    SIZE_BEFORE: str = "__size_before__"
    SIZE_AFTER: str = "__size_after__"


class ConversionStats(BData):
    """Container for conversion statistics."""

    def __init__(self) -> None:
        """Initialize conversion statistics."""
        self._set_data(
            key=_ConversionStatsKeys.PROCESSED_FILES, value=0, set_default_type=int
        )
        self._set_data(
            key=_ConversionStatsKeys.SKIPPED_FILES, value=0, set_default_type=int
        )
        self._set_data(
            key=_ConversionStatsKeys.SIZE_BEFORE, value=0, set_default_type=int
        )
        self._set_data(
            key=_ConversionStatsKeys.SIZE_AFTER, value=0, set_default_type=int
        )

    @property
    def processed_files(self) -> int:
        """Get number of processed files.

        ### Returns:
        int - Number of processed files.
        """
        tmp: Optional[int] = self._get_data(key=_ConversionStatsKeys.PROCESSED_FILES)
        if tmp is None:
            return 0
        return tmp

    @property
    def skipped_files(self) -> int:
        """Get number of skipped files.

        ### Returns:
        int - Number of skipped files.
        """
        tmp: Optional[int] = self._get_data(key=_ConversionStatsKeys.SKIPPED_FILES)
        if tmp is None:
            return 0
        return tmp

    @property
    def size_before(self) -> int:
        """Get total size before conversion.

        ### Returns:
        int - Total size in bytes.
        """
        tmp: Optional[int] = self._get_data(key=_ConversionStatsKeys.SIZE_BEFORE)
        if tmp is None:
            return 0
        return tmp

    @property
    def size_after(self) -> int:
        """Get total size after conversion.

        ### Returns:
        int - Total size in bytes.
        """
        tmp: Optional[int] = self._get_data(key=_ConversionStatsKeys.SIZE_AFTER)
        if tmp is None:
            return 0
        return tmp

    def add_processed(self, size_before: int, size_after: int) -> None:
        """Add processed file statistics.

        ### Arguments:
        * size_before: int - Original file size in bytes.
        * size_after: int - Converted file size in bytes.
        """
        current_processed = self.processed_files
        current_size_before = self.size_before
        current_size_after = self.size_after

        self._set_data(
            key=_ConversionStatsKeys.PROCESSED_FILES, value=current_processed + 1
        )
        self._set_data(
            key=_ConversionStatsKeys.SIZE_BEFORE,
            value=current_size_before + size_before,
        )
        self._set_data(
            key=_ConversionStatsKeys.SIZE_AFTER, value=current_size_after + size_after
        )

    def add_skipped(self) -> None:
        """Add skipped file count."""
        current_skipped = self.skipped_files
        self._set_data(
            key=_ConversionStatsKeys.SKIPPED_FILES, value=current_skipped + 1
        )

    @property
    def total_files(self) -> int:
        """Get total number of files."""
        return self.processed_files + self.skipped_files

    @property
    def saved_bytes(self) -> int:
        """Get number of saved bytes."""
        return self.size_before - self.size_after

    @property
    def compression_ratio(self) -> float:
        """Get compression ratio as percentage."""
        if self.size_before == 0:
            return 0.0
        return (1 - self.size_after / self.size_before) * 100

    def __str__(self) -> str:
        """Human-readable statistics."""
        return (
            f"Conversion Statistics:\n"
            f"  Total files: {self.total_files}\n"
            f"  Processed: {self.processed_files}\n"
            f"  Skipped: {self.skipped_files}\n"
            f"  Size before: {self.size_before:,} bytes\n"
            f"  Size after: {self.size_after:,} bytes\n"
            f"  Saved: {self.saved_bytes:,} bytes "
            f"({self.compression_ratio:.1f}% reduction)"
        )


class _Keys(object, metaclass=ReadOnlyClass):
    """Class containing constant keys for converter configuration."""

    MAX_SIZE: str = "__max_size__"
    QUALITY: str = "__quality__"
    STATS: str = "__stats__"
    TEST_MODE: str = "__test_mode__"


class Converter(BData):
    """Image converter class for resizing and compressing images.

    Processes images according to configuration:
    - Resizes images larger than max_size
    - Applies format-specific compression
    - Preserves file permissions
    """

    def __init__(self, max_size: int, quality: int, test_mode: bool = False) -> None:
        """Initialize Converter with configuration.

        ### Arguments:
        * max_size: int - Maximum size for longest image dimension.
        * quality: int - JPEG quality (1-100).
        * test_mode: bool - If True, analyze without modifying files.
        """
        self._set_data(key=_Keys.MAX_SIZE, value=max_size, set_default_type=int)
        self._set_data(key=_Keys.QUALITY, value=quality, set_default_type=int)
        self._set_data(
            key=_Keys.STATS, value=ConversionStats(), set_default_type=ConversionStats
        )
        self._set_data(key=_Keys.TEST_MODE, value=test_mode, set_default_type=bool)

    @property
    def max_size(self) -> int:
        """Get maximum image size."""
        tmp: Optional[int] = self._get_data(key=_Keys.MAX_SIZE)
        if tmp is None:
            raise Raise.error(
                message="Maximum size is not set in converter.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def quality(self) -> int:
        """Get JPEG quality setting."""
        tmp: Optional[int] = self._get_data(key=_Keys.QUALITY)
        if tmp is None:
            raise Raise.error(
                message="Quality is not set in converter.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def stats(self) -> ConversionStats:
        """Get conversion statistics."""
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

    def convert(self, image_info: ImageFileInfo) -> bool:
        """Convert and compress image file.

        Checks file accessibility, resizes if needed, applies compression
        based on format, and preserves original permissions.

        ### Arguments:
        * image_info: ImageFileInfo - Image file metadata and path.

        ### Returns:
        bool - True if file was processed, False if skipped.

        ### Raises:
        * PermissionError: If file is not readable/writable.
        * OSError: If file operations fail.
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
            # Open and check image
            with Image.open(file_path) as im:
                original_format = im.format
                original_width, original_height = im.size
                max_dimension = max(original_width, original_height)

                # Check if resize is needed
                if max_dimension <= self.max_size:
                    self.stats.add_skipped()
                    return False

                # Calculate new dimensions
                if original_width > original_height:
                    new_width = self.max_size
                    new_height = int(original_height * self.max_size / original_width)
                else:
                    new_height = self.max_size
                    new_width = int(original_width * self.max_size / original_height)

                # Resize image
                resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Save to temporary file first
                with tempfile.NamedTemporaryFile(
                    mode="wb", suffix=file_path.suffix, delete=False
                ) as tmp_file:
                    tmp_path = Path(tmp_file.name)

                try:
                    # Apply format-specific compression
                    if original_format in ("JPEG", "JPG"):
                        resized.save(
                            tmp_path, format="JPEG", quality=self.quality, optimize=True
                        )
                    elif original_format == "PNG":
                        resized.save(
                            tmp_path,
                            format="PNG",
                            compress_level=9,
                            optimize=True,
                            interlace=True,
                        )
                    else:
                        # Other formats: save without specific compression
                        resized.save(tmp_path, format=original_format)

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
                            import pwd
                            import grp

                            uid = pwd.getpwnam(image_info.owner).pw_uid
                            gid = grp.getgrnam(image_info.group).gr_gid
                            os.chown(file_path, uid, gid)
                        except (KeyError, PermissionError):
                            # Cannot restore ownership, skip
                            pass
                    else:
                        # Test mode: clean up temporary file
                        tmp_path.unlink()

                    # Update statistics
                    self.stats.add_processed(size_before, size_after)
                    return True

                except Exception:
                    # Clean up temporary file on error
                    if tmp_path.exists():
                        tmp_path.unlink()
                    raise

        except Exception as e:
            raise Raise.error(
                message=f"Failed to convert image {file_path}: {e}",
                exception=type(e),
                class_name=self._c_name,
                currentframe=currentframe(),
            )

    def print_report(self) -> None:
        """Print conversion statistics report."""
        print("\n" + "=" * 60)
        print(str(self.stats))
        print("=" * 60)


# #[EOF]#######################################################################
