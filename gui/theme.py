"""VS Code 2026 Fluent Light+ theme for IMGtoPDF."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# ── Surface tokens ───────────────────────────────────────
BG = "#edeff3"
PANEL = "#ffffff"
CANVAS_BG = "#e6e8ed"
HEADER_BG = "#f5f6f8"

# ── Text tokens ──────────────────────────────────────────
TEXT = "#1f1f1f"
MUTED = "#616161"

# ── Accent tokens ────────────────────────────────────────
BLUE = "#005fb8"
BLUE_DARK = "#004882"

# ── Border tokens ────────────────────────────────────────
LINE = "#dcdde2"

# ── Interactive state tokens ─────────────────────────────
GHOST_BG = "#f2f4f6"
HOVER_BG = "#e2e4e8"
PRESS_BG = "#d0d2d6"
SELECT_BG = "#d6e4ff"

# ── Status bar tokens ────────────────────────────────────
STATUS_BG = "#007acc"
STATUS_FG = "#ffffff"

# ── Preview tokens ───────────────────────────────────────
SHADOW = "#c8cad0"

# ── Typography ───────────────────────────────────────────
_FONT = "Microsoft YaHei"
_SIZE = 10
_SIZE_SM = 9
_SIZE_H = 11


def configure_style(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # ── Defaults ──────────────────────────────────────
    style.configure(
        ".", font=(_FONT, _SIZE), background=BG, foreground=TEXT, borderwidth=0,
    )

    # ── Frames ────────────────────────────────────────
    style.configure("App.TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Divider.TFrame", background=LINE)

    # ── Labels ────────────────────────────────────────
    style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
    style.configure(
        "Muted.TLabel", background=PANEL, foreground=MUTED,
        font=(_FONT, _SIZE_SM),
    )
    style.configure(
        "Section.TLabel", background=PANEL, foreground=TEXT,
        font=(_FONT, _SIZE_H, "bold"),
    )

    # ── Status Bar ────────────────────────────────────
    style.configure("StatusBar.TFrame", background=STATUS_BG)
    style.configure(
        "StatusBar.TLabel", background=STATUS_BG, foreground=STATUS_FG,
        font=(_FONT, 12),
    )

    # ── Primary Button ────────────────────────────────
    style.configure(
        "Primary.TButton",
        background=BLUE, foreground="#ffffff", borderwidth=0,
        padding=(16, 8), font=(_FONT, _SIZE),
    )
    style.map(
        "Primary.TButton",
        background=[
            ("active", BLUE_DARK),
            ("pressed", "#003566"),
            ("disabled", "#cccccc"),
        ],
        foreground=[("disabled", "#888888")],
    )

    # ── Ghost / Secondary Button ──────────────────────
    style.configure(
        "Ghost.TButton",
        background=GHOST_BG, foreground=TEXT, borderwidth=1,
        padding=(10, 7), font=(_FONT, _SIZE),
    )
    style.map(
        "Ghost.TButton",
        background=[
            ("active", HOVER_BG),
            ("pressed", PRESS_BG),
            ("disabled", PANEL),
        ],
        foreground=[("disabled", "#999999")],
    )

    # ── Treeview ──────────────────────────────────────
    style.configure(
        "Treeview",
        rowheight=32, fieldbackground=PANEL, background=PANEL,
        foreground=TEXT, borderwidth=1,
    )
    style.configure(
        "Treeview.Heading",
        background=HEADER_BG, foreground=MUTED,
        font=(_FONT, _SIZE_SM, "bold"),
        borderwidth=1, relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", SELECT_BG)],
        foreground=[("selected", TEXT)],
    )

    # ── Entry ─────────────────────────────────────────
    style.configure(
        "TEntry",
        fieldbackground=PANEL, foreground=TEXT,
        borderwidth=1, padding=(8, 6),
    )

    # ── Scrollbar ─────────────────────────────────────
    style.configure(
        "Vertical.TScrollbar",
        background="#c8c8c8", troughcolor=PANEL,
        borderwidth=0, arrowsize=0, width=8,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#a0a0a0")],
    )

    # ── Separator ─────────────────────────────────────
    style.configure("TSeparator", background=LINE)

    return style
