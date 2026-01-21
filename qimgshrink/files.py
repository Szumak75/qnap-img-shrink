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
import pwd
import grp

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise


class _ImageFileInfoKeys(object, metaclass=ReadOnlyClass):
    """Keys for ImageFileInfo data storage."""

    PATH: str = "__path__"
    PERMISSIONS: str = "__permissions__"
    OWNER: str = "__owner__"
    GROUP: str = "__group__"
    SIZE: str = "__size__"


class ImageFileInfo(BData):
    """Container class for image file metadata.

    Stores file path and metadata including permissions, owner, and group.
    """

    def __init__(
        self,
        path: str,
        permissions: int,
        owner: str,
        group: str,
        size: int,
    ) -> None:
        """Initialize ImageFileInfo with file metadata.

        ### Arguments:
        * path: str - Absolute path to the image file.
        * permissions: int - File permissions as octal integer (e.g., 0o644).
        * owner: str - File owner username.
        * group: str - File group name.
        * size: int - File size in bytes.
        """
        self._set_data(key=_ImageFileInfoKeys.PATH, value=path, set_default_type=str)
        self._set_data(
            key=_ImageFileInfoKeys.PERMISSIONS,
            value=permissions,
            set_default_type=int,
        )
        self._set_data(key=_ImageFileInfoKeys.OWNER, value=owner, set_default_type=str)
        self._set_data(key=_ImageFileInfoKeys.GROUP, value=group, set_default_type=str)
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
    def owner(self) -> str:
        """Get file owner username.

        ### Returns:
        str - Owner username.

        ### Raises:
        * ValueError: If owner is not set.
        """
        tmp: Optional[str] = self._get_data(key=_ImageFileInfoKeys.OWNER)
        if tmp is None:
            raise Raise.error(
                message="Owner is not set in ImageFileInfo.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    @property
    def group(self) -> str:
        """Get file group name.

        ### Returns:
        str - Group name.

        ### Raises:
        * ValueError: If group is not set.
        """
        tmp: Optional[str] = self._get_data(key=_ImageFileInfoKeys.GROUP)
        if tmp is None:
            raise Raise.error(
                message="Group is not set in ImageFileInfo.",
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
            f"owner={self.owner!r}, "
            f"group={self.group!r}, "
            f"size={self.size})"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"{self.path} ({self.owner}:{self.group}, "
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
                              and metadata (permissions, owner, group, size).

        ### Raises:
        * FileNotFoundError: If working directory does not exist.
        * PermissionError: If working directory is not accessible.

        ### Examples:
        ```python
        >>> finder = FileFind("/path/to/images")
        >>> images = finder.find_images()
        >>> for img in images:
        ...     print(f"{img.path}: {img.owner}:{img.group} {img.permissions_str}")
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

                        # Get owner and group names
                        try:
                            owner = pwd.getpwuid(stat_info.st_uid).pw_name
                        except KeyError:
                            owner = str(stat_info.st_uid)

                        try:
                            group = grp.getgrgid(stat_info.st_gid).gr_name
                        except KeyError:
                            group = str(stat_info.st_gid)

                        # Create ImageFileInfo object
                        img_info = ImageFileInfo(
                            path=str(file_path.absolute()),
                            permissions=stat_info.st_mode & 0o777,
                            owner=owner,
                            group=group,
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
