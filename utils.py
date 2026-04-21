from pathlib import Path
from PIL import Image, ImageDraw
from customtkinter import CTkImage

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}


def discover_images(folder: str) -> list[Path]:
    """Return sorted list of image paths in folder matching supported extensions."""
    folder_path = Path(folder)
    if not folder_path.is_dir():
        return []
    return sorted(
        p
        for p in folder_path.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def generate_thumbnail(image: Image.Image, size: tuple[int, int] = (120, 120)) -> Image.Image:
    """Create a thumbnail preserving aspect ratio."""
    thumb = image.copy()
    thumb.thumbnail(size, Image.LANCZOS)
    return thumb


def create_checkerboard(width: int, height: int, square_size: int = 10) -> Image.Image:
    """Create a checkerboard pattern image to visualize transparency."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    colors = [(200, 200, 200), (255, 255, 255)]
    for y in range(0, height, square_size):
        for x in range(0, width, square_size):
            color_idx = ((x // square_size) + (y // square_size)) % 2
            draw.rectangle([x, y, x + square_size - 1, y + square_size - 1], fill=colors[color_idx])
    return img


def thumbnail_with_checkerboard(image: Image.Image, size: tuple[int, int] = (120, 120)) -> Image.Image:
    """Create a thumbnail with checkerboard background for transparent images."""
    thumb = generate_thumbnail(image, size)
    if thumb.mode == "RGBA":
        checker = create_checkerboard(thumb.width, thumb.height, 8)
        checker.paste(thumb, mask=thumb.split()[3])
        return checker
    return thumb


def pil_to_ctk_image(image: Image.Image, size: tuple[int, int] = (120, 120)) -> CTkImage:
    """Convert a PIL image to CTkImage for display."""
    return CTkImage(light_image=image, dark_image=image, size=size)


def format_time(seconds: float) -> str:
    """Format seconds into a human-readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours = int(minutes // 60)
    mins = minutes % 60
    return f"{hours}h {mins:02d}m"


def unique_output_path(output_folder: Path, stem: str, ext: str = ".png") -> Path:
    """Generate a unique output path, appending _1, _2 etc. if needed."""
    candidate = output_folder / (stem + ext)
    if not candidate.exists():
        return candidate
    counter = 1
    while True:
        candidate = output_folder / f"{stem}_{counter}{ext}"
        if not candidate.exists():
            return candidate
        counter += 1


def model_exists(model_name: str) -> bool:
    """Check if the rembg model file already exists locally."""
    model_dir = Path.home() / ".u2net"
    return (model_dir / f"{model_name}.onnx").exists()
