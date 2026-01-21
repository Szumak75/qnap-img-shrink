# -*- coding: utf-8 -*-
"""
converter.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026, 10:41:28

Purpose:
"""

from typing import Optional
import PIL.Image as img
from jsktoolbox.basetool import BData
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from inspect import currentframe


class _Keys(object, metaclass=ReadOnlyClass):
    """Class containing constant keys for converter configuration."""

    MAX_SIZE: str = "__max_size__"
    QUALITY: str = "__quality__"


class Converter(BData):
    """Image converter class for resizing and compressing images."""

    def __init__(self, max_size: int, quality: int) -> None:
        self._set_data(key=_Keys.MAX_SIZE, value=max_size, set_default_type=int)
        self._set_data(key=_Keys.QUALITY, value=quality, set_default_type=int)

    @property
    def max_size(self) -> int:
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
        tmp: Optional[int] = self._get_data(key=_Keys.QUALITY)
        if tmp is None:
            raise Raise.error(
                message="Quality is not set in converter.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )
        return tmp

    def convert(self, input_path: str, output_path: str) -> None:
        """Convert the image at input_path and save it to output_path."""
        try:
            with img.open(input_path) as im:
                im.thumbnail((self.max_size, self.max_size))
                im.save(output_path, quality=self.quality)
        except Exception as e:
            raise Raise.error(
                message=f"Failed to convert image: {e}",
                exception=type(e),
                class_name=self._c_name,
                currentframe=currentframe(),
            )


# #[EOF]#######################################################################
