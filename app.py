import os
import time
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from processing import BatchProcessor
from utils import discover_images, generate_thumbnail, pil_to_ctk_image, model_exists
from widgets import ProgressPanel, PreviewGrid, ColorPickerButton

MODELS = [
    "u2net",
    "u2netp",
    "isnet-general-use",
    "silueta",
    "birefnet-general",
    "birefnet-general-lite",
]


class ImageBatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ImageBatch - Background Remover")
        self.geometry("900x750")
        self.minsize(700, 550)

        self._image_paths: list[Path] = []
        self._processor: BatchProcessor | None = None
        self._process_start_time: float = 0

        self._build_ui()

    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkLabel(
            self, text="ImageBatch", font=("", 24, "bold"),
            anchor="w"
        )
        header.pack(fill="x", padx=20, pady=(15, 5))

        subtitle = ctk.CTkLabel(
            self, text="Batch remove backgrounds from product photos",
            font=("", 13), text_color=("gray40", "gray60"), anchor="w"
        )
        subtitle.pack(fill="x", padx=20, pady=(0, 10))

        # ── Input/Output Folders ──
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(fill="x", padx=20, pady=5)

        # Input row
        input_row = ctk.CTkFrame(folder_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(input_row, text="Input:", width=60, anchor="w").pack(side="left")
        self.input_btn = ctk.CTkButton(
            input_row, text="Select Folder", width=120, command=self._select_input
        )
        self.input_btn.pack(side="left", padx=(0, 10))
        self.input_files_btn = ctk.CTkButton(
            input_row, text="Select Files", width=100, command=self._select_files,
            fg_color=("gray70", "gray30")
        )
        self.input_files_btn.pack(side="left", padx=(0, 10))
        self.input_label = ctk.CTkLabel(input_row, text="No folder selected", anchor="w", text_color=("gray50", "gray50"))
        self.input_label.pack(side="left", fill="x", expand=True)

        # Output row
        output_row = ctk.CTkFrame(folder_frame, fg_color="transparent")
        output_row.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(output_row, text="Output:", width=60, anchor="w").pack(side="left")
        self.output_btn = ctk.CTkButton(
            output_row, text="Select Folder", width=120, command=self._select_output
        )
        self.output_btn.pack(side="left", padx=(0, 10))
        self.output_label = ctk.CTkLabel(output_row, text="No folder selected", anchor="w", text_color=("gray50", "gray50"))
        self.output_label.pack(side="left", fill="x", expand=True)

        # ── Settings ──
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(fill="x", padx=20, pady=5)

        settings_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        settings_row.pack(fill="x", padx=10, pady=10)

        # Model
        ctk.CTkLabel(settings_row, text="Model:", font=("", 12)).pack(side="left", padx=(0, 5))
        self.model_var = ctk.StringVar(value="u2net")
        self.model_menu = ctk.CTkOptionMenu(
            settings_row, variable=self.model_var, values=MODELS, width=170
        )
        self.model_menu.pack(side="left", padx=(0, 20))

        # Alpha matting
        self.alpha_var = ctk.BooleanVar(value=False)
        self.alpha_cb = ctk.CTkCheckBox(
            settings_row, text="Alpha Matting", variable=self.alpha_var
        )
        self.alpha_cb.pack(side="left", padx=(0, 20))

        # Post-process mask
        self.postprocess_var = ctk.BooleanVar(value=False)
        self.postprocess_cb = ctk.CTkCheckBox(
            settings_row, text="Post-process", variable=self.postprocess_var
        )
        self.postprocess_cb.pack(side="left", padx=(0, 20))

        # Background color
        self.color_picker = ColorPickerButton(settings_row)
        self.color_picker.pack(side="left")

        # ── Action Buttons ──
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=5)

        self.start_btn = ctk.CTkButton(
            action_frame, text="▶  Start Processing", width=180, height=40,
            font=("", 15, "bold"), command=self._start_processing
        )
        self.start_btn.pack(side="left")

        self.cancel_btn = ctk.CTkButton(
            action_frame, text="■  Cancel", width=100, height=40,
            fg_color=("gray70", "gray30"), state="disabled",
            command=self._cancel_processing
        )
        self.cancel_btn.pack(side="left", padx=10)

        self.open_output_btn = ctk.CTkButton(
            action_frame, text="Open Output Folder", width=140, height=40,
            fg_color=("gray70", "gray30"), state="disabled",
            command=self._open_output_folder
        )
        self.open_output_btn.pack(side="right")

        # ── Progress ──
        self.progress_panel = ProgressPanel(self)
        self.progress_panel.pack(fill="x", padx=20, pady=5)

        # ── Preview Grid ──
        self.preview_grid = PreviewGrid(self, label_text="Preview")
        self.preview_grid.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        # State
        self._input_folder: str | None = None
        self._output_folder: str | None = None

        # Window close handler
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Folder Selection ──

    def _select_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if not folder:
            return
        self._input_folder = folder
        images = discover_images(folder)
        self._image_paths = images
        count = len(images)
        self.input_label.configure(
            text=f"{folder}  ({count} image{'s' if count != 1 else ''})",
            text_color=("gray10", "gray90"),
        )
        self._populate_previews()

    def _select_files(self):
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif"),
            ("All files", "*.*"),
        ]
        files = filedialog.askopenfilenames(title="Select Images", filetypes=filetypes)
        if not files:
            return
        self._image_paths = [Path(f) for f in files]
        self._input_folder = str(self._image_paths[0].parent)
        count = len(self._image_paths)
        self.input_label.configure(
            text=f"{count} file{'s' if count != 1 else ''} selected",
            text_color=("gray10", "gray90"),
        )
        self._populate_previews()

    def _select_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if not folder:
            return
        self._output_folder = folder
        self.output_label.configure(
            text=folder, text_color=("gray10", "gray90")
        )

    def _populate_previews(self):
        """Load before-thumbnails into the preview grid (on a background thread)."""
        self.preview_grid.clear()
        paths = self._image_paths

        def _load():
            for i, path in enumerate(paths):
                try:
                    img = Image.open(path)
                    img.load()
                    # Schedule thumbnail addition on GUI thread
                    self.after(0, self._add_before_thumb, i, img, path.name)
                except Exception:
                    self.after(0, self._add_before_thumb, i, None, path.name)

        threading.Thread(target=_load, daemon=True).start()

    def _add_before_thumb(self, index: int, image: Image.Image | None, filename: str):
        if image:
            self.preview_grid.add_before(image, filename)
        else:
            self.preview_grid.add_before(
                Image.new("RGB", (120, 120), (200, 200, 200)), f"{filename} (err)"
            )

    # ── Processing ──

    def _start_processing(self):
        if not self._image_paths:
            self.progress_panel.set_status("No images selected!")
            return
        if not self._output_folder:
            self.progress_panel.set_status("No output folder selected!")
            return

        output_path = Path(self._output_folder)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)

        if not os.access(self._output_folder, os.W_OK):
            self.progress_panel.set_status("Output folder is not writable!")
            return

        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.open_output_btn.configure(state="disabled")
        self.progress_panel.reset()
        self._process_start_time = time.time()

        self._processor = BatchProcessor(
            image_paths=self._image_paths,
            output_folder=output_path,
            model_name=self.model_var.get(),
            alpha_matting=self.alpha_var.get(),
            post_process_mask=self.postprocess_var.get(),
            bgcolor=self.color_picker.get_bgcolor(),
            on_progress=self._on_progress,
            on_complete=self._on_complete,
            on_status=self._on_status,
        )
        self._processor.start()

    def _cancel_processing(self):
        if self._processor:
            self._processor.cancel()
            self.cancel_btn.configure(state="disabled")
            self.progress_panel.set_status("Cancelling...")

    def _on_progress(self, index: int, total: int, result_image, error):
        """Called from worker thread."""
        elapsed = time.time() - self._process_start_time
        self.after(0, self._handle_progress, index, total, result_image, error, elapsed)

    def _handle_progress(self, index: int, total: int, result_image, error, elapsed: float):
        """Runs on GUI thread."""
        self.progress_panel.update_progress(index, total, elapsed)
        self.preview_grid.update_after(index, result_image, error)

    def _on_complete(self, stats: dict):
        """Called from worker thread."""
        self.after(0, self._handle_complete, stats)

    def _handle_complete(self, stats: dict):
        """Runs on GUI thread."""
        self.progress_panel.show_complete(stats)
        self.start_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
        self.open_output_btn.configure(state="normal")

    def _on_status(self, text: str):
        """Called from worker thread."""
        self.after(0, self.progress_panel.set_status, text)

    # ── Utilities ──

    def _open_output_folder(self):
        if self._output_folder:
            if sys.platform == "win32":
                os.startfile(self._output_folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self._output_folder])
            else:
                subprocess.Popen(["xdg-open", self._output_folder])

    def _on_close(self):
        if self._processor and self._processor.is_running:
            self._processor.cancel()
        self.destroy()
