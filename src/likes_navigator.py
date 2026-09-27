from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget

from src.config import COLORS


class LikesNavigator(QWidget):
    image_requested = Signal(int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._liked: list[bool] = []
        self._scroll_value = 0
        self._scroll_maximum = 0
        self._page_step = 0

    def set_images(self, liked: list[bool]) -> None:
        self._liked = liked
        self.update()

    def set_scroll(self, value: int, maximum: int, page_step: int) -> None:
        self._scroll_value, self._scroll_maximum, self._page_step = value, maximum, page_step
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        count = len(self._liked)
        if not count:
            return
        slot = self.height() / count
        line_height = max(1.0, min(2.0, slot * 0.55))
        for index, liked in enumerate(self._liked):
            painter.fillRect(0, round(index * slot + (slot - line_height) / 2), self.width(), max(1, round(line_height)), QColor(COLORS["like"] if liked else COLORS["unliked"]))

        document = self._scroll_maximum + self._page_step
        if document > 0:
            overlay_height = max(10, round(self.height() * self._page_step / document))
            travel = max(0, self.height() - overlay_height)
            top = round(travel * self._scroll_value / max(1, self._scroll_maximum))
            painter.fillRect(0, top, self.width(), overlay_height, QColor(0, 0, 0, 105))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._liked:
            index = min(len(self._liked) - 1, int(event.position().y() * len(self._liked) / max(1, self.height())))
            self.image_requested.emit(index)
        super().mousePressEvent(event)
