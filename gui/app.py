#!/usr/bin/env python
"""中文友好的无损图片转 PDF 桌面界面。"""

from __future__ import annotations

from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from img2pdf.converter import make_pdf
from img2pdf.files import SUPPORTED_SUFFIXES, exif_rotation, image_info, natural_key
from gui.theme import BG, PANEL, configure_style
from gui.preview import PreviewPanel
from gui.pagetable import PageTable


class ImageToPdfApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("图片转 PDF 工具")
        self.geometry("1320x860")
        self.minsize(1120, 720)
        self.configure(bg=BG)

        self.images: list[Path] = []
        self.rotations: list[int] = []
        self.meta: list[tuple[int, int, str, int | None]] = []
        self.current_index = 0

        self.source_var = tk.StringVar(value="")
        self.output_var = tk.StringVar(
            value=str(Path.cwd() / "output" / "pdf" / "document.pdf")
        )
        self.status_var = tk.StringVar(value="准备就绪。")

        self.style = configure_style(self)
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_workspace()
        self._build_statusbar()

    def _build_workspace(self) -> None:
        workspace = ttk.Frame(self, style="App.TFrame", padding=14)
        workspace.grid(row=0, column=0, sticky="nsew")
        workspace.columnconfigure(0, weight=17, uniform="main")
        workspace.columnconfigure(1, weight=70, uniform="main")
        workspace.columnconfigure(2, weight=13, uniform="main")
        workspace.rowconfigure(0, weight=1)

        self._build_left_panel(workspace)
        self._build_center_panel(workspace)
        self._build_right_panel(workspace)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(3, weight=1)

        ttk.Label(panel, text="图片来源", style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(panel, textvariable=self.source_var).grid(
            row=1, column=0, sticky="ew", pady=(8, 6)
        )

        source_buttons = ttk.Frame(panel, style="Panel.TFrame")
        source_buttons.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        source_buttons.columnconfigure(0, weight=1)
        ttk.Button(
            source_buttons, text="文件加载", style="Ghost.TButton",
            command=self.choose_source,
        ).grid(row=0, column=0, sticky="ew")

        self.page_table = PageTable(
            panel,
            on_select=self._on_page_select,
            on_reorder=self._handle_reorder,
            on_remove=self._handle_remove,
        )
        self.page_table.grid(row=3, column=0, sticky="nsew")

    def _build_center_panel(self, parent: ttk.Frame) -> None:
        self.preview = PreviewPanel(parent, on_move=self._handle_move)
        self.preview.grid(row=0, column=1, sticky="nsew")

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        panel.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text="单页调整", style="Section.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        tools = ttk.Frame(panel, style="Panel.TFrame")
        tools.grid(row=1, column=0, sticky="ew", pady=(10, 14))
        tools.columnconfigure(0, weight=1)
        tools.rowconfigure((0, 1), weight=1, uniform="tool")
        ttk.Button(
            tools, text="左旋 90°", style="Ghost.TButton",
            command=lambda: self._rotate_current(-90),
        ).grid(row=0, column=0, sticky="ew")
        ttk.Button(
            tools, text="右旋 90°", style="Ghost.TButton",
            command=lambda: self._rotate_current(90),
        ).grid(row=1, column=0, sticky="ew", pady=(8, 0))

        ttk.Separator(panel, orient="horizontal").grid(
            row=2, column=0, sticky="ew", pady=(0, 14)
        )

        ttk.Label(panel, text="批量处理", style="Section.TLabel").grid(
            row=3, column=0, sticky="w"
        )
        batch = ttk.Frame(panel, style="Panel.TFrame")
        batch.grid(row=4, column=0, sticky="ew", pady=(10, 14))
        batch.columnconfigure(0, weight=1)
        batch.rowconfigure((0, 1), weight=1, uniform="batch")
        ttk.Button(
            batch, text="自动修正", style="Ghost.TButton",
            command=self._apply_auto_orient,
        ).grid(row=0, column=0, sticky="ew")
        ttk.Button(
            batch, text="全部归零", style="Ghost.TButton",
            command=self._reset_rotations,
        ).grid(row=1, column=0, sticky="ew", pady=(8, 0))

        ttk.Separator(panel, orient="horizontal").grid(
            row=5, column=0, sticky="ew", pady=(0, 14)
        )

        ttk.Label(panel, text="导出设置", style="Section.TLabel").grid(
            row=6, column=0, sticky="w"
        )
        output = ttk.Frame(panel, style="Panel.TFrame")
        output.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        output.columnconfigure(0, weight=1)
        ttk.Label(output, text="保存位置", style="Muted.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(output, textvariable=self.output_var).grid(
            row=1, column=0, sticky="ew", pady=(5, 8)
        )
        ttk.Button(
            output, text="选择保存位置", style="Ghost.TButton",
            command=self.choose_output,
        ).grid(row=2, column=0, sticky="ew", pady=(0, 8))
        ttk.Button(
            output, text="导出 PDF", style="Primary.TButton",
            command=self.export_pdf,
        ).grid(row=3, column=0, sticky="ew")

    def _build_statusbar(self) -> None:
        bar = ttk.Frame(self, style="StatusBar.TFrame", padding=(16, 6, 16, 6))
        bar.grid(row=1, column=0, sticky="ew")
        bar.columnconfigure(0, weight=1)
        ttk.Label(
            bar, textvariable=self.status_var, style="StatusBar.TLabel"
        ).grid(row=0, column=0, sticky="w")

    # -- source / output file dialogs --

    def choose_source(self) -> None:
        initial_dir = self._initial_image_dir()
        filenames = filedialog.askopenfilenames(
            title="选择图片文件",
            initialdir=initial_dir,
            filetypes=[
                ("支持的图片", "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff *.webp"),
                ("所有文件", "*.*"),
            ],
        )
        if filenames:
            self._load_images([Path(filename) for filename in filenames])

    def _initial_image_dir(self) -> str:
        if self.images:
            return str(self.images[0].parent)
        source = self.source_var.get()
        if source:
            path = Path(source)
            if path.exists() and path.is_dir():
                return str(path)
        candidate = Path.cwd() / "IMG"
        if candidate.exists():
            return str(candidate)
        return str(Path.cwd())

    def choose_output(self) -> None:
        initial = Path(self.output_var.get())
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF 文件", "*.pdf")],
            initialfile=initial.name,
            initialdir=str(initial.parent),
        )
        if filename:
            self.output_var.set(filename)

    # -- image loading --

    def _load_images(self, images: list[Path]) -> None:
        try:
            valid_images = [
                image
                for image in images
                if image.is_file() and image.suffix.casefold() in SUPPORTED_SUFFIXES
            ]
            if not valid_images:
                raise ValueError("请选择支持的图片文件。")
            self.images = sorted(valid_images, key=natural_key)
            self.meta = [image_info(path) for path in self.images]
            self.rotations = [exif_rotation(m[3]) for m in self.meta]
        except Exception as exc:
            messagebox.showerror("加载失败", str(exc))
            return

        self.current_index = 0
        source_folder = self.images[0].parent
        self.source_var.set(f"已选择 {len(self.images)} 张图片：{source_folder}")
        self.output_var.set(
            str(Path.cwd() / "output" / "pdf" / f"{source_folder.name}.pdf")
        )

        self.page_table.load(self.images, self.rotations, self.meta)
        self._refresh_preview()
        self.status_var.set(
            f"已加载 {len(self.images)} 张图片，并已自动设置旋转。"
        )
        self.update_idletasks()

    # -- callbacks from child widgets --

    def _on_page_select(self, index: int) -> None:
        self.current_index = index
        self._refresh_preview()

    def _handle_move(self, delta: int) -> None:
        if not self.images:
            return
        self.current_index = max(
            0, min(len(self.images) - 1, self.current_index + delta)
        )
        self.page_table.select(self.current_index)
        self._refresh_preview()

    def _handle_reorder(self, delta: int) -> None:
        if not self.images:
            return
        new_index = self.current_index + delta
        if new_index < 0 or new_index >= len(self.images):
            return
        self.images[self.current_index], self.images[new_index] = (
            self.images[new_index],
            self.images[self.current_index],
        )
        self.rotations[self.current_index], self.rotations[new_index] = (
            self.rotations[new_index],
            self.rotations[self.current_index],
        )
        self.current_index = new_index
        self.page_table.refresh(self.images, self.rotations)
        self.page_table.select(self.current_index)
        self._refresh_preview()
        self.status_var.set("页面顺序已更新。")

    def _handle_remove(self) -> None:
        if not self.images:
            return
        if not messagebox.askyesno(
            "确认移除",
            "仅从本次 PDF 导出中移除当前页面，原始图片文件不会被删除。是否继续？",
        ):
            return
        removed = self.images.pop(self.current_index)
        self.rotations.pop(self.current_index)
        if self.current_index >= len(self.images):
            self.current_index = max(len(self.images) - 1, 0)
        self.page_table.refresh(self.images, self.rotations)
        self.page_table.select(self.current_index)
        self._refresh_preview()
        self.status_var.set(f"已从本次导出移除 {removed.name}，原始图片未改动。")

    # -- rotation tools --

    def _rotate_current(self, delta: int) -> None:
        if not self.images:
            return
        self.rotations[self.current_index] = (
            self.rotations[self.current_index] + delta
        ) % 360
        self.page_table.refresh(self.images, self.rotations)
        self.page_table.select(self.current_index)
        self._refresh_preview()
        self.status_var.set(
            f"第 {self.current_index + 1} 页旋转角度已设为 {self.rotations[self.current_index]}°。"
        )

    def _apply_auto_orient(self) -> None:
        if not self.images:
            return
        self.rotations = [exif_rotation(m[3]) for m in self.meta]
        self.page_table.refresh(self.images, self.rotations)
        self.page_table.select(self.current_index)
        self._refresh_preview()
        self.status_var.set("已按照片 EXIF 方向修正全部页面。")

    def _reset_rotations(self) -> None:
        if not self.images:
            return
        self.rotations = [0 for _path in self.images]
        self.page_table.refresh(self.images, self.rotations)
        self.page_table.select(self.current_index)
        self._refresh_preview()
        self.status_var.set("全部页面旋转角度已重置为 0°。")

    # -- preview sync --

    def _refresh_preview(self) -> None:
        self.preview.load(self.images, self.rotations, self.current_index)

    # -- export --

    def export_pdf(self) -> None:
        if not self.images:
            messagebox.showwarning("无法导出", "请先加载图片。")
            return

        output = Path(self.output_var.get())
        if output.suffix.casefold() != ".pdf":
            output = output.with_suffix(".pdf")
            self.output_var.set(str(output))
        if output.exists() and not messagebox.askyesno(
            "确认覆盖",
            f"文件已存在：\n{output}\n\n是否覆盖它？",
        ):
            self.status_var.set("已取消导出。")
            return
        self.status_var.set(f"正在导出 {len(self.images)} 页…")
        self.update_idletasks()
        try:
            success, skipped = make_pdf(
                self.images, output, output.stem,
                page_rotations=self.rotations, meta=self.meta,
            )
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc))
            self.status_var.set("导出失败。")
            return

        self.status_var.set(f"已导出 {success} 页：{output}")
        if skipped:
            names = "\n".join(skipped[:5])
            more = f"\n…等共 {len(skipped)} 张" if len(skipped) > 5 else ""
            messagebox.showwarning("部分跳过", f"以下图片无法处理：\n{names}{more}\n\n其余 {success} 页已成功导出。")
        else:
            messagebox.showinfo("导出完成", f"PDF 已保存：\n{output}")


def _init_high_dpi() -> None:
    """Declare per-monitor DPI awareness so Tk renders sharply on HiDPI displays."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main() -> None:
    _init_high_dpi()
    app = ImageToPdfApp()
    app.mainloop()


if __name__ == "__main__":
    main()
