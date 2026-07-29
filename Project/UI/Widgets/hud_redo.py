from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy
)

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt

from .maze_widget import MazeWidget
from .orientation_widget import OrientationWidget
from .inventory_slot import InventorySlot
from .stats_panel import StatsPanel


class HUD(QWidget):

    def __init__(self, parent=None):

        super().__init__()

        self.maze_map = None


        # ==================================================
        # Widget Initializations
        # ==================================================

        self.layout = QVBoxLayout()


        self.maze_widget = MazeWidget(
            self
        )


        self.orientation_widget = OrientationWidget(
            self
        )


        self.inventory = QWidget(
            self
        )


        self.inventory_layout = QGridLayout()


        self.inventory_slots = []

        self.selected_inventory_slot = None


        self.stats_panel = StatsPanel()



        # ==================================================
        # Palette / Background
        # ==================================================

        palette = self.palette()

        palette.setColor(
            QPalette.Window,
            Qt.black
        )

        self.setPalette(
            palette
        )

        self.setAutoFillBackground(
            True
        )


        # ==================================================
        # Layout Configuration
        # ==================================================

        self.setLayout(
            self.layout
        )


        self.layout.setContentsMargins(
            5,
            5,
            5,
            5
        )


        self.layout.setSpacing(
            5
        )


        self.layout.setAlignment(
            Qt.AlignVCenter | Qt.AlignHCenter
        )


        self.inventory.setLayout(
            self.inventory_layout
        )


        self.inventory_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )


        self.inventory_layout.setHorizontalSpacing(
            10
        )


        self.inventory_layout.setVerticalSpacing(
            10
        )


        self.maze_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.orientation_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.inventory.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.stats_panel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )


        # ==================================================
        # Inventory
        # ==================================================

        for row in range(2):

            for col in range(3):

                slot = InventorySlot(
                    self.inventory
                )


                slot.clicked.connect(
                    self.select_inventory_slot
                )


                self.inventory_slots.append(
                    slot
                )


                self.inventory_layout.addWidget(
                    slot,
                    row,
                    col
                )


        for row in range(2):

            self.inventory_layout.setRowStretch(
                row,
                1
            )


        for col in range(3):

            self.inventory_layout.setColumnStretch(
                col,
                1
            )


        self.inventory.setStyleSheet(
            """
            QWidget {
                background-color: black;
            }
            """
        )


        # ==================================================
        # Add Widgets
        # ==================================================

        self.layout.addWidget(
            self.maze_widget,
            stretch=10
        )


        self.layout.addWidget(
            self.orientation_widget,
            stretch=10
        )


        self.layout.addWidget(
            self.inventory,
            stretch=8
        )


        self.layout.addWidget(
            self.stats_panel
        )



    # ==================================================
    # Inventory Selection
    # ==================================================

    def clear_inventory_selection(self):

        if self.selected_inventory_slot:

            self.selected_inventory_slot.set_selected(
                False
            )

            self.selected_inventory_slot = None



    def select_inventory_slot(self, slot):

        # Toggle off selected slot
        if self.selected_inventory_slot == slot:

            slot.set_selected(
                False
            )

            self.selected_inventory_slot = None

            return


        # Remove previous selection

        if self.selected_inventory_slot:

            self.selected_inventory_slot.set_selected(
                False
            )


        # Select new slot

        self.selected_inventory_slot = slot

        slot.set_selected(
            True
        )



    def set_inventory_mode(self, enabled):

        if enabled:

            self.inventory.setStyleSheet(
                """
                QWidget {
                    background-color: white;
                }
                """
            )

        else:

            self.inventory.setStyleSheet(
                """
                QWidget {
                    background-color: black;
                }
                """
            )

            self.clear_inventory_selection()



    # ==================================================
    # Inventory Items
    # ==================================================

    def add_item(self, item):

        for slot in self.inventory_slots:

            if not slot.has_item():

                slot.set_item(
                    item
                )

                return True


        return False



    # ==================================================
    # Initialization
    # ==================================================

    def initialize(
        self,
        maze_map,
        player_frame
    ):

        self.maze_map = maze_map


        self.maze_widget.initialize_widget(
            maze_map
        )


        self.orientation_widget.update_widget(
            player_frame
        )



    # ==================================================
    # Update
    # ==================================================

    def update_hud(
        self,
        maze_map,
        player_node_id,
        player_frame
    ):

        self.maze_widget.update_widget(
            maze_map,
            player_node_id
        )


        self.orientation_widget.update_widget(
            player_frame
        )



    # ==================================================
    # Cleanup
    # ==================================================

    def cleanup(self):

        self.maze_widget.deleteLater()

        self.orientation_widget.deleteLater()