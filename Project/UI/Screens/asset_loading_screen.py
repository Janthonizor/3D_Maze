from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class AssetLoadingScreen(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        self.asset_loading_label = QLabel(
            "Loading Assets..."
        )

        self.asset_loading_info = QLabel(
            "..."
        )

        self.asset_loading_label.setAlignment(
            Qt.AlignCenter
        )

        self.asset_loading_info.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.asset_loading_info
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


    def update_text(self, text):

        self.asset_loading_info.setText(
            text
        )