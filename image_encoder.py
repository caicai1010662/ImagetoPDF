"""PDF image stream encoder — produces lossless image XObject data."""

from __future__ import annotations

from pathlib import Path
import zlib

from PIL import Image

from image_files import JPEG_SUFFIXES, image_info


def make_image_stream(
    path: Path,
    meta: tuple[int, int, str, int | None] | None = None,
) -> tuple[int, int, str, bytes]:
    suffix = path.suffix.casefold()
    if suffix in JPEG_SUFFIXES:
        if meta is not None:
            width, height, color_space = meta[0], meta[1], meta[2]
        else:
            width, height, color_space, _orientation = image_info(path)
        image_bytes = path.read_bytes()
        dictionary = (
            f"/Type /XObject /Subtype /Image /Width {width} /Height {height} "
            f"/ColorSpace {color_space} /BitsPerComponent 8 /Filter /DCTDecode "
            f"/Length {len(image_bytes)}"
        )
        return width, height, dictionary, image_bytes

    with Image.open(path) as image:
        image.seek(0)
        if image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        ):
            rgba = image.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            background.alpha_composite(rgba)
            converted = background.convert("RGB")
        elif image.mode == "L":
            converted = image.copy()
        else:
            converted = image.convert("RGB")

        width, height = converted.size
        color_space = "/DeviceGray" if converted.mode == "L" else "/DeviceRGB"
        pixel_bytes = converted.tobytes()

    compressed = zlib.compress(pixel_bytes, level=9)
    dictionary = (
        f"/Type /XObject /Subtype /Image /Width {width} /Height {height} "
        f"/ColorSpace {color_space} /BitsPerComponent 8 /Filter /FlateDecode "
        f"/Length {len(compressed)}"
    )
    return width, height, dictionary, compressed
