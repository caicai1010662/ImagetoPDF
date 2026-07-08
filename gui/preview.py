"""Preview panel with canvas rendering and page navigation."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from gui.theme import CANVAS_BG, LINE, MUTED, SHADOW


class PreviewPanel(ttk.Frame):
    def __init__(self, parent: ttk.Frame, on_move: callable | None = None) -> None:
        super().__init__(parent, style="Panel.TFrame", padding=12)
        self._on_move = on_move
        self._images: list[Path] = []
        self._rotations: list[int] = []
        self._current_index = 0
        self._preview_image: ImageTk.PhotoImage | None = None
        self._redraw_after_id: str | None = None
        self._decoded_cache: dict[Path, Image.Image] = {}

        self.page_var = tk.StringVar(value="未选择页面")

        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self, style="Panel.TFrame")
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(0, weight=1)
        toolbar.columnconfigure((1, 2), weight=0, uniform="nav")

        ttk.Label(toolbar, textvariable=self.page_var, style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(
            toolbar, text="上一页", style="Ghost.TButton",
            command=lambda: self._move(-1),
        ).grid(row=0, column=1, sticky="ew", padx=(8, 4))
        ttk.Button(
            toolbar, text="下一页", style="Ghost.TButton",
            command=lambda: self._move(1),
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        canvas_frame = ttk.Frame(self, style="Panel.TFrame")
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame, bg=CANVAS_BG, highlightthickness=1, highlightbackground=LINE,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def load(self, images: list[Path], rotations: list[int], current_index: int) -> None:
        self._images = images
        self._rotations = rotations
        self._current_index = current_index
        self._draw()

    def _on_canvas_resize(self, _event: tk.Event) -> None:
        if self._redraw_after_id is not None:
            self.after_cancel(self._redraw_after_id)
        self._redraw_after_id = self.after(50, self._draw)

    def _move(self, delta: int) -> None:
        if self._on_move is not None:
            self._on_move(delta)

    def _draw(self) -> None:
        self.canvas.delete("all")

        if not self._images:
            self.page_var.set("未选择页面")
            self.canvas.create_text(
                max(self.canvas.winfo_width(), 320) // 2,
                max(self.canvas.winfo_height(), 320) // 2,
                text='请通过"文件加载"选择图片',
                fill=MUTED,
                font=("Microsoft YaHei", 15),
            )
            return

        path = self._images[self._current_index]
        rotation = self._rotations[self._current_index]
        self.page_var.set(
            f"第 {self._current_index + 1} / {len(self._images)} 页 - {path.name} - 旋转 {rotation}°"
        )

        cache_key = path
        if cache_key in self._decoded_cache:
            preview = self._decoded_cache[cache_key].copy()
        else:
            try:
                with Image.open(path) as image:
                    decoded = image.convert("RGB").rotate(-rotation, expand=True)
            except Exception:
                self.canvas.create_text(
                    max(self.canvas.winfo_width(), 320) // 2,
                    max(self.canvas.winfo_height(), 320) // 2,
                    text=f"无法预览：{path.name}",
                    fill=MUTED,
                    font=("Microsoft YaHei", 15),
                )
                return
            if len(self._decoded_cache) >= 3:
                oldest = next(iter(self._decoded_cache))
                del self._decoded_cache[oldest]
            self._decoded_cache[cache_key] = decoded
            preview = decoded.copy()

        canvas_width = max(self.canvas.winfo_width(), 360)
        canvas_height = max(self.canvas.winfo_height(), 360)
        max_width = max(canvas_width - 46, 1)
        max_height = max(canvas_height - 46, 1)
        ratio = min(max_width / preview.width, max_height / preview.height)
        target = (max(1, int(preview.width * ratio)), max(1, int(preview.height * ratio)))
        preview = preview.resize(target, Image.Resampling.LANCZOS)

        self._preview_image = ImageTk.PhotoImage(preview)
        x = canvas_width // 2
        y = canvas_height // 2
        shadow_offset = 6

        self.canvas.create_rectangle(
            x - preview.width // 2 + shadow_offset,
            y - preview.height // 2 + shadow_offset,
            x + preview.width // 2 + shadow_offset,
            y + preview.height // 2 + shadow_offset,
            fill=SHADOW,
            outline="",
        )
        self.canvas.create_rectangle(
            x - preview.width // 2 - 1,
            y - preview.height // 2 - 1,
            x + preview.width // 2 + 1,
            y + preview.height // 2 + 1,
            fill="#ffffff",
            outline=LINE,
        )
        self.canvas.create_image(x, y, image=self._preview_image)
