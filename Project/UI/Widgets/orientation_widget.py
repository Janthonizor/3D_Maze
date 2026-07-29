import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtCore import Qt

from .hud_widget_utils import isometric_projection, normalized_to_screen


class OrientationWidget(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        # projected player axes
        self.px = None
        self.py = None
        self.pz = None

        # depth values
        self.dx = None
        self.dy = None
        self.dz = None
        self.pad = 0.75

    def update_widget(
        self,
        player_frame
    ):

        _, up, forward = player_frame


        # calculate right-handed frame

        right = np.cross(
            up,
            forward
        )

        right /= np.linalg.norm(
            right
        )


        # Treat axes as points

        points = np.array(
            [
                forward,
                up,
                right
            ]
        )


        projected, depths = isometric_projection(
            points
        )


        # preserve axis identity

        self.px = projected[0]
        self.py = projected[1]
        self.pz = projected[2]


        self.dx = depths[0]
        self.dy = depths[1]
        self.dz = depths[2]


        self.update()






    def draw_axis(
        self,
        painter,
        point,
        depth,
        color
    ):

        x, y = normalized_to_screen(
            self,
            self.pad,
            point[0],
            point[1]
        )


        cx, cy = normalized_to_screen(
            self,
            self.pad,
            0,
            0
        )


        size = int(10 - depth * 6)


        # white axis line

        painter.setPen(
            QPen(
                Qt.white,
                2
            )
        )

        painter.drawLine(
            cx,
            cy,
            x,
            y
        )


        # colored endpoint

        painter.setBrush(
            QBrush(
                Qt.NoBrush
            )
        )

        painter.setPen(
            QPen(
                color,
                3
            )
        )

        painter.drawEllipse(
            int(x - size/2),
            int(y - size/2),
            size,
            size
        )

   


    def paintEvent(
        self,
        event
    ):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )


        # background

        painter.fillRect(
            self.rect(),
            Qt.black
        )

        """
        # border

        painter.setPen(
            QPen(
                Qt.white,
                2
            )
        )

        painter.drawRect(
            1,
            1,
            self.width()-2,
            self.height()-2
        )
        """

        # -------------------------
        # Draw static maze frame
        # -------------------------

        cx, cy = normalized_to_screen(
            self,
            self.pad,
            0,
            0
        )


        maze_axes = [
            (
                np.array([np.sqrt(3)/2, -0.5]),
                "Y"
            ),
            (
                np.array([-np.sqrt(3)/2, -0.5]),
                "X"
            ),
            (
                np.array([0, 1]),
                "Z"
            )
        ]


        painter.setPen(
            QPen(
                Qt.gray,
                1
            )
        )


        for point, label in maze_axes:


            # shorten line

            line_point = (
                point *
                0.9
            )


            x, y = normalized_to_screen(
                self,
                self.pad,
                line_point[0],
                line_point[1]
            )


            # draw shortened axis line

            painter.drawLine(
                cx,
                cy,
                x,
                y
            )


            # label at true endpoint

            lx, ly = normalized_to_screen(
                self,
                self.pad,
                point[0],
                point[1]
            )


            painter.drawText(
                int(lx),
                int(ly),
                label
            )


        if self.px is not None:


            # sort only for drawing

            axes = [
                (self.px, self.dx, Qt.red),
                (self.py, self.dy, Qt.white),
                (self.pz, self.dz, Qt.white)
            ]


            axes.sort(
                key=lambda item: item[1]
            )


            for point, depth, color in axes:

                self.draw_axis(
                    painter,
                    point,
                    depth,
                    color
                )


        painter.end()