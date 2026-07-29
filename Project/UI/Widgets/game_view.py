from pyvistaqt import QtInteractor
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor


class GameView(QtInteractor):
    resized = pyqtSignal(int, int)
    def __init__(self, input_manager, parent = None):
        
        super().__init__(parent)

        self.input_manager = input_manager

        self.cursor_locked = True
        self.last_mouse_pos = None
        self.ignore_mouse = False
        self.hide_cursor()

    def hide_cursor(self):
        self.setCursor(
            Qt.BlankCursor
        )


    def show_cursor(self):
        self.setCursor(
            Qt.ArrowCursor
        )


    def toggle_cursor(self):

        if self.cursor_locked:

            self.unlock_cursor()

        else:
            self.lock_cursor()


    def lock_cursor(self):

        self.cursor_locked = True

        self.hide_cursor()

        self.center_cursor()


    def unlock_cursor(self):

        self.cursor_locked = False

        self.show_cursor()

        self.last_mouse_pos = self.rect().center()


    def center_cursor(self):

        center = self.rect().center()

        global_center = self.mapToGlobal(
            center
        )

        self.ignore_mouse = True

        QCursor.setPos(
            global_center
        )

        self.last_mouse_pos = center


    def mouseMoveEvent(self, event):

        if self.ignore_mouse:

            self.ignore_mouse = False

            event.accept()
            return


        if not self.cursor_locked:

            event.accept()
            return


        pos = event.pos()

        if self.last_mouse_pos is not None:

            dx = pos.x() - self.last_mouse_pos.x()
            dy = pos.y() - self.last_mouse_pos.y()

            self.input_manager.move_mouse(
                dx,
                dy
            )


        self.last_mouse_pos = pos


        self.center_cursor()


        # Do NOT call VTK interaction
        event.accept()


    def mousePressEvent(self, event):

        event.accept()


    def mouseReleaseEvent(self, event):

        event.accept()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.resized.emit(
            self.width(),
            self.height()
        )
        