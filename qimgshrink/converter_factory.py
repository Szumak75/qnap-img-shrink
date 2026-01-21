# -*- coding: utf-8 -*-
"""
converter_factory.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026

Purpose: Factory for creating appropriate converter implementation.
"""

from typing import Union

from qimgshrink.converter import Converter
from qimgshrink.converter2 import Converter2


def create_converter(
    max_size: int,
    quality: int,
    test_mode: bool = False,
    prefer_imagemagick: bool = False,
) -> Union[Converter, Converter2]:
    """Create appropriate converter implementation.

    Tries to create Converter2 (ImageMagick) first if preferred or if
    Converter (Pillow) is not available. Falls back to the other
    implementation if the first choice fails.

    ### Arguments:
    * max_size: int - Maximum dimension for image longest side.
    * quality: int - JPEG quality (1-100).
    * test_mode: bool - If True, analyze without modifying files.
    * prefer_imagemagick: bool - If True, prefer ImageMagick over Pillow.

    ### Returns:
    Union[Converter, Converter2] - Converter instance.

    ### Raises:
    * RuntimeError: If neither implementation is available.

    ### Examples:
    ```python
    >>> converter = create_converter(1920, 85)
    >>> converter = create_converter(1920, 85, prefer_imagemagick=True)
    ```
    """
    errors = []

    # Determine order of attempts
    if prefer_imagemagick:
        first_choice = ("ImageMagick", Converter2)
        second_choice = ("Pillow", Converter)
    else:
        first_choice = ("Pillow", Converter)
        second_choice = ("ImageMagick", Converter2)

    # Try first choice
    try:
        converter = first_choice[1](max_size, quality, test_mode)
        print(f"Using {first_choice[0]}-based converter")
        return converter
    except (ImportError, RuntimeError) as e:
        errors.append(f"{first_choice[0]}: {e}")

    # Try second choice
    try:
        converter = second_choice[1](max_size, quality, test_mode)
        print(f"Using {second_choice[0]}-based converter (fallback)")
        return converter
    except (ImportError, RuntimeError) as e:
        errors.append(f"{second_choice[0]}: {e}")

    # Both failed
    error_msg = "No converter implementation available. Errors:\n"
    error_msg += "\n".join(f"  - {err}" for err in errors)
    raise RuntimeError(error_msg)


# #[EOF]#######################################################################
