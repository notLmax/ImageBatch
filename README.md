# ImageBatch

A desktop app for batch removing backgrounds from product photos using AI. Built with Python, [rembg](https://github.com/danielgatis/rembg), and [customtkinter](https://github.com/TomSchimansky/CustomTkinter).

## Download for macOS

Download the latest **ImageBatch.dmg** from the [GitHub Releases](https://github.com/notLmax/ImageBatch/releases/latest) page. Open the DMG, drag ImageBatch to your Applications folder, and you're ready to go.

### First Launch (Important)

Because this app is not signed by an Apple Developer, macOS will block the first launch.

1. Open **Finder** and go to **Applications**
2. **Right-click** ImageBatch and select **Open**
3. In the warning dialog, click **Open**
4. After this one time, you can launch normally from Launchpad or the Dock

## Features

- **Batch processing** — select a folder or individual files (PNG, JPG, WebP, BMP, TIFF)
- **Multiple AI models** — u2net, u2netp, isnet-general-use, silueta, birefnet-general, birefnet-general-lite
- **Transparent or solid backgrounds** — toggle transparency or pick a custom color
- **Live preview** — scrollable before/after thumbnail grid with checkerboard transparency
- **Progress tracking** — progress bar, image count, elapsed time, and ETA
- **Alpha matting & post-processing** — optional edge refinement for cleaner results
- **Non-blocking UI** — processing runs in a background thread with cancel support

## Usage

1. Select input images (folder or individual files)
2. Choose an output folder
3. Pick a model and adjust settings
4. Click **Start Processing**
5. Review before/after previews as images are processed

On first run, the selected AI model (~200-400 MB) will be downloaded automatically and cached for future use.

## Building from Source

Requires Python 3.11+ with tkinter support.

```bash
pip install -r requirements.txt
python main.py
```

To build the macOS `.app` bundle and DMG installer:

```bash
./build-mac.sh
```

This creates `dist/ImageBatch.app` and `dist/ImageBatch.dmg`.

## Project Structure

```
main.py              — entry point
app.py               — main GUI window
processing.py        — background removal worker
widgets.py           — custom UI components
utils.py             — image discovery, thumbnails, helpers
build-mac.sh         — macOS build script (app + DMG)
ImageBatch.spec      — PyInstaller configuration
```
