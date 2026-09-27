from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtGui import QImageReader


IMAGE_EXTENSIONS = {bytes(x).decode().lower() for x in QImageReader.supportedImageFormats()}
EXECUTABLE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
VIEWER_STORAGE_DIR = EXECUTABLE_DIR / "viewer-storage"
APP_DIR = VIEWER_STORAGE_DIR
FAVORITES_FILE = VIEWER_STORAGE_DIR / "favourites.json"
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ICONS_DIR = RESOURCE_DIR / "assets"

COLORS = {
    "window": "#27282a",
    "frame": "#303030",
    "control": "#454545",
    "danger": "#a15454",
    "like": "#9df2fb",
    "unliked": "#838383",
    "border": "rgba(255,255,255,54)",
    "popup_border": "rgba(255,255,255,145)",
    "text": "#ffffff",
}
