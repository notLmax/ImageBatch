#!/usr/bin/env python3
"""ImageBatch - Batch background removal for product photos."""

import os
import sys
from pathlib import Path

# Inside a PyInstaller bundle, redirect rembg model cache to a writable location.
# Must happen before importing rembg.
if getattr(sys, "frozen", False):
    _cache = Path.home() / "Library" / "Application Support" / "ImageBatch" / "models"
    _cache.mkdir(parents=True, exist_ok=True)
    os.environ["U2NET_HOME"] = str(_cache)

import customtkinter as ctk
from app import ImageBatchApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ImageBatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
