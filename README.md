# ImageBatch

A desktop app for batch removing backgrounds from product photos using AI. Built with Python, [rembg](https://github.com/danielgatis/rembg), and [customtkinter](https://github.com/TomSchimansky/CustomTkinter).

## Download

Get the latest installer from the [Releases page](https://github.com/notLmax/ImageBatch/releases/latest):

- **macOS (Apple Silicon):** `ImageBatch.dmg`
- **Windows (64-bit):** `ImageBatch-Setup.exe`

### First Launch on macOS (Important)

Because the app is not signed by an Apple Developer, macOS will block the first launch.

1. Open **Finder** → **Applications**
2. **Right-click** ImageBatch → **Open**
3. In the warning dialog, click **Open**
4. After this one time, you can launch normally from Launchpad or the Dock

### First Launch on Windows

Because the installer is not signed, Windows SmartScreen will warn you.

1. Run `ImageBatch-Setup.exe`
2. If SmartScreen appears, click **More info** → **Run anyway**
3. Follow the installer prompts
4. Launch ImageBatch from the Start Menu

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

To build the Windows installer (run on Windows with Inno Setup installed):

```cmd
python create_icon.py
pyinstaller ImageBatch.spec --noconfirm
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

This creates `Output/ImageBatch-Setup.exe`. The GitHub Actions workflow runs this automatically on every push.

## Project Structure

```
main.py              — entry point
app.py               — main GUI window
processing.py        — background removal worker
widgets.py           — custom UI components
utils.py             — image discovery, thumbnails, helpers
build-mac.sh         — macOS build script (app + DMG)
ImageBatch.spec      — cross-platform PyInstaller configuration
installer.iss        — Inno Setup script for Windows installer
create_icon.py       — generates icon.icns + icon.ico
```
