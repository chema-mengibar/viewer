from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLineEdit, QPushButton, QWidget

from src.config import COLORS
from src.icons import icon


class FrameHeader(QWidget):
    favorites_requested = Signal()
    folder_requested = Signal()
    layout_requested = Signal()
    options_requested = Signal()
    deep_loop_changed = Signal(bool)
    path_submitted = Signal(str)

    def __init__(self, directory: Path):
        super().__init__()
        self.setFixedHeight(33)
        bar = QHBoxLayout(self)
        bar.setContentsMargins(5, 8, 5, 8)
        bar.setSpacing(5)

        self.favorites_button = self._tool("star", self.favorites_requested.emit)
        self.folder_button = self._tool("folder", self.folder_requested.emit)
        self.showDeepLoop = QCheckBox("deep loop")
        self.showDeepLoop.setFixedHeight(17)
        self.showDeepLoop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.showDeepLoop.setStyleSheet(self.control_css() + " padding: 0 4px;")
        self.showDeepLoop.toggled.connect(self.deep_loop_changed.emit)
        self.path = QLineEdit(str(directory))
        self.path.setFixedHeight(17)
        self.path.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.path.returnPressed.connect(lambda: self.path_submitted.emit(self.path.text()))
        self.path.setStyleSheet(self.control_css())
        self.layout_button = self._tool("grid", self.layout_requested.emit)
        self.options_button = self._tool("ellipsis", self.options_requested.emit)

        for widget in (self.favorites_button, self.folder_button, self.showDeepLoop, self.path, self.layout_button, self.options_button):
            bar.addWidget(widget)

    @staticmethod
    def control_css():
        return f"background: {COLORS['control']}; color: {COLORS['text']}; border: 1px solid {COLORS['border']}; border-radius: 2px; font-size: 10px;"

    def mark_invalid_path(self) -> None:
        self.path.setStyleSheet(self.control_css() + f" QLineEdit {{ border-color: {COLORS['danger']}; }}")

    def set_path(self, path: Path) -> None:
        self.path.setText(str(path))
        self.path.setStyleSheet(self.control_css())

    def _tool(self, icon_name: str, slot, danger: bool = False):
        button = QPushButton()
        button.setIcon(icon(icon_name))
        button.setIconSize(QSize(12, 12))
        button.setFixedSize(25, 17)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(self.control_css().replace(COLORS["control"], COLORS["danger"] if danger else COLORS["control"]))
        button.clicked.connect(slot)
        return button
