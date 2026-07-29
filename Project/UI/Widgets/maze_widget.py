from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt

from .hud_widget_utils import normalized_to_screen, project_node, create_hex_grids

class MazeWidget(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        self.xy_point = None
        self.xz_point = None
        self.yz_point = None

        #NxNx2 matrices filled with x,y points
        self.xy_grid = None
        self.xz_grid = None 
        self.yz_grid = None
        
    def initialize_widget(self, maze_map):
        N = maze_map.N
        # 3 Nx2
        self.xy_grid, self.xz_grid, self.yz_grid = create_hex_grids(N)

    def update_widget(self,maze_map, node_id):
        N = maze_map.N

        self.xy_point, self.xz_point,self.yz_point = project_node(node_id, N)
        
        self.update()

    def draw_point(
        self,
        painter,
        point,
        radius
    ):

        if point is None:
            return

        x,y = normalized_to_screen(
            self,
            0.9,
            point[0],
            point[1]
        )

        painter.drawEllipse(
            int(x-radius),
            int(y-radius),
            int(radius*2),
            int(radius*2)
        )

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )


        # black background

        painter.fillRect(
            self.rect(),
            Qt.black
        )


        # -------------------------
        # Draw grid points
        # -------------------------

        painter.setPen(
            QPen(
                Qt.white,
                2
            )
        )


        grids = [
            self.xy_grid,
            self.xz_grid,
            self.yz_grid
        ]


        for grid in grids:

            if grid is None:
                continue


            for point in grid.reshape(-1,2):

                x,y = normalized_to_screen(
                    self,
                    0.9,
                    point[0],
                    point[1]
                )

                painter.drawPoint(
                    int(x),
                    int(y)
                )


        # -------------------------
        # Draw player points
        # -------------------------

        painter.setPen(
            QPen(
                Qt.red,
                2
            )
        )


        player_points = [
            self.xy_point,
            self.xz_point,
            self.yz_point
        ]


        for point in player_points:

            if point is None:
                continue


            self.draw_point(
                painter,
                point,
                5
            )


        # -------------------------
        # Border
        # -------------------------
        """
        painter.setPen(
            QPen(
                Qt.white,
                2
            )
        )

        painter.drawRect(
            self.rect().adjusted(
                1,
                1,
                -1,
                -1
            )
        )
        """

        painter.end()