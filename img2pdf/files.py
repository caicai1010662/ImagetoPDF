"""Image file discovery, sorting, and metadata extraction."""

from __future__ import annotations

from pathlib import Path
import re

from PIL import Image


VALID_ROTATIONS = (0, 90, 180, 270)

JPEG_SUFFIXES = {".jpg", ".jpeg"}
SUPPORTED_SUFFIXES = JPEG_SUFFIXES | {
    ".png",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".webp",
}


def natural_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.stem)
    return [int(part) if part.isdigit() else part.casefold() for part in parts]


def collect_images(source: Path) -> list[Path]:
    if not source.exists():
        raise ValueError(f"Source path does not exist: {source}")

    if source.is_file():
        if source.suffix.casefold() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported image file: {source}")
        images = [source]
    else:
        images = [
            item
            for item in source.iterdir()
            if item.is_file() and item.suffix.casefold() in SUPPORTED_SUFFIXES
        ]

    images = sorted(images, key=natural_key)
    if not images:
        raise ValueError(f"No supported image files found in {source}")
    return images


def image_info(path: Path) -> tuple[int, int, str, int | None]:
    with Image.open(path) as image:
        exif = image.getexif()
        orientation = exif.get(274) if exif else None
        width, height = image.size
        mode = image.mode
        image.load()

    if mode == "L":
        color_space = "/DeviceGray"
    elif mode == "CMYK":
        color_space = "/DeviceCMYK"
    else:
        color_space = "/DeviceRGB"

    return width, height, color_space, orientation


def exif_rotation(orientation: int | None) -> int:
    return {
        3: 180,
        6: 90,
        8: 270,
    }.get(orientation, 0)
