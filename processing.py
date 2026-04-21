import threading
import time
from pathlib import Path
from typing import Callable, Optional

from PIL import Image
from rembg import new_session, remove

from utils import unique_output_path


class BatchProcessor:
    """Processes a list of images through rembg in a background thread."""

    def __init__(
        self,
        image_paths: list[Path],
        output_folder: Path,
        model_name: str = "u2net",
        alpha_matting: bool = False,
        post_process_mask: bool = False,
        bgcolor: Optional[tuple[int, int, int, int]] = None,
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_status: Optional[Callable] = None,
    ):
        self.image_paths = image_paths
        self.output_folder = output_folder
        self.model_name = model_name
        self.alpha_matting = alpha_matting
        self.post_process_mask = post_process_mask
        self.bgcolor = bgcolor
        self.on_progress = on_progress  # (index, total, output_pil_image_or_None, error_str_or_None)
        self.on_complete = on_complete  # (stats_dict)
        self.on_status = on_status  # (status_string)
        self._cancel = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start processing in a background thread."""
        self._cancel.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def cancel(self):
        """Request cancellation of the current batch."""
        self._cancel.set()

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def _run(self):
        stats = {"processed": 0, "errors": 0, "skipped": 0, "elapsed": 0.0}
        start_time = time.time()
        seen_stems: set[str] = set()

        # Load model (may trigger download on first run)
        if self.on_status:
            self.on_status(f"Loading model '{self.model_name}'...")
        try:
            session = new_session(self.model_name)
        except Exception as e:
            stats["errors"] = len(self.image_paths)
            stats["elapsed"] = time.time() - start_time
            if self.on_status:
                self.on_status(f"Failed to load model: {e}")
            if self.on_complete:
                self.on_complete(stats)
            return

        if self.on_status:
            self.on_status("Processing...")

        for i, path in enumerate(self.image_paths):
            if self._cancel.is_set():
                stats["skipped"] = len(self.image_paths) - i
                break

            try:
                img = Image.open(path).convert("RGBA")
                result = remove(
                    img,
                    session=session,
                    alpha_matting=self.alpha_matting,
                    post_process_mask=self.post_process_mask,
                    bgcolor=self.bgcolor,
                )

                # Handle duplicate stems
                stem = path.stem
                if stem in seen_stems:
                    output_path = unique_output_path(self.output_folder, stem)
                else:
                    output_path = self.output_folder / f"{stem}.png"
                seen_stems.add(stem)

                result.save(output_path, "PNG")
                stats["processed"] += 1

                if self.on_progress:
                    self.on_progress(i, len(self.image_paths), result, None)

            except Exception as e:
                stats["errors"] += 1
                if self.on_progress:
                    self.on_progress(i, len(self.image_paths), None, str(e))

        stats["elapsed"] = time.time() - start_time
        if self.on_status:
            self.on_status("Complete" if not self._cancel.is_set() else "Cancelled")
        if self.on_complete:
            self.on_complete(stats)
