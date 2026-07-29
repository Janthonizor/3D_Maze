from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QProgressBar,
    QLabel,
    QHBoxLayout,
    QStyleFactory
)

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

        self.health = self.create_bar(
            "Health",
            100,
            "red"
        )

        self.hunger = self.create_bar(
            "Hunger",
            85,
            "orange"
        )

        self.stamina = self.create_bar(
            "Stamina",
            100,
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

        bar = QProgressBar()

        bar.setStyle(
            QStyleFactory.create("Fusion")
        )

        bar.setRange(
            0,
            100
        )

        bar.setValue(
            value
        )

        bar.setTextVisible(
            False
        )

        palette = bar.palette()

        palette.setColor(
            QPalette.Highlight,
            QColor(color)
        )

        palette.setColor(
            QPalette.Active,
            QPalette.Highlight,
            QColor(color)
        )

        palette.setColor(
            QPalette.Inactive,
            QPalette.Highlight,
            QColor(color)
        )

        bar.setPalette(
            palette
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

        return layout