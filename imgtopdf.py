#!/usr/bin/env python
"""Command-line entry point for image-to-PDF conversion."""

from __future__ import annotations

import argparse
from pathlib import Path

from img2pdf.converter import make_pdf
from img2pdf.files import VALID_ROTATIONS, collect_images


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert images to a lightweight lossless PDF."
    )
    parser.add_argument("source", type=Path, help="Image file or folder to convert")
    parser.add_argument("output", type=Path, help="Output PDF path")
    parser.add_argument(
        "--title",
        default=None,
        help="PDF title metadata. Defaults to the source folder or file name.",
    )
    parser.add_argument(
        "--rotate",
        type=int,
        choices=VALID_ROTATIONS,
        default=0,
        help="Display rotation for every PDF page.",
    )
    parser.add_argument(
        "--auto-orient",
        action="store_true",
        help="Use each image's EXIF orientation for PDF display rotation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    title = args.title or source.stem

    images = collect_images(source)
    success, skipped = make_pdf(images, output, title, args.rotate, args.auto_orient)
    print(f"Converted {success} image(s) to: {output}")
    if skipped:
        print(f"Warning: {len(skipped)} image(s) skipped: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
