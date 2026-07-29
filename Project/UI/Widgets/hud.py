from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSizePolicy
)

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt


from .maze_widget import MazeWidget
from .orientation_widget import OrientationWidget
from .inventory_panel import InventoryPanel
from .stats_panel import StatsPanel



class HUD(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.maze_map = None


        self.layout = QVBoxLayout()

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


        # -----------------------------
        # Background
        # -----------------------------

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


        # -----------------------------
        # Widgets
        # -----------------------------

        self.maze_widget = MazeWidget(
            self
        )


        self.orientation_widget = OrientationWidget(
            self
        )


        self.inventory_panel = InventoryPanel(
            self
        )


        self.stats_panel = StatsPanel(
            self
        )


        # -----------------------------
        # Size policies
        # -----------------------------

        self.maze_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.orientation_widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.inventory_panel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        # -----------------------------
        # Layout
        # -----------------------------

        self.layout.addWidget(
            self.maze_widget,
            stretch=10
        )


        self.layout.addWidget(
            self.orientation_widget,
            stretch=10
        )


        self.layout.addWidget(
            self.inventory_panel,
            stretch=8
        )


        self.layout.addWidget(
            self.stats_panel
        )



    def add_item(self, item):

        return self.inventory_panel.add_item(
            item
        )



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