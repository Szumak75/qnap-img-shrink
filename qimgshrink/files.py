# -*- coding: utf-8 -*-
"""
files.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026, 10:41:02

Purpose: File scanning utilities for finding image files.
"""

from inspect import currentframe
from pathlib import Path
from typing import List, Optional

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise


class _ImageFileInfoKeys(object, metaclass=ReadOnlyClass):
    """Keys for ImageFileInfo data storage."""

    PATH: str = "__path__"
    PERMISSIONS: str = "__permissions__"
    UID: str = "__uid__"
    GID: str = "__gid__"
    SIZE: str = "__size__"


class ImageFileInfo(BData):
    """Container class for image file metadata.

    Stores file path and metadata including permissions, uid, and gid.
    """

    def __init__(
        self,
        path: str,
        permissions: int,
        uid: int,
        gid: int,
        size: int,
    ) -> None:
        """Initialize ImageFileInfo with file metadata.

        ### Arguments:
        * path: str - Absolute path to the image file.
        * permissions: int - File permissions as octal integer (e.g., 0o644).
        * uid: int - File owner user ID.
        * gid: int - File group ID.
        * size: int - File size in bytes.
        """
        self._set_data(key=_ImageFileInfoKeys.PATH, value=path, set_default_type=str)
        self._set_data(
            key=_ImageFileInfoKeys.PERMISSIONS,
            value=permissions,
            set_default_type=int,
        )
        self._set_data(key=_ImageFileInfoKeys.UID, value=uid, set_default_type=int)
        self._set_data(key=_ImageFileInfoKeys.GID, value=gid, set_default_type=int)
        self._set_data(key=_ImageFileInfoKeys.SIZE, value=size, set_default_type=int)

    @property
    def path(self) -> str:
        """Get file path.

        ### Returns:
        str - Absolute path to the file.

        ### Raises:
        * ValueError: If path is not set.
        """
        tmp: Optional[str] = self._get_data(key=_ImageFileInfoKeys.PATH)
        if tmp is None:
            raise Raise.error(
                message="Path is not set in ImageFileInfo.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def permissions(self) -> int:
        """Get file permissions as octal integer.

        ### Returns:
        int - File permissions.

        ### Raises:
        * ValueError: If permissions are not set.
        """
        tmp: Optional[int] = self._get_data(key=_ImageFileInfoKeys.PERMISSIONS)
        if tmp is None:
            raise Raise.error(
                message="Permissions are not set in ImageFileInfo.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def permissions_str(self) -> str:
        """Get file permissions as string (e.g., 'rw-r--r--')."""
        return oct(self.permissions)[-3:]

    @property
    def uid(self) -> int:
        """Get file owner user ID.

        ### Returns:
        int - Owner user ID.

        ### Raises:
        * ValueError: If uid is not set.
        """
        tmp: Optional[int] = self._get_data(key=_ImageFileInfoKeys.UID)
        if tmp is None:
            raise Raise.error(
                message="UID is not set in ImageFileInfo.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def gid(self) -> int:
        """Get file group ID.

        ### Returns:
        int - Group ID.

        ### Raises:
        * ValueError: If gid is not set.
        """
        tmp: Optional[int] = self._get_data(key=_ImageFileInfoKeys.GID)
        if tmp is None:
            raise Raise.error(
                message="GID is not set in ImageFileInfo.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def size(self) -> int:
        """Get file size in bytes.

        ### Returns:
        int - File size.

        ### Raises:
        * ValueError: If size is not set.
        """
        tmp: Optional[int] = self._get_data(key=_ImageFileInfoKeys.SIZE)
        if tmp is None:
            raise Raise.error(
                message="Size is not set in ImageFileInfo.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    def __repr__(self) -> str:
        """String representation of ImageFileInfo."""
        return (
            f"ImageFileInfo(path={self.path!r}, "
            f"permissions={oct(self.permissions)}, "
            f"uid={self.uid}, "
            f"gid={self.gid}, "
            f"size={self.size})"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"{self.path} (uid={self.uid}, gid={self.gid}, "
            f"{self.permissions_str}, {self.size} bytes)"
        )


class _Keys(object, metaclass=ReadOnlyClass):
    """Class containing constant keys for file configuration."""

    WRK_DIR: str = "__wrk_dir__"


class FileFind(BData):
    """Class for finding image files in directory structure.

    Scans the specified working directory and its subdirectories
    for image files with extensions: jpg, jpeg, bmp, tiff, tif, png.
    """

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".png"}

    def __init__(self, wrk_dir: str) -> None:
        """Initialize FileFind with working directory.

        ### Arguments:
        * wrk_dir: str - Directory path to scan for image files.
        """
        self._set_data(key=_Keys.WRK_DIR, value=wrk_dir, set_default_type=str)

    @property
    def wrk_dir(self) -> str:
        """Get the working directory path.

        ### Returns:
        str - The working directory path.

        ### Raises:
        * ValueError: If working directory is not set.
        """
        tmp: Optional[str] = self._get_data(key=_Keys.WRK_DIR)
        if tmp is None:
            raise Raise.error(
                message="Working directory is not set in file configuration.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    def find_images(self) -> List[ImageFileInfo]:
        """Scan working directory for image files.

        Recursively searches the working directory and all subdirectories
        for files with supported image extensions (jpg, jpeg, bmp, tiff, tif, png).
        Case-insensitive extension matching.

        ### Returns:
        List[ImageFileInfo] - List of ImageFileInfo objects containing file paths
                              and metadata (permissions, uid, gid, size).

        ### Raises:
        * FileNotFoundError: If working directory does not exist.
        * PermissionError: If working directory is not accessible.

        ### Examples:
        ```python
        >>> finder = FileFind("/path/to/images")
        >>> images = finder.find_images()
        >>> for img in images:
        ...     print(f"{img.path}: uid={img.uid} gid={img.gid} {img.permissions_str}")
        ```
        """
        work_path = Path(self.wrk_dir)

        if not work_path.exists():
            raise Raise.error(
                message=f"Working directory does not exist: {self.wrk_dir}",
                exception=FileNotFoundError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        if not work_path.is_dir():
            raise Raise.error(
                message=f"Working directory is not a directory: {self.wrk_dir}",
                exception=NotADirectoryError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        image_files: List[ImageFileInfo] = []

        try:
            for file_path in work_path.rglob("*"):
                if file_path.is_file():
                    if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                        # Get file statistics
                        stat_info = file_path.stat()

                        # Create ImageFileInfo object
                        img_info = ImageFileInfo(
                            path=str(file_path.absolute()),
                            permissions=stat_info.st_mode & 0o777,
                            uid=stat_info.st_uid,
                            gid=stat_info.st_gid,
                            size=stat_info.st_size,
                        )
                        image_files.append(img_info)
        except PermissionError as exc:
            raise Raise.error(
                message=f"Permission denied while scanning directory: {exc}",
                exception=PermissionError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        # Sort by path
        return sorted(image_files, key=lambda x: x.path)


# #[EOF]#######################################################################
