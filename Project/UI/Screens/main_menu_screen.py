from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSlider,
    QLineEdit
)

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter
import hashlib
import time
import random

class MainMenuScreen(QWidget):

    start_game_signal = pyqtSignal(dict)


    def __init__(self):

        super().__init__()

        self.create_layout()



    def create_layout(self):

        self.setStyleSheet(
            """
            QWidget {
                background-color: black;
            }

            QLabel {
                color: white;
                font-size: 24px;
            }

            QPushButton {
                background-color: white;
                color: black;
                border-radius: 8px;
                font-size: 18px;
            }

            QPushButton:hover {
                background-color: gray;
            }

            QComboBox {
                background-color: white;
                color: black;
                font-size: 16px;
                padding: 5px;
            }

            QComboBox QAbstractItemView {
                background-color: gray;
                color: white;
                selection-background-color: black;
                selection-color: white;
            }

            QLineEdit {
                background-color: white;
                color: black;
                font-size: 16px;
                padding: 5px;
            }

            QSlider::groove:horizontal {
                height: 6px;
                background: white;
            }

            QSlider::handle:horizontal {
                width: 15px;
                background: gray;
            }
            """
        )


        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            50,
            50,
            50,
            50
        )

        main_layout.setSpacing(
            40
        )


        title = QLabel(
            "Maze Explorer"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        main_layout.addWidget(
            title
        )


        bottom_layout = QHBoxLayout()

        bottom_layout.setSpacing(
            100
        )


        # -------------------------
        # Settings
        # -------------------------

        settings_layout = QVBoxLayout()

        settings_layout.setSpacing(
            15
        )


        self.n_dropdown = QComboBox()

        self.n_dropdown.addItems(
            [
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10"
            ]
        )


        self.seed_box = QLineEdit()

        self.seed_box.setPlaceholderText(
            "Random seed"
        )


        self.branch_slider = QSlider(
            Qt.Horizontal
        )

        self.branch_slider.setMinimum(0)
        self.branch_slider.setMaximum(100)
        self.branch_slider.setValue(75)


        settings_layout.addWidget(
            QLabel("Maze Size (N)")
        )

        settings_layout.addWidget(
            self.n_dropdown
        )

        settings_layout.addWidget(
            QLabel("Seed")
        )

        settings_layout.addWidget(
            self.seed_box
        )

        settings_layout.addWidget(
            QLabel("Branchiness")
        )

        settings_layout.addWidget(
            self.branch_slider
        )


        # -------------------------
        # Start button
        # -------------------------

        button_layout = QVBoxLayout()

        self.start_button = QPushButton(
            "Start Game"
        )

        self.start_button.setFixedSize(
            250,
            100
        )

        self.start_button.clicked.connect(
            self.emit_start_game
        )


        button_layout.addStretch()

        button_layout.addWidget(
            self.start_button,
            alignment=Qt.AlignCenter
        )

        button_layout.addStretch()


        bottom_layout.addLayout(
            settings_layout,
            stretch=1
        )

        bottom_layout.addLayout(
            button_layout,
            stretch=1
        )


        main_layout.addLayout(
            bottom_layout,
            stretch=3
        )


        self.setLayout(
            main_layout
        )


    def emit_start_game(self):

        seed_text = self.seed_box.text()


        if seed_text == "":
            seed = int(
                time.time_ns()
            )

        else:
            try:
                seed = int(seed_text)

            except ValueError:
                seed = int(
                    hashlib.sha256(seed_text.encode()).hexdigest()[:8],
                    16
                )


        settings = {

            "N":
                int(self.n_dropdown.currentText()),

            "grid_spacing":
                8,

            "branchiness":
                self.branch_slider.value(),

            "seed":
                seed
        }


        self.start_game_signal.emit(
            settings
        )

        def paintEvent(self, event):

            painter = QPainter(self)

            painter.fillRect(
                self.rect(),
                Qt.black
            )

            super().paintEvent(event)