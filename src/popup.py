from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget

from src.config import COLORS
from src.icons import icon


class Popup(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(167, 227)
        self.setStyleSheet(f"QFrame {{ background: {COLORS['window']}; border: 1px solid {COLORS['popup_border']}; }}")
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(10, 17, 10, 17)
        self.box.setSpacing(10)
        self.box.setAlignment(Qt.AlignmentFlag.AlignTop)

    def action(self, icon_name: str, text: str, slot, danger: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setIcon(icon(icon_name))
        button.setIconSize(QSize(12, 12))
        button.setFixedHeight(19)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            f"QPushButton {{ background: {COLORS['danger'] if danger else COLORS['control']}; color: {COLORS['text']}; "
            "border: none; border-radius: 2px; padding: 0 10px; text-align: left; font-size: 10px; }} "
            "QPushButton:hover { background: #5a5a5a; }"
        )
        button.clicked.connect(slot)
        self.box.addWidget(button)
        return button

    def separator(self):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet("background: rgba(255,255,255,145); border: none;")
        self.box.addWidget(line)
