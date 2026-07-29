from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt


class InventorySlot(QLabel):

    clicked = pyqtSignal(object)


    def __init__(self, parent=None):

        super().__init__(parent)

        self.item = None
        self.selected = False


        self.setAlignment(
            Qt.AlignCenter
        )
        self.setFocusPolicy(
            Qt.NoFocus
        )
        self.setAttribute(
            Qt.WA_TransparentForMouseEvents,
            False
        )


    
        self.setMinimumSize(
            40,
            40
        )


        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.setStyleSheet(
            """
            QLabel {
                background-color: black;
                border: 1px solid white;
            }
            """
        )


    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.clicked.emit(
                self
            )

        super().mousePressEvent(event)



    def set_selected(self, selected):

        self.selected = selected


        if selected:

            self.setStyleSheet(
                """
                QLabel {
                    background-color: black;
                    border: 3px solid red;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QLabel {
                    background-color: black;
                    border: 1px solid white;
                }
                """
            )


    def set_item(self, item):

        self.item = item

        if item:

            self.setText(
                str(item)
            )

        else:

            self.setText(
                ""
            )


    def clear_item(self):

        self.item = None

        self.setText(
            ""
        )


    def has_item(self):

        return self.item is not None