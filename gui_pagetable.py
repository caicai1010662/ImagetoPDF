"""Page list table with reorder/remove controls."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

MetaEntry = tuple[int, int, str, int | None]


class PageTable(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        on_select: callable | None = None,
        on_reorder: callable | None = None,
        on_remove: callable | None = None,
    ) -> None:
        super().__init__(parent, style="Panel.TFrame")
        self._on_select = on_select
        self._on_reorder = on_reorder
        self._on_remove = on_remove

        self._images: list[Path] = []
        self._rotations: list[int] = []
        self._meta: list[MetaEntry] = []
        self.current_index = 0
        self.stats_var = tk.StringVar(value="0 页")

        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        row = ttk.Frame(self, style="Panel.TFrame")
        row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        row.columnconfigure(0, weight=1)
        ttk.Label(row, text="页面列表", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(row, textvariable=self.stats_var, style="Muted.TLabel").grid(row=0, column=1, sticky="e")

        table_frame = ttk.Frame(self, style="Panel.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self._tree = ttk.Treeview(
            table_frame,
            columns=("file", "rotate", "size"),
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("file", text="文件名")
        self._tree.heading("rotate", text="旋转")
        self._tree.heading("size", text="尺寸")
        self._tree.column("file", width=132, stretch=True)
        self._tree.column("rotate", width=52, anchor="center", stretch=False)
        self._tree.column("size", width=96, minwidth=70, anchor="center", stretch=True)
        self._tree.grid(row=0, column=0, sticky="nsew")
        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 0))
        self._tree.configure(yscrollcommand=scrollbar.set)

        manage = ttk.Frame(self, style="Panel.TFrame")
        manage.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        manage.columnconfigure((0, 1), weight=1)
        ttk.Button(
            manage, text="上移", style="Ghost.TButton",
            command=lambda: self._emit_reorder(-1),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(
            manage, text="下移", style="Ghost.TButton",
            command=lambda: self._emit_reorder(1),
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ttk.Button(
            manage, text="从本次导出移除", style="Ghost.TButton",
            command=self._emit_remove,
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def load(
        self, images: list[Path], rotations: list[int],
        meta: list[MetaEntry] | None = None,
    ) -> None:
        self._images = images
        self._rotations = rotations
        self._meta = meta or []
        self.current_index = 0
        self._rebuild()

    def refresh(self, images: list[Path], rotations: list[int]) -> None:
        self._images = images
        self._rotations = rotations
        self.current_index = max(0, min(self.current_index, len(self._images) - 1))
        self._rebuild()
        self._select_current()

    def select(self, index: int) -> None:
        self.current_index = index
        self._select_current()

    def _page_values(self, index: int) -> tuple[str, str, str]:
        path = self._images[index]
        if index < len(self._meta):
            width, height = self._meta[index][0], self._meta[index][1]
            size = f"{width}x{height}"
        else:
            size = "未知"
        return (path.name, str(self._rotations[index]), size)

    def _rebuild(self) -> None:
        self._tree.delete(*self._tree.get_children())
        max_size_len = 0
        for index in range(len(self._images)):
            values = self._page_values(index)
            self._tree.insert("", "end", iid=str(index), values=values)
            max_size_len = max(max_size_len, len(values[2]))
        size_width = max(80, max_size_len * 14 + 24)
        self._tree.column("size", width=size_width)
        self.stats_var.set(f"{len(self._images)} 页")

    def _select_current(self) -> None:
        if not self._images:
            return
        iid = str(self.current_index)
        self._tree.selection_set(iid)
        self._tree.focus(iid)
        self._tree.see(iid)

    def _on_tree_select(self, _event: tk.Event) -> None:
        selection = self._tree.selection()
        if selection:
            self.current_index = int(selection[0])
            if self._on_select is not None:
                self._on_select(self.current_index)

    def _emit_reorder(self, delta: int) -> None:
        if self._on_reorder is not None:
            self._on_reorder(delta)

    def _emit_remove(self) -> None:
        if self._on_remove is not None:
            self._on_remove()
