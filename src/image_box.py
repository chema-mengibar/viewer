from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QLayout, QVBoxLayout, QWidget

from src.config import COLORS
from src.icons import icon


class FlowLayout(QLayout):
    """Small wrapping layout used by the gallery."""

    def __init__(self, parent: QWidget | None = None, margin: int = 5, spacing: int = 0):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._arrange(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._arrange(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        return size + QSize(margins.left() + margins.right(), margins.top() + margins.bottom())

    def _arrange(self, rect: QRect, test_only: bool) -> int:
        margins = self.contentsMargins()
        x, y = rect.x() + margins.left(), rect.y() + margins.top()
        line_height = 0
        right = rect.right() - margins.right()
        for item in self._items:
            hint = item.sizeHint()
            if x + hint.width() > right + 1 and line_height:
                x, y = rect.x() + margins.left(), y + line_height + self.spacing()
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x += hint.width() + self.spacing()
            line_height = max(line_height, hint.height())
        return y + line_height + margins.bottom() - rect.y()


class ImageBox(QFrame):
    double_clicked = Signal(object)

    def __init__(self, path: Path, size: int, show_name: bool, expanded: bool = False, liked: bool = False):
        super().__init__()
        self.path = path
        self.tile_size = size
        self.expanded = expanded
        self.setObjectName("imageTile")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.image = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.image.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.image)
        self.like_badge = QLabel(self)
        self.like_badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.like_badge.setFixedSize(20, 20)
        self.like_badge.setStyleSheet("background: rgba(0,0,0,160); border: none; border-radius: 10px;")
        self.like_icon = QLabel(self.like_badge)
        self.like_icon.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.like_icon.setFixedSize(12, 12)
        self.like_icon.setStyleSheet("border: none; background: transparent;")
        self.like_icon.setPixmap(self._tinted_pixmap("like", QSize(12, 12), COLORS["like"]))
        self.name = QLabel(path.name, self)
        self.name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.name.setVisible(show_name)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setStyleSheet(f"background: rgba(0,0,0,160); color: {COLORS['text']}; padding: 3px; border: none;")
        self._source = QPixmap(str(path))
        self.set_liked(liked)
        self.refresh(size, expanded)

    def set_liked(self, liked: bool) -> None:
        self.liked = liked
        color = COLORS["like"] if liked else COLORS["border"]
        self.setStyleSheet(f"QFrame#imageTile {{ border: 1px solid {color}; background: {COLORS['frame']}; }}")
        self.like_badge.setVisible(liked)
        self.like_badge.raise_()

    @staticmethod
    def _tinted_pixmap(icon_name: str, size: QSize, color: str) -> QPixmap:
        pixmap = icon(icon_name).pixmap(size)
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color))
        painter.end()
        return tinted

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.path)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._reveal_native()
            else:
                self._open_native()
            event.accept()
            return
        super().mousePressEvent(event)

    def _open_native(self) -> None:
        path = self.path.resolve()
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    def _reveal_native(self) -> None:
        path = self.path.resolve()
        if sys.platform == "win32":
            subprocess.Popen(f'explorer.exe /select,"{path}"')
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path.parent)])

    def refresh(self, size: int, expanded: bool) -> None:
        self.tile_size, self.expanded = size, expanded
        if expanded:
            width = max(100, self.parentWidget().width() - 12) if self.parentWidget() else 600
            ratio = self._source.height() / max(1, self._source.width())
            height = max(80, round(width * ratio))
            self.setFixedSize(width, height)
        else:
            self.setFixedSize(size, size)
        target = self.size() - QSize(2, 2)
        self.image.setPixmap(
            self._source.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.name.setGeometry(1, max(1, self.height() - 24), max(1, self.width() - 2), 23)
        self._position_overlays()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_overlays()

    def _position_overlays(self) -> None:
        self.name.setGeometry(1, max(1, self.height() - 24), max(1, self.width() - 2), 23)
        self.like_badge.move(max(1, self.width() - self.like_badge.width() - 5), 5)
        self.like_icon.move(
            round((self.like_badge.width() - self.like_icon.width()) / 2),
            round((self.like_badge.height() - self.like_icon.height()) / 2),
        )
        self.like_badge.raise_()
