# ImageBatch — Native macOS App Build Spec

Package the existing Python ImageBatch app as a native macOS `.app` bundle distributed via DMG installer, so non-technical users can install and launch it from Finder/Launchpad without touching a terminal.

## Constraints (decided by owner)
- **Unsigned** — no Apple Developer account. Users will need to right-click → Open the first time. Document this clearly.
- **Apple Silicon only** (`arm64`). Smaller bundle, faster build. Skip universal binary.
- Repo: `notLmax/ImageBatch` (already cloned at `~/projects/ImageBatch`).

## Stack Decisions
- **PyInstaller** for bundling Python + dependencies + Tkinter into a `.app`
- **create-dmg** (homebrew) for the DMG installer with drag-to-Applications UI
- **GitHub Actions** workflow that builds a fresh DMG on every push to `main` and attaches it to a GitHub Release

## Critical Engineering Notes (don't skip these)

### 1. rembg Model Cache Path
By default `rembg` downloads models to `~/.u2net/`. Inside a PyInstaller `.app`, the bundle's internal paths are read-only, but `~/.u2net` is in the user's home dir — that should work. **Verify** by running the bundled app and triggering a model download. If it fails, set the cache to `~/Library/Application Support/ImageBatch/models/` via the `U2NET_HOME` environment variable, set early in `main.py`:

```python
import os
from pathlib import Path
cache = Path.home() / "Library" / "Application Support" / "ImageBatch" / "models"
cache.mkdir(parents=True, exist_ok=True)
os.environ["U2NET_HOME"] = str(cache)
```

Set this BEFORE importing rembg.

### 2. PyInstaller Hidden Imports
`rembg`, `onnxruntime`, and `customtkinter` use dynamic imports that PyInstaller misses. Add explicit `--hidden-import` flags or a `.spec` file with `hiddenimports=[...]`. Common ones:
- `onnxruntime`
- `onnxruntime.capi._pybind_state`
- `rembg.sessions`
- `rembg.sessions.u2net`, `u2netp`, `silueta`, `isnet_general_use`, `birefnet_general`, `birefnet_general_lite`
- `PIL._tkinter_finder`
- `customtkinter`

### 3. customtkinter Theme/Asset Files
customtkinter ships JSON theme files and image assets that PyInstaller doesn't auto-discover. Use `--add-data` to bundle them, or import `customtkinter` and use `Path(customtkinter.__file__).parent` to find them at build time and inject them into the .spec.

### 4. Tkinter on macOS
Tkinter requires the system's Tcl/Tk. Make sure the Python being used to build supports Tkinter (`python -c "import tkinter; tkinter._test()"` should pop a window). If using pyenv-installed Python, it must be built with `--enable-framework` and Tcl/Tk support.

### 5. Bundle Size
Expect the final `.app` to be 500MB–1GB due to PyTorch+ONNX. This is normal. Don't try to optimize this aggressively — broken bundle is worse than a big bundle.

## Build Steps

### Step 1 — Set up build env
- Create `build-mac.sh` script at repo root that:
  1. Creates a fresh venv at `.venv-build/`
  2. Installs from `requirements.txt` + `pyinstaller`
  3. Cleans `dist/` and `build/`
  4. Runs PyInstaller with the `.spec` file
  5. Runs `create-dmg` to produce `ImageBatch.dmg`
- Make it idempotent and safe to re-run.

### Step 2 — PyInstaller spec
Create `ImageBatch.spec`:
- App name: `ImageBatch`
- Entry: `main.py`
- `windowed=True` (no terminal window on launch)
- Icon: generate a simple `icon.icns` (a clean, modern icon — a stylized image with a "scissor cut" or "remove background" motif, or the letters "IB" on a colored background). Use Pillow + `iconutil` to create it. If too complex, ship without icon for v1.
- `target_arch='arm64'`
- Bundle customtkinter assets via `datas`
- Add all hidden imports listed above
- `bundle_identifier='com.notlmax.imagebatch'`

### Step 3 — Patch main.py
Add the U2NET_HOME cache redirect (above) at the very top of `main.py`, before any other imports. Wrap in a `if getattr(sys, 'frozen', False):` block so it only activates inside the bundled app, not during dev.

### Step 4 — Build & test locally
- Run `./build-mac.sh`
- Verify `dist/ImageBatch.app` exists
- Launch it: `open dist/ImageBatch.app`
- Verify the GUI opens, can select a test image, run background removal (on a small jpg), and the result saves correctly. Use a small test image you generate or find in `public/` or similar — if no test image exists, generate one with PIL (a 100x100 colored square with a circle on top).
- If launch fails, check Console.app for crash logs (search "ImageBatch") and fix.

### Step 5 — DMG installer
- Install `create-dmg` if missing: `brew install create-dmg`
- Run create-dmg to produce `ImageBatch.dmg` with:
  - Custom volume name "ImageBatch Installer"
  - "Drag to Applications" UI (a symlink to /Applications visible in the DMG window)
  - Window size 500x300
- Output: `dist/ImageBatch.dmg`

### Step 6 — GitHub Actions workflow
Create `.github/workflows/build-mac.yml`:
- Trigger: push to `main` and manual `workflow_dispatch`
- Runner: `macos-14` (Apple Silicon)
- Steps: checkout → set up Python 3.11 → run `build-mac.sh` → upload `ImageBatch.dmg` as artifact AND create a GitHub Release with the DMG attached (use `softprops/action-gh-release@v2`, version = `v$(date +%Y.%m.%d)-$(git rev-parse --short HEAD)`)
- Permissions: `contents: write` for the release step.

### Step 7 — README updates
Update `README.md`:
- Add a top section: "Download for macOS" with a link to the latest GitHub Release `.dmg`
- "First Launch (Important)" subsection explaining macOS Gatekeeper:
  > Because this app is not signed by an Apple Developer, macOS will block the first launch.
  > 1. Open Finder → Applications
  > 2. **Right-click** ImageBatch → **Open**
  > 3. In the warning dialog, click **Open**
  > 4. After this one time, you can launch normally from Launchpad or the Dock.
- Keep the existing "developer setup" section but move it lower under a "Building from source" heading.

### Step 8 — .gitignore
Add to `.gitignore`:
```
.venv-build/
build/
dist/
*.spec.bak
```
But keep `ImageBatch.spec` tracked (without trailing .bak).

### Step 9 — Commit & push
- Commit message: `Add native macOS app build (PyInstaller + DMG)`
- Push to `main`
- Confirm the GitHub Actions workflow runs and produces a release. If permissions/secrets are missing, document what's needed and skip the release upload — artifact upload is fine.

### Step 10 — Update STATUS.md
Create `docs/STATUS.md` summarizing:
- What was built
- DMG file size
- Build time
- Known issues / first-launch UX caveats
- Link to GitHub Release (if successful)

## Done = All True
- `dist/ImageBatch.app` exists, launches via double-click, runs a background-removal job successfully end-to-end.
- `dist/ImageBatch.dmg` exists, opens with drag-to-Applications UI, install works.
- `build-mac.sh` is idempotent and reproducible.
- GitHub Actions workflow is committed (whether or not the run succeeds — fix it if it fails).
- README explains download + first-launch flow clearly enough for a non-technical user.
- All committed and pushed to `main`.
