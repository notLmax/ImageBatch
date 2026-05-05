# Build Status

## What Was Built

- **ImageBatch.app** — native macOS app bundle (PyInstaller, arm64 only)
- **ImageBatch.dmg** — DMG installer with drag-to-Applications layout
- **build-mac.sh** — idempotent build script that creates both from source
- **GitHub Actions workflow** — builds DMG on every push to `main` and creates a GitHub Release

## Build Artifacts

| Artifact | Size |
|----------|------|
| `dist/ImageBatch.app` | ~284 MB |
| `dist/ImageBatch.dmg` | ~110 MB |

## Known Issues / Caveats

- **Unsigned app** — no Apple Developer certificate. Users must right-click > Open on first launch to bypass Gatekeeper. Documented in README.
- **Apple Silicon only** — built with `target_arch='arm64'`. Will not run on Intel Macs.
- **First-run model download** — rembg downloads the selected AI model (~200-400 MB) on first use. Models are cached in `~/Library/Application Support/ImageBatch/models/`.
- **Bundle size** — the app is ~284 MB due to bundled Python + ONNX Runtime + NumPy + SciPy. This is expected for ML-based desktop apps.

## GitHub Actions

Workflow: `.github/workflows/build-mac.yml`
- Trigger: push to `main` or manual `workflow_dispatch`
- Runner: `macos-14` (Apple Silicon)
- Outputs: DMG artifact + GitHub Release with DMG attached
- Requires: `contents: write` permission (configured in workflow)
