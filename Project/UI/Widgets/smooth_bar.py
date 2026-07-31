from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt


class SmoothBar(QWidget):

    def __init__(self, color="cyan"):
        super().__init__()

        self.value = 1.0
        self.color = QColor(color)

        self.setMinimumHeight(12)


    def setValue(self, value):

        self.value = max(
            0.01,
            min(1.0, value)
        )

        self.update()


    def paintEvent(self, event):

        painter = QPainter(self)

        # background
        painter.setBrush(
            QColor(30,30,30)
        )

        painter.drawRoundedRect(
            self.rect(),
            6,
            6
        )

        # fill
        width = int(
            self.width() * self.value
        )

        painter.setBrush(
            self.color
        )

        painter.drawRoundedRect(
            0,
            0,
            width,
            self.height(),
            6,
            6
        )