from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class LevelLoadingScreen(QWidget):

    def __init__(self):

        super().__init__()

        self.label = QLabel(
            "Loading Maze..."
        )

        self.create_layout()


    def create_layout(self):

        layout = QVBoxLayout()


        self.label.setAlignment(
            Qt.AlignCenter
        )


        self.setStyleSheet(
            """
            QWidget {
                background-color: black;
            }

            QLabel {
                color: white;
                font-size: 24px;
            }
            """
        )


        layout.addWidget(
            self.label
        )


        self.setLayout(
            layout
        )


    def set_text(self, text):

        self.label.setText(
            text
        )