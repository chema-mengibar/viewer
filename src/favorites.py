from __future__ import annotations

import json
from pathlib import Path

from src.config import APP_DIR, FAVORITES_FILE


def load_favorites() -> list[str]:
    try:
        values = json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
        return [p for p in values if isinstance(p, str) and Path(p).is_dir()]
    except (OSError, json.JSONDecodeError):
        return []


def save_favorites(values: list[str]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    FAVORITES_FILE.write_text(json.dumps(values, indent=2), encoding="utf-8")
