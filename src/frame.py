from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QTimer, Qt, Signal
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from src.config import COLORS, IMAGE_EXTENSIONS
from src.favorites import save_favorites
from src.frame_header import FrameHeader
from src.image_box import FlowLayout, ImageBox
from src.likes import clear_likes, load_likes, save_likes
from src.likes_navigator import LikesNavigator
from src.popup import Popup


class Gallery(QScrollArea):
    resized = Signal(int)

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(f"QScrollArea {{ background: {COLORS['frame']}; border: none; }}")
        self.content = QWidget()
        self.content.setStyleSheet(f"background: {COLORS['frame']};")
        self.flow = FlowLayout(self.content)
        self.setWidget(self.content)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.resized.emit(20 if event.angleDelta().y() > 0 else -20)
            event.accept()
        else:
            super().wheelEvent(event)


class ViewerFrame(QFrame):
    request_new = Signal(object)
    request_close = Signal(object)

    def __init__(self, window: "ViewerWindow", directory: str | None = None):
        super().__init__()
        self.window = window
        self.directory = Path(directory) if directory and Path(directory).is_dir() else Path.home()
        self.tile_size = 250
        self.expanded = False
        self.show_names = False
        self.show_likes_navigator = True
        self.show_only_liked = False
        self.sort_by_likes = False
        self.showDeepLoop = False
        self.likes: set[str] = set()
        self.tiles: list[ImageBox] = []
        self.setStyleSheet(f"background: {COLORS['frame']};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.header = FrameHeader(self.directory)
        self.header.favorites_requested.connect(self.show_favorites)
        self.header.folder_requested.connect(self.choose_directory)
        self.header.layout_requested.connect(self.show_layout)
        self.header.options_requested.connect(self.show_options)
        self.header.deep_loop_changed.connect(self.toggle_deep_loop)
        self.header.path_submitted.connect(self.set_directory)
        root.addWidget(self.header)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)
        self.likes_navigator = LikesNavigator()
        self.likes_navigator.image_requested.connect(self.scroll_to_image)
        body_layout.addWidget(self.likes_navigator)
        self.gallery = Gallery()
        self.gallery.resized.connect(self.resize_tiles)
        scroll_bar = self.gallery.verticalScrollBar()
        scroll_bar.valueChanged.connect(self.update_navigator_scroll)
        scroll_bar.rangeChanged.connect(lambda _minimum, _maximum: self.update_navigator_scroll())
        body_layout.addWidget(self.gallery, 1)
        root.addWidget(body, 1)
        self.set_directory(str(self.directory))

    def choose_directory(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select image directory", str(self.directory))
        if chosen:
            self.set_directory(chosen)

    def set_directory(self, value: str):
        directory = Path(value.strip().strip('"')).expanduser()
        if not directory.is_dir():
            self.header.mark_invalid_path()
            return
        self.directory = directory.resolve()
        self.header.set_path(self.directory)
        self.likes = load_likes(self.directory)
        self.reload()

    def reload(self, preserve_scroll: bool = False):
        scroll_bar = self.gallery.verticalScrollBar()
        scroll_position = scroll_bar.value() if preserve_scroll else 0
        while self.gallery.flow.count():
            item = self.gallery.flow.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        try:
            files = sorted(self._image_files(), key=lambda p: str(p.relative_to(self.directory)).lower())
        except OSError:
            files = []
        self.likes.intersection_update(p.name for p in files)
        if self.show_only_liked:
            files = [p for p in files if p.name in self.likes]
        if self.sort_by_likes:
            files.sort(key=lambda p: (p.name not in self.likes, p.name.lower()))
        self.tiles = [ImageBox(p, self.tile_size, self.show_names, self.expanded, p.name in self.likes) for p in files]
        for tile in self.tiles:
            tile.double_clicked.connect(self.toggle_like)
            self.gallery.flow.addWidget(tile)
        self.gallery.content.adjustSize()
        self.likes_navigator.set_images([tile.liked for tile in self.tiles])
        QTimer.singleShot(0, lambda: self._restore_after_reload(scroll_position) if preserve_scroll else self.update_navigator_scroll())

    def _restore_after_reload(self, scroll_position: int) -> None:
        bar = self.gallery.verticalScrollBar()
        bar.setValue(min(scroll_position, bar.maximum()))
        self.update_navigator_scroll()

    def resize_tiles(self, delta: int):
        if self.expanded:
            return
        self.tile_size = min(500, max(80, self.tile_size + delta))
        for tile in self.tiles:
            tile.refresh(self.tile_size, False)
        self.gallery.content.adjustSize()

    def show_popup(self, popup: Popup, anchor: QPushButton):
        pos = anchor.mapToGlobal(QPoint(anchor.width() - popup.width(), anchor.height() + 4))
        popup.move(pos)
        popup.show()

    def show_favorites(self):
        popup = Popup(self)
        if not self.window.favorites:
            empty = QLabel("No favorites saved")
            empty.setStyleSheet(f"color: {COLORS['text']}; border: none; font-size: 10px;")
            popup.box.addWidget(empty)
        for path in self.window.favorites:
            name = "..." + path[-18:] if len(path) > 18 else path
            popup.action("folder", name, lambda checked=False, p=path: (self.set_directory(p), popup.close()))
        self.show_popup(popup, self.header.favorites_button)

    def show_layout(self):
        popup = Popup(self)
        popup.action("grid", "Grid", lambda: (self.set_layout(False), popup.close()))
        popup.action("open", "Expand width", lambda: (self.set_layout(True), popup.close()))
        self.show_popup(popup, self.header.layout_button)

    def set_layout(self, expanded: bool):
        self.expanded = expanded
        for tile in self.tiles:
            tile.refresh(self.tile_size, expanded)
        self.gallery.content.adjustSize()

    def show_options(self):
        popup = Popup(self)
        popup.setFixedHeight(380)
        fav = str(self.directory) in self.window.favorites
        popup.action("star", "Remove favorite" if fav else "Save as favorite", lambda: (self.toggle_favorite(), popup.close()))
        popup.action("close", "Close frame", lambda: (popup.close(), self.request_close.emit(self)), True)
        popup.separator()
        popup.action("open", "Open in windows", lambda: (self.open_in_windows(), popup.close()))
        popup.action("eye", "Hide images name" if self.show_names else "Show images name", lambda: (self.toggle_names(), popup.close()))
        popup.separator()
        popup.action("eye", "all images" if self.show_only_liked else "liked images", lambda: (self.toggle_show_only_liked(), popup.close()))
        popup.action("like", "Hide likes navigator" if self.show_likes_navigator else "Show likes navigator", lambda: (self.toggle_likes_navigator(), popup.close()))
        popup.action("likes-sort", "Default order" if self.sort_by_likes else "Sort by likes", lambda: (self.toggle_sort_by_likes(), popup.close()))
        popup.action("trash", "Clear directory likes", lambda: (self.clear_directory_likes(), popup.close()), True)
        popup.separator()
        popup.action("grid", "New frame", lambda: (popup.close(), self.request_new.emit(self)))
        self.show_popup(popup, self.header.options_button)

    def toggle_favorite(self):
        path = str(self.directory)
        if path in self.window.favorites:
            self.window.favorites.remove(path)
        else:
            self.window.favorites.append(path)
        save_favorites(self.window.favorites)

    def toggle_names(self):
        self.show_names = not self.show_names
        for tile in self.tiles:
            tile.name.setVisible(self.show_names)

    def toggle_like(self, path: Path) -> None:
        if path.name in self.likes:
            self.likes.remove(path.name)
        else:
            self.likes.add(path.name)
        save_likes(self.directory, self.likes)
        for tile in self.tiles:
            if tile.path == path:
                tile.set_liked(path.name in self.likes)
                break
        if self.sort_by_likes or self.show_only_liked:
            self.reload(preserve_scroll=True)
        else:
            self.likes_navigator.set_images([tile.liked for tile in self.tiles])

    def clear_directory_likes(self) -> None:
        clear_likes(self.directory)
        self.likes.clear()
        if self.show_only_liked:
            self.reload(preserve_scroll=True)
        else:
            for tile in self.tiles:
                tile.set_liked(False)
            self.likes_navigator.set_images([False] * len(self.tiles))

    def toggle_likes_navigator(self) -> None:
        self.show_likes_navigator = not self.show_likes_navigator
        self.likes_navigator.setVisible(self.show_likes_navigator)

    def toggle_show_only_liked(self) -> None:
        self.show_only_liked = not self.show_only_liked
        self.reload(preserve_scroll=True)

    def toggle_sort_by_likes(self) -> None:
        self.sort_by_likes = not self.sort_by_likes
        self.reload(preserve_scroll=True)

    def toggle_deep_loop(self, checked: bool) -> None:
        self.showDeepLoop = checked
        self.reload(preserve_scroll=True)

    def _image_files(self) -> list[Path]:
        if not self.showDeepLoop:
            return [p for p in self.directory.iterdir() if self._is_image_file(p)]

        files: list[Path] = []
        pending: list[tuple[Path, int]] = [(self.directory, 0)]
        while pending:
            directory, depth = pending.pop(0)
            try:
                children = list(directory.iterdir())
            except OSError:
                continue
            for path in children:
                if self._is_image_file(path):
                    files.append(path)
                elif path.is_dir() and depth < 2:
                    pending.append((path, depth + 1))
        return files

    @staticmethod
    def _is_image_file(path: Path) -> bool:
        return path.is_file() and path.suffix.lower().lstrip(".") in IMAGE_EXTENSIONS

    def scroll_to_image(self, index: int) -> None:
        if 0 <= index < len(self.tiles):
            self.gallery.ensureWidgetVisible(self.tiles[index], 0, 0)

    def update_navigator_scroll(self) -> None:
        bar = self.gallery.verticalScrollBar()
        self.likes_navigator.set_scroll(bar.value(), bar.maximum(), bar.pageStep())

    def open_in_windows(self):
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(self.directory)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(self.directory)])
        else:
            subprocess.Popen(["xdg-open", str(self.directory)])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_navigator_scroll()
        if self.expanded:
            for tile in self.tiles:
                tile.refresh(self.tile_size, True)
