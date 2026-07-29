from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QSizePolicy
)

from PyQt5.QtGui import QPainter, QColor

from PyQt5.QtCore import Qt


class MenuOverlay(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )
        self.setAutoFillBackground(
            True
        )
    


        self.setStyleSheet(
            """
            QWidget {
                background-color:black;
            }
            QPushButton {
                background-color: rgb(120, 120, 120);
                color: white;
                border: 1px solid rgb(170, 170, 170);
                border-radius: 6px;
                font-size: 20px;
                font-weight: bold;
                padding: 10px 20px;
                min-width: 240px;
            }

            QPushButton:hover {
                background-color: rgb(245, 245, 245);
                color: black;
                border: 1px solid rgb(255, 255, 255);
            }

            QPushButton:pressed {
                background-color: rgb(200, 200, 200);
            }
            """
        )


        self.create_widgets()
        self.create_layout()


    def create_widgets(self):

        self.resume_button = QPushButton("Resume")
        self.save_button = QPushButton("Save")
        self.settings_button = QPushButton("Settings")
        self.quit_button = QPushButton("Quit to Main Menu")

        buttons = (
            self.resume_button,
            self.save_button,
            self.settings_button,
            self.quit_button,
        )

    def create_layout(self):

        layout = QVBoxLayout()

        layout.addWidget(
            self.resume_button
        )

        layout.addWidget(
            self.save_button
        )

        layout.addWidget(
            self.settings_button
        )

        layout.addWidget(
            self.quit_button
        )


        layout.setAlignment(
            Qt.AlignCenter
        )

        self.setLayout(
            layout
        )
  