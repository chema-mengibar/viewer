from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.config import VIEWER_STORAGE_DIR


def likes_file(directory: Path) -> Path:
    full_path = str(directory.resolve())
    digest = hashlib.sha256(full_path.encode("utf-8")).hexdigest()
    return VIEWER_STORAGE_DIR / f"{digest}.json"


def load_likes(directory: Path) -> set[str]:
    try:
        data = json.loads(likes_file(directory).read_text(encoding="utf-8"))
        if data.get("full_path") != str(directory.resolve()):
            return set()
        return {name for name in data.get("likes", []) if isinstance(name, str)}
    except (OSError, json.JSONDecodeError, AttributeError):
        return set()


def save_likes(directory: Path, likes: set[str]) -> None:
    VIEWER_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"full_path": str(directory.resolve()), "likes": sorted(likes, key=str.lower)}
    likes_file(directory).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def clear_likes(directory: Path) -> None:
    try:
        likes_file(directory).unlink()
    except FileNotFoundError:
        pass

