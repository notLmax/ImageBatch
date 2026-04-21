#!/usr/bin/env python3
"""ImageBatch - Batch background removal for product photos."""

import customtkinter as ctk
from app import ImageBatchApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ImageBatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
