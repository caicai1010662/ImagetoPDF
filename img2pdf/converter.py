"""High-level image-to-PDF conversion workflow."""

from __future__ import annotations

from pathlib import Path
import tempfile

from img2pdf.files import VALID_ROTATIONS, exif_rotation, image_info
from img2pdf.encoder import make_image_stream
from img2pdf.writer import PdfWriter, pdf_text


MetaEntry = tuple[int, int, str, int | None]


def make_pdf(
    images: list[Path],
    output_path: Path,
    title: str,
    rotate: int = 0,
    auto_orient: bool = False,
    page_rotations: list[int] | None = None,
    meta: list[MetaEntry] | None = None,
) -> tuple[int, list[str]]:
    if page_rotations is not None:
        if len(page_rotations) != len(images):
            raise ValueError("Page rotation count must match image count.")
        invalid = [r for r in page_rotations if r not in VALID_ROTATIONS]
        if invalid:
            raise ValueError(f"Unsupported page rotation value: {invalid[0]}")

    writer = PdfWriter()
    page_ids: list[int] = []
    pending_pages: list[tuple[int, bytes]] = []
    skipped: list[str] = []

    for index, image_path in enumerate(images, start=1):
        try:
            entry = meta[index - 1] if meta else None
            if entry is not None:
                _, _, _, orientation = entry
            else:
                _, _, _, orientation = image_info(image_path)

            if page_rotations is not None:
                page_rotate = page_rotations[index - 1]
            else:
                page_rotate = exif_rotation(orientation) if auto_orient else rotate

            width, height, image_dictionary, image_bytes = make_image_stream(image_path, meta=entry)
        except Exception:
            skipped.append(image_path.name)
            continue

        image_id = writer.add(
            b"<< "
            + image_dictionary.encode("ascii")
            + b" >>\nstream\n"
            + image_bytes
            + b"\nendstream"
        )

        content = f"q\n{width} 0 0 {height} 0 0 cm\n/Im{index} Do\nQ\n".encode(
            "ascii"
        )
        content_id = writer.add(
            f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
            + content
            + b"endstream"
        )

        page_id = len(writer.objects) + 1
        page_ids.append(page_id)
        pending_pages.append(
            (
                page_id,
                (
                    f"<< /Type /Page /Parent {{pages_id}} 0 R "
                    f"/MediaBox [0 0 {width} {height}] "
                    f"/Rotate {page_rotate} "
                    f"/Resources << /XObject << /Im{index} {image_id} 0 R >> >> "
                    f"/Contents {content_id} 0 R >>"
                ).encode("ascii"),
            )
        )
        writer.add(b"")

    if not page_ids:
        raise ValueError("所有图片均无法处理，PDF 未生成。")

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pages_id = len(writer.objects) + 1
    pages_id = writer.add(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
    )

    for page_id, page_data in pending_pages:
        writer.objects[page_id - 1] = page_data.replace(
            b"{pages_id}", str(pages_id).encode("ascii")
        )

    info_id = writer.add(
        b"<< /Title "
        + pdf_text(title)
        + b" /Producer (IMGtoPDF lossless converter) >>"
    )
    root_id = writer.add(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_bytes = writer.build(root_id, info_id)
    with tempfile.NamedTemporaryFile(
        "wb",
        delete=False,
        dir=output_path.parent,
        prefix=f".{output_path.name}.",
        suffix=".tmp",
    ) as temp_file:
        temp_file.write(pdf_bytes)
        temp_path = Path(temp_file.name)
    try:
        temp_path.replace(output_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return len(page_ids), skipped
