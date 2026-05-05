#!/usr/bin/env python3
"""Generate icon.icns for ImageBatch app."""

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ICON_DIR = Path("icon.iconset")
SIZES = [16, 32, 64, 128, 256, 512, 1024]


def create_icon_image(size: int) -> Image.Image:
    """Create a clean icon: rounded blue square with white 'IB' letters.
    Always render at 512px and resize down for quality."""
    render_size = max(size, 512)
    img = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded rectangle
    margin = int(render_size * 0.05)
    radius = int(render_size * 0.18)
    draw.rounded_rectangle(
        [margin, margin, render_size - margin, render_size - margin],
        radius=radius,
        fill=(41, 98, 255),  # vibrant blue
    )

    # Draw "IB" text
    font_size = int(render_size * 0.45)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    text = "IB"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (render_size - tw) // 2 - bbox[0]
    y = (render_size - th) // 2 - bbox[1]
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    if size != render_size:
        img = img.resize((size, size), Image.LANCZOS)

    return img


def create_ico() -> None:
    """Create a multi-resolution icon.ico for Windows."""
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base = create_icon_image(256)
    base.save("icon.ico", format="ICO", sizes=ico_sizes)
    print("Created icon.ico")


def create_icns() -> None:
    """Create icon.icns for macOS via iconutil."""
    ICON_DIR.mkdir(exist_ok=True)

    for s in SIZES:
        img = create_icon_image(s)
        if s <= 512:
            img.resize((s, s), Image.LANCZOS).save(ICON_DIR / f"icon_{s}x{s}.png")
        if s >= 32:
            half = s // 2
            if half in [16, 32, 64, 128, 256, 512]:
                img.resize((s, s), Image.LANCZOS).save(ICON_DIR / f"icon_{half}x{half}@2x.png")

    result = subprocess.run(
        ["iconutil", "-c", "icns", str(ICON_DIR), "-o", "icon.icns"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"iconutil failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    import shutil
    shutil.rmtree(ICON_DIR)
    print("Created icon.icns")


def main():
    """Generate icons for the current platform.

    On macOS: creates icon.icns (and icon.ico for cross-platform builds).
    On Windows/Linux: creates icon.ico only.
    """
    create_ico()
    if sys.platform == "darwin":
        create_icns()


if __name__ == "__main__":
    main()
