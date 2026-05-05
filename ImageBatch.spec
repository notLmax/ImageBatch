# -*- mode: python ; coding: utf-8 -*-
"""Cross-platform PyInstaller spec for ImageBatch (macOS + Windows)."""

import sys
import importlib
from pathlib import Path

from PyInstaller.utils.hooks import copy_metadata

sys.setrecursionlimit(10000)

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

block_cipher = None

# Locate customtkinter package to bundle its assets (themes, images)
ctk_path = Path(importlib.import_module("customtkinter").__file__).parent

# Collect package metadata needed by importlib.metadata.version() calls
metadata_packages = [
    "pymatting", "rembg", "scikit-image", "scipy", "numpy",
    "Pillow", "pooch", "onnxruntime", "tqdm", "numba",
]
extra_datas = []
for pkg in metadata_packages:
    try:
        extra_datas += copy_metadata(pkg)
    except Exception:
        pass

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (str(ctk_path), "customtkinter"),
    ] + extra_datas,
    hiddenimports=[
        "onnxruntime",
        "onnxruntime.capi._pybind_state",
        "rembg",
        "rembg.sessions",
        "rembg.sessions.u2net",
        "rembg.sessions.u2netp",
        "rembg.sessions.silueta",
        "rembg.sessions.isnet_general_use",
        "rembg.sessions.birefnet_general",
        "rembg.sessions.birefnet_general_lite",
        "PIL._tkinter_finder",
        "customtkinter",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe_kwargs = dict(
    name="ImageBatch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
if IS_MAC:
    exe_kwargs["target_arch"] = "arm64"
if IS_WIN:
    exe_kwargs["icon"] = "icon.ico"

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    **exe_kwargs,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name="ImageBatch",
)

if IS_MAC:
    app = BUNDLE(
        coll,
        name="ImageBatch.app",
        icon="icon.icns",
        bundle_identifier="com.notlmax.imagebatch",
        info_plist={
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
        },
    )
