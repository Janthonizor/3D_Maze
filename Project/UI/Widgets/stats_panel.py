from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QProgressBar,
    QLabel,
    QHBoxLayout,
    QStyleFactory
)
from .smooth_bar import SmoothBar

from PyQt5.QtGui import QColor, QPalette


class StatsPanel(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        # --------------------------------------------------
        # Shared label width
        # --------------------------------------------------

        titles = [
            "Health",
            "Hunger",
            "Stamina"
        ]

        self.label_width = max(
            QLabel(title).sizeHint().width()
            for title in titles
        )

        # --------------------------------------------------
        # Layout
        # --------------------------------------------------

        layout = QVBoxLayout()

        self.health, self.health_bar = self.create_bar(
            "Health",
            1000,
            "red"
        )

        self.hunger, self.hunger_bar = self.create_bar(
            "Hunger",
            1000,
            "orange"
        )

        self.stamina, self.stamina_bar = self.create_bar(
            "Stamina",
            1000,
            "cyan"
        )

        layout.addLayout(
            self.health
        )

        layout.addLayout(
            self.hunger
        )

        layout.addLayout(
            self.stamina
        )

        self.setLayout(
            layout
        )


    def create_bar(
        self,
        title,
        value,
        color
    ):

        layout = QHBoxLayout()

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            10
        )

        # --------------------------------------------------
        # Progress Bar
        # --------------------------------------------------

        bar = SmoothBar(color)

        bar.setValue(
            value
        )
    
        # --------------------------------------------------
        # Label
        # --------------------------------------------------

        label = QLabel(
            title
        )

        label.setFixedWidth(
            self.label_width
        )

        label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 16px;
            }
            """
        )

        # --------------------------------------------------
        # Layout
        # --------------------------------------------------

        layout.addWidget(
            bar,
            stretch=1
        )

        layout.addWidget(
            label
        )

        return layout, bar