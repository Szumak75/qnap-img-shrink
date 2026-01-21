# -*- coding: utf-8 -*-
"""
main.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 21.01.2026, 09:39:51

Purpose: Main application module for qimgshrink.
"""

import argparse
from inspect import currentframe
import sys
from pathlib import Path
from typing import List, Optional

import yaml

from jsktoolbox.basetool import BData
from jsktoolbox.raisetool import Raise
from jsktoolbox.attribtool import ReadOnlyClass, NoDynamicAttributes

from qimgshrink.files import FileFind, ImageFileInfo
from qimgshrink.converter import Converter


class _Keys(object, metaclass=ReadOnlyClass):
    """Class containing constant keys for configuration."""

    # Configuration keys
    WRK_DIR: str = "__wrk_dir__"
    MAX_SIZE: str = "__max_size__"
    QUALITY: str = "__quality__"
    TEST_MODE: str = "__test_mode__"

    # Application keys
    CONFIG: str = "__config__"


class Config(BData):
    """Configuration class for qimgshrink application."""

    def __init__(self) -> None:

        self._set_data(key=_Keys.WRK_DIR, value="/tmp", set_default_type=str)
        self._set_data(key=_Keys.MAX_SIZE, value=1920, set_default_type=int)
        self._set_data(key=_Keys.QUALITY, value=97, set_default_type=int)

    @property
    def wrk_dir(self) -> str:
        """Get the working directory."""
        tmp: Optional[str] = self._get_data(key=_Keys.WRK_DIR)
        if tmp is None:
            raise Raise.error(
                message="Working directory is not set in configuration.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        return tmp

    @wrk_dir.setter
    def wrk_dir(self, value: str) -> None:
        """Set the working directory."""
        self._set_data(key=_Keys.WRK_DIR, value=value)

    @property
    def max_size(self) -> int:
        """Get the maximum image size."""
        tmp: Optional[int] = self._get_data(key=_Keys.MAX_SIZE)
        if tmp is None:
            raise Raise.error(
                message="Maximum size is not set in configuration.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        return tmp

    @max_size.setter
    def max_size(self, value: int) -> None:
        """Set the maximum image size."""
        self._set_data(key=_Keys.MAX_SIZE, value=value)

    @property
    def quality(self) -> int:
        """Get the image quality."""
        tmp: Optional[int] = self._get_data(key=_Keys.QUALITY)
        if tmp is None:
            raise Raise.error(
                message="Quality is not set in configuration.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        return tmp

    @quality.setter
    def quality(self, value: int) -> None:
        """Set the image quality."""
        self._set_data(key=_Keys.QUALITY, value=value)

    @property
    def test_mode(self) -> bool:
        """Get test mode flag.

        ### Returns:
        bool - True if in test mode (no file modifications).
        """
        tmp: Optional[bool] = self._get_data(key=_Keys.TEST_MODE)
        if tmp is None:
            return False
        return tmp

    @test_mode.setter
    def test_mode(self, value: bool) -> None:
        """Set test mode flag.

        ### Arguments:
        * value: bool - True to enable test mode.
        """
        self._set_data(key=_Keys.TEST_MODE, value=value)

    def load_from_file(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from YAML file.

        If file doesn't exist or specific variables are missing,
        default values are preserved.

        ### Arguments:
        * config_path: Optional[Path] - Path to configuration file.
                                       If None, uses default path: etc/config.yaml

        ### Raises:
        * yaml.YAMLError: If the configuration file is not valid YAML.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "etc" / "config.yaml"

        if not config_path.exists():
            return

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                config_data = yaml.safe_load(file)

            if config_data is None:
                return

            if "wrk_dir" in config_data and isinstance(config_data["wrk_dir"], str):
                self.wrk_dir = config_data["wrk_dir"]

            if "max_size" in config_data and isinstance(config_data["max_size"], int):
                self.max_size = config_data["max_size"]

            if "quality" in config_data and isinstance(config_data["quality"], int):
                self.quality = config_data["quality"]

        except yaml.YAMLError as exc:
            raise Raise.error(
                message=f"Failed to parse configuration file: {exc}",
                exception=yaml.YAMLError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )


class App(BData):
    """Main application class for qimgshrink."""

    def __init__(self) -> None:
        self._set_data(key=_Keys.CONFIG, value=Config(), set_default_type=Config)

    @property
    def config(self) -> Config:
        """Get the configuration object."""
        tmp: Optional[Config] = self._get_data(key=_Keys.CONFIG)
        if tmp is None:
            raise Raise.error(
                message="Configuration is not set in application.",
                exception=ValueError,
                class_name=self._c_name,
                currentframe=currentframe(),
            )

        return tmp

    def run(self) -> None:
        """Run the main application logic."""
        self.config.load_from_file()

        # Show mode
        if self.config.test_mode:
            print("\n*** TEST MODE ENABLED - No files will be modified ***\n")

        # Find all images
        finder = FileFind(self.config.wrk_dir)
        images = finder.find_images()

        if not images:
            print("No images found to process.")
            return

        print(f"Found {len(images)} image(s) to process...")

        # Initialize converter
        converter = Converter(
            max_size=self.config.max_size,
            quality=self.config.quality,
            test_mode=self.config.test_mode,
        )

        # Process each image
        for img_info in images:
            try:
                was_processed = converter.convert(img_info)
                if was_processed:
                    action = "Would process" if self.config.test_mode else "Processed"
                    print(f"  ✓ {action}: {img_info.path}")
                else:
                    print(f"  - Skipped (no resize needed): {img_info.path}")
            except PermissionError:
                print(f"  ✗ Permission denied: {img_info.path}")
            except Exception as e:
                print(f"  ✗ Error: {img_info.path} - {e}")

        # Print final report
        converter.print_report()


def main() -> int:
    """Main entry point with CLI argument parsing.

    ### Returns:
    int - Exit code (0 for success).
    """
    parser = argparse.ArgumentParser(
        description="QNAP Image Shrink - Resize and compress images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              Process images normally
  %(prog)s -t           Test mode (no modifications)
        """,
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Test mode - analyze files without modifying them",
    )

    args = parser.parse_args()

    # Create and configure application
    app = App()
    app.config.test_mode = args.test

    # Run
    app.run()

    return 0


# #[EOF]#######################################################################

if __name__ == "__main__":
    sys.exit(main())
