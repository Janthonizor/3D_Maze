from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class EndScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.create_widgets()
        self.create_layout()


    def create_widgets(self):

        self.end_label = QLabel(
            "End"
        )

        self.end_label.setAlignment(
            Qt.AlignCenter
        )


        self.return_button = QPushButton(
            "Return to Main Menu"
        )

        self.return_button.setFixedSize(
            200,
            60
        )


    def create_layout(self):

        self.end_screen_layout = QVBoxLayout()


        self.end_screen_layout.addWidget(
            self.end_label,
            alignment=Qt.AlignCenter
        )

        self.end_screen_layout.addWidget(
            self.return_button,
            alignment=Qt.AlignCenter
        )


        self.setLayout(
            self.end_screen_layout
        )