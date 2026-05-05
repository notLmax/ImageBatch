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


def main():
    ICON_DIR.mkdir(exist_ok=True)

    for s in SIZES:
        img = create_icon_image(s)
        # Standard size
        if s <= 512:
            img.resize((s, s), Image.LANCZOS).save(ICON_DIR / f"icon_{s}x{s}.png")
        # @2x size (the 1024 serves as 512@2x)
        if s >= 32:
            half = s // 2
            if half in [16, 32, 64, 128, 256, 512]:
                img.resize((s, s), Image.LANCZOS).save(ICON_DIR / f"icon_{half}x{half}@2x.png")

    # Use iconutil to create .icns
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(ICON_DIR), "-o", "icon.icns"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"iconutil failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Cleanup
    import shutil
    shutil.rmtree(ICON_DIR)
    print("Created icon.icns")


if __name__ == "__main__":
    main()
