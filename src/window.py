from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from src.config import COLORS
from src.favorites import load_favorites
from src.frame import ViewerFrame


class ViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Viewer")
        self.resize(1280, 832)
        self.setMinimumSize(640, 420)
        self.favorites = load_favorites()
        self.frames: list[ViewerFrame] = []
        central = QWidget()
        central.setStyleSheet(f"background: {COLORS['window']};")
        self.row = QHBoxLayout(central)
        self.row.setContentsMargins(0, 0, 0, 0)
        self.row.setSpacing(0)
        self.setCentralWidget(central)
        self.add_frame()

    def add_frame(self, after: ViewerFrame | None = None):
        frame = ViewerFrame(self, str(after.directory) if after else None)
        frame.request_new.connect(self.add_frame)
        frame.request_close.connect(self.close_frame)
        index = self.frames.index(after) + 1 if after in self.frames else len(self.frames)
        self.frames.insert(index, frame)
        self.row.insertWidget(index, frame, 1)
        self._equalize()

    def close_frame(self, frame: ViewerFrame):
        if len(self.frames) == 1:
            return
        self.frames.remove(frame)
        self.row.removeWidget(frame)
        frame.deleteLater()
        self._equalize()

    def _equalize(self):
        for i in range(self.row.count()):
            self.row.setStretch(i, 1)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Viewer")
    app.setFont(QFont("Segoe UI", 9))
    window = ViewerWindow()
    window.show()
    sys.exit(app.exec())
