# ImageBatch

A desktop app for batch removing backgrounds from product photos using AI. Built with Python, [rembg](https://github.com/danielgatis/rembg), and [customtkinter](https://github.com/TomSchimansky/CustomTkinter).

## Features

- **Batch processing** — select a folder or individual files (PNG, JPG, WebP, BMP, TIFF)
- **Multiple AI models** — u2net, u2netp, isnet-general-use, silueta, birefnet-general, birefnet-general-lite
- **Transparent or solid backgrounds** — toggle transparency or pick a custom color
- **Live preview** — scrollable before/after thumbnail grid with checkerboard transparency
- **Progress tracking** — progress bar, image count, elapsed time, and ETA
- **Alpha matting & post-processing** — optional edge refinement for cleaner results
- **Non-blocking UI** — processing runs in a background thread with cancel support

## Setup

Requires Python 3.8+.

```bash
pip install -r requirements.txt
python main.py
```

On first run, the selected AI model (~200–400 MB) will be downloaded automatically and cached for future use.

## Usage

1. Select input images (folder or individual files)
2. Choose an output folder
3. Pick a model and adjust settings
4. Click **Start Processing**
5. Review before/after previews as images are processed

## Project Structure

```
main.py          — entry point
app.py           — main GUI window
processing.py    — background removal worker
widgets.py       — custom UI components (progress panel, preview grid, color picker)
utils.py         — image discovery, thumbnails, helpers
```
