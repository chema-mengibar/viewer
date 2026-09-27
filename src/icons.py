from __future__ import annotations

from PySide6.QtGui import QIcon

from src.config import ICONS_DIR


def icon(name: str) -> QIcon:
    return QIcon(str(ICONS_DIR / f"{name}.svg"))
