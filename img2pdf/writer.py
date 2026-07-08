"""Small PDF object writer used by the converter."""

from __future__ import annotations


def pdf_text(value: str) -> bytes:
    if all(ord(char) < 128 for char in value):
        escaped = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return f"({escaped})".encode("ascii")
    return b"<FEFF" + value.encode("utf-16-be").hex().upper().encode("ascii") + b">"


class PdfWriter:
    def __init__(self) -> None:
        self.objects: list[bytes] = []

    def add(self, data: bytes) -> int:
        self.objects.append(data)
        return len(self.objects)

    def build(self, root_id: int, info_id: int | None = None) -> bytes:
        output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]

        for object_id, data in enumerate(self.objects, start=1):
            offsets.append(len(output))
            output.extend(f"{object_id} 0 obj\n".encode("ascii"))
            output.extend(data)
            output.extend(b"\nendobj\n")

        xref_position = len(output)
        output.extend(f"xref\n0 {len(self.objects) + 1}\n".encode("ascii"))
        output.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

        trailer = f"<< /Size {len(self.objects) + 1} /Root {root_id} 0 R"
        if info_id is not None:
            trailer += f" /Info {info_id} 0 R"
        trailer += " >>"
        output.extend(
            (
                "trailer\n"
                f"{trailer}\n"
                "startxref\n"
                f"{xref_position}\n"
                "%%EOF\n"
            ).encode("ascii")
        )
        return bytes(output)
