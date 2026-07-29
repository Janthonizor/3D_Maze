from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QSizePolicy
)

from PyQt5.QtCore import Qt

from .inventory_slot import InventorySlot


class InventoryPanel(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.inventory_slots = []
        self.setObjectName("InventoryPanel")
        self.setFocusPolicy(
            Qt.NoFocus
        )
        self.selected_inventory_slot = None


        self.layout = QGridLayout()

        self.setLayout(
            self.layout
        )


        self.layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.layout.setHorizontalSpacing(
            10
        )

        self.layout.setVerticalSpacing(
            10
        )


        self.create_slots()


        self.set_inventory_mode(
            False
        )


    def create_slots(self):

        for row in range(2):

            for col in range(3):

                slot = InventorySlot(
                    self
                )

                slot.clicked.connect(
                    self.select_inventory_slot
                )


                self.inventory_slots.append(
                    slot
                )


                self.layout.addWidget(
                    slot,
                    row,
                    col
                )


            for row in range(2):

                self.layout.setRowStretch(
                    row,
                    1
                )


            for col in range(3):

                self.layout.setColumnStretch(
                    col,
                    1
                )


            # Select first slot by default
            self.selected_inventory_slot = self.inventory_slots[0]

            self.selected_inventory_slot.set_selected(
                True
            )
            
    def select_inventory_slot(self, slot):

        # Already selected -> do nothing
        if self.selected_inventory_slot == slot:
            return

        if self.selected_inventory_slot:
            self.selected_inventory_slot.set_selected(False)

        self.selected_inventory_slot = slot
        slot.set_selected(True)





    def add_item(self, item):

        for slot in self.inventory_slots:

            if not slot.has_item():

                slot.set_item(
                    item
                )

                return True


        return False



    def set_inventory_mode(self, enabled):

        if enabled:

            self.setStyleSheet(
                """
                #InventoryPanel {
                    background-color: white;
                }
                """
            )

        else:
            self.setStyleSheet(
                """
                #InventoryPanel {
                    background-color: black;
                }
                """
            )