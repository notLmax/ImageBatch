import customtkinter as ctk
from tkinter import colorchooser
from PIL import Image
from typing import Optional, Callable

from utils import (
    generate_thumbnail,
    thumbnail_with_checkerboard,
    pil_to_ctk_image,
    format_time,
)


class ProgressPanel(ctk.CTkFrame):
    """Progress bar with status text and ETA."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.count_label = ctk.CTkLabel(bottom_frame, text="", anchor="w")
        self.count_label.pack(side="left")

        self.time_label = ctk.CTkLabel(bottom_frame, text="", anchor="e")
        self.time_label.pack(side="right")

        self._start_time: Optional[float] = None

    def reset(self):
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready")
        self.count_label.configure(text="")
        self.time_label.configure(text="")
        self._start_time = None

    def set_status(self, text: str):
        self.status_label.configure(text=text)

    def update_progress(self, current: int, total: int, elapsed: float):
        if total == 0:
            return
        fraction = (current + 1) / total
        self.progress_bar.set(fraction)
        self.count_label.configure(text=f"{current + 1} / {total}")

        if current > 0:
            avg_time = elapsed / (current + 1)
            remaining = avg_time * (total - current - 1)
            self.time_label.configure(
                text=f"Elapsed: {format_time(elapsed)}  |  ETA: ~{format_time(remaining)}"
            )
        else:
            self.time_label.configure(text=f"Elapsed: {format_time(elapsed)}")

    def show_complete(self, stats: dict):
        processed = stats.get("processed", 0)
        errors = stats.get("errors", 0)
        skipped = stats.get("skipped", 0)
        elapsed = stats.get("elapsed", 0.0)

        parts = [f"{processed} processed"]
        if errors:
            parts.append(f"{errors} errors")
        if skipped:
            parts.append(f"{skipped} skipped")

        self.status_label.configure(text=f"Done: {', '.join(parts)}")
        self.time_label.configure(text=f"Total time: {format_time(elapsed)}")
        self.progress_bar.set(1.0)


class PreviewGrid(ctk.CTkScrollableFrame):
    """Scrollable grid of before/after thumbnail pairs."""

    THUMB_SIZE = (110, 110)

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._items: list[dict] = []
        self._row = 0

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._items.clear()
        self._row = 0

    def add_before(self, image: Image.Image, filename: str) -> int:
        """Add a 'before' thumbnail. Returns the index for later update."""
        idx = len(self._items)

        # Calculate grid position: 2 pairs per row
        pair_in_row = idx % 2
        row = idx // 2

        col_offset = pair_in_row * 4  # Each pair takes 4 columns

        thumb = generate_thumbnail(image, self.THUMB_SIZE)
        ctk_img = pil_to_ctk_image(thumb, self.THUMB_SIZE)

        before_label = ctk.CTkLabel(self, image=ctk_img, text="")
        before_label.grid(row=row * 2, column=col_offset, padx=(10, 2), pady=(5, 0))

        arrow_label = ctk.CTkLabel(self, text="→", font=("", 18))
        arrow_label.grid(row=row * 2, column=col_offset + 1, padx=2, pady=(5, 0))

        after_placeholder = ctk.CTkLabel(
            self, text="...", width=self.THUMB_SIZE[0], height=self.THUMB_SIZE[1],
            fg_color=("gray85", "gray20"), corner_radius=6
        )
        after_placeholder.grid(row=row * 2, column=col_offset + 2, padx=(2, 10), pady=(5, 0))

        name_label = ctk.CTkLabel(
            self, text=filename, font=("", 11),
            wraplength=self.THUMB_SIZE[0] * 2 + 30
        )
        name_label.grid(
            row=row * 2 + 1, column=col_offset, columnspan=3,
            padx=10, pady=(0, 5)
        )

        self._items.append({
            "before_label": before_label,
            "before_img": ctk_img,
            "after_label": after_placeholder,
            "after_img": None,
            "name_label": name_label,
        })

        return idx

    def update_after(self, index: int, image: Optional[Image.Image], error: Optional[str] = None):
        """Update the 'after' thumbnail for a given index."""
        if index >= len(self._items):
            return

        item = self._items[index]
        after_label = item["after_label"]

        if error:
            after_label.configure(text="ERR", text_color="red", fg_color=("gray85", "gray20"))
        elif image is not None:
            thumb = thumbnail_with_checkerboard(image, self.THUMB_SIZE)
            ctk_img = pil_to_ctk_image(thumb, self.THUMB_SIZE)
            item["after_img"] = ctk_img  # Keep reference to prevent GC
            after_label.configure(image=ctk_img, text="", fg_color="transparent")


class ColorPickerButton(ctk.CTkFrame):
    """Background color selector: transparent toggle + color picker."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._transparent = True
        self._color = (255, 255, 255)  # Default white

        self.transparent_var = ctk.BooleanVar(value=True)
        self.transparent_cb = ctk.CTkCheckBox(
            self, text="Transparent", variable=self.transparent_var,
            command=self._on_toggle
        )
        self.transparent_cb.pack(side="left", padx=(0, 8))

        self.color_btn = ctk.CTkButton(
            self, text="", width=30, height=30,
            fg_color=self._rgb_hex(),
            hover_color=self._rgb_hex(),
            command=self._pick_color,
            state="disabled",
            corner_radius=4,
            border_width=2,
            border_color=("gray60", "gray40"),
        )
        self.color_btn.pack(side="left")

        self.color_label = ctk.CTkLabel(self, text="BG Color:", font=("", 12))
        # Not packed - label is part of the parent layout

    def _rgb_hex(self) -> str:
        return f"#{self._color[0]:02x}{self._color[1]:02x}{self._color[2]:02x}"

    def _on_toggle(self):
        self._transparent = self.transparent_var.get()
        self.color_btn.configure(state="disabled" if self._transparent else "normal")

    def _pick_color(self):
        result = colorchooser.askcolor(
            initialcolor=self._rgb_hex(),
            title="Choose Background Color"
        )
        if result and result[0]:
            self._color = (int(result[0][0]), int(result[0][1]), int(result[0][2]))
            self.color_btn.configure(fg_color=self._rgb_hex(), hover_color=self._rgb_hex())

    def get_bgcolor(self) -> Optional[tuple[int, int, int, int]]:
        """Return (R,G,B,A) tuple or None for transparent."""
        if self._transparent:
            return None
        return (*self._color, 255)
