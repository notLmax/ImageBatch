#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== ImageBatch macOS Build ==="

# Workaround: Homebrew Python may need Homebrew's libexpat
if [ -d "/opt/homebrew/opt/expat/lib" ]; then
    export DYLD_LIBRARY_PATH="/opt/homebrew/opt/expat/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
fi

# 1. Find Python 3.11+ (required by rembg) with tkinter support
PYTHON=""
for candidate in python3.13 python3.12 python3.11; do
    if command -v "$candidate" &> /dev/null; then
        if "$candidate" -c "import tkinter" 2>/dev/null; then
            PYTHON="$(command -v "$candidate")"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    PYTHON="$(command -v python3)"
fi
echo "Using Python: $PYTHON ($($PYTHON --version))"

# 2. Create fresh build venv
if [ -d ".venv-build" ]; then
    echo "Removing old build venv..."
    rm -rf .venv-build
fi
echo "Creating build venv..."
"$PYTHON" -m venv .venv-build
source .venv-build/bin/activate

# 3. Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt pyinstaller

# 5. Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/

# 6. Run PyInstaller
echo "Running PyInstaller..."
pyinstaller ImageBatch.spec --noconfirm

# 7. Ad-hoc codesign
echo "Codesigning (ad-hoc)..."
codesign --force --deep --sign - "dist/ImageBatch.app"

# 8. Verify .app exists
if [ ! -d "dist/ImageBatch.app" ]; then
    echo "ERROR: dist/ImageBatch.app was not created!"
    exit 1
fi
echo "✓ dist/ImageBatch.app created"

# 9. Build DMG installer
echo "Building DMG installer..."
rm -f dist/ImageBatch.dmg

DMG_STAGING=$(mktemp -d)
cp -R dist/ImageBatch.app "$DMG_STAGING/"
ln -s /Applications "$DMG_STAGING/Applications"

hdiutil create \
    -volname "ImageBatch Installer" \
    -srcfolder "$DMG_STAGING" \
    -ov \
    -format UDZO \
    dist/ImageBatch.dmg

rm -rf "$DMG_STAGING"

if [ ! -f "dist/ImageBatch.dmg" ]; then
    echo "ERROR: dist/ImageBatch.dmg was not created!"
    exit 1
fi

DMG_SIZE=$(du -sh dist/ImageBatch.dmg | cut -f1)
echo "✓ dist/ImageBatch.dmg created ($DMG_SIZE)"

echo ""
echo "=== Build complete ==="
echo "  App:  dist/ImageBatch.app"
echo "  DMG:  dist/ImageBatch.dmg"
