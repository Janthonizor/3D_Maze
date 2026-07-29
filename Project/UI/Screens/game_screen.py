from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSizePolicy
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication
from UI.Widgets.hud import HUD
from UI.Widgets.game_view import GameView
from UI.Widgets.menu_overlay import MenuOverlay
from UI.game_mode import GameMode


class GameScreen(QWidget):

    def __init__(self, input_manager):

        super().__init__()

        self.input_manager = input_manager

        self.game_mode = GameMode.PLAYING
        self.previous_game_mode = GameMode.PLAYING

        self.game_stack = None
        self.game_container = None

        self.hud = None
        self.game_plotter = None
        self.menu_overlay = None
        self.focusChanged = None

        self.setFocusPolicy(
            Qt.StrongFocus
        )

        self.create_widgets()
        self.create_layout()

        QApplication.instance().focusChanged.connect(
            self.debug_focus_change
        )
        QTimer.singleShot(
            0,
            self.initialize_game_view
        )


    def initialize_game_view(self):

        self.game_plotter.show()

        self.game_plotter.ren_win.Render()

        self.hud.show()



    def create_widgets(self):

        # -------------------------
        # Stack container
        # -------------------------

        self.game_stack = QWidget(
            self
        )

        self.game_stack.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        # -------------------------
        # Game container
        # -------------------------

        self.game_container = QWidget(
            self.game_stack
        )

        self.game_container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        self.hud = HUD(
            self.game_container
        )


        self.game_plotter = GameView(
            self.input_manager,
            self.game_container
        )


        self.game_plotter.installEventFilter(
            self
        )

        self.game_plotter.setFocusPolicy(
            Qt.StrongFocus
        )


        self.game_plotter.keyPressEvent = (
            self.keyPressEvent
        )

        self.game_plotter.keyReleaseEvent = (
            self.keyReleaseEvent
        )


        gameplay_layout = QHBoxLayout()

        gameplay_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        gameplay_layout.setSpacing(
            0
        )


        gameplay_layout.addWidget(
            self.hud
        )

        gameplay_layout.addWidget(
            self.game_plotter
        )


        gameplay_layout.setStretch(
            0,
            1
        )

        gameplay_layout.setStretch(
            1,
            4
        )


        self.game_container.setLayout(
            gameplay_layout
        )


        # -------------------------
        # Overlay
        # -------------------------

        self.menu_overlay = MenuOverlay(
            self.game_stack
        )

        self.menu_overlay.hide()


        self.configure_plotter()



    def create_layout(self):

        layout = QHBoxLayout()

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )


        layout.addWidget(
            self.game_stack
        )


        self.setLayout(
            layout
        )



    def resizeEvent(self, event):

        if self.game_stack:

            self.game_container.setGeometry(
                self.game_stack.rect()
            )

            self.menu_overlay.setGeometry(
                self.game_stack.rect()
            )

            self.menu_overlay.raise_()


        super().resizeEvent(event)



    def configure_plotter(self):

        self.game_plotter.interactor.SetInteractorStyle(
            None
        )

        self.game_plotter.ren_win.SetMultiSamples(
            0
        )

        self.game_plotter.set_background(
            "black"
        )

        self.game_plotter.renderer.SetUseDepthPeeling(
            False
        )



    def set_game_mode(self, mode):

        self.game_mode = mode


        if mode == GameMode.MENU:

            self.game_plotter.unlock_cursor()

            self.input_manager.keys.clear()

            self.menu_overlay.setGeometry(
                self.game_stack.rect()
            )

            self.menu_overlay.show()

            self.menu_overlay.raise_()


        else:

            self.menu_overlay.hide()


            if mode == GameMode.PLAYING:

                self.game_plotter.lock_cursor()


            else:

                self.game_plotter.unlock_cursor()

                self.input_manager.keys.clear()



    def toggle_inventory(self):

        if self.game_mode == GameMode.INVENTORY:

            self.set_game_mode(
                GameMode.PLAYING
            )
            
            self.hud.inventory_panel.set_inventory_mode(
                False
            )





        elif self.game_mode == GameMode.PLAYING:

            self.set_game_mode(
                GameMode.INVENTORY
            )
            self.hud.inventory_panel.set_inventory_mode(
                True
            )





    def toggle_menu(self):

        if self.game_mode == GameMode.MENU:

            self.set_game_mode(
                self.previous_game_mode
            )


        else:

            self.previous_game_mode = self.game_mode

            self.set_game_mode(
                GameMode.MENU
            )


    def restore_game_focus(self):

        self.game_plotter.setFocus(
            Qt.OtherFocusReason
        )


    def keyPressEvent(self, event):

        key = event.key()



        if key == Qt.Key_Escape:

            self.toggle_menu()

            event.accept()

            return


        if key == Qt.Key_Tab:

            self.toggle_inventory()

            event.accept()

            return


        movement_keys = (
            Qt.Key_W,
            Qt.Key_A,
            Qt.Key_S,
            Qt.Key_D,
        )


        if (
            key in movement_keys
            and self.game_mode != GameMode.PLAYING
        ):

            event.accept()

            return


        self.input_manager.press(
            key
        )



    def keyReleaseEvent(self, event):

        self.input_manager.release(
            event.key()
        )



    def showEvent(self, event):

        self.game_plotter.setFocus()

        super().showEvent(event)



    def eventFilter(self, obj, event):

        if obj == self.game_plotter:

            if event.type() == event.KeyPress:

                self.keyPressEvent(event)

                return True


            if event.type() == event.KeyRelease:

                self.keyReleaseEvent(event)

                return True


        return super().eventFilter(obj, event)

    def debug_focus_change(self, old, new):

        pass
    
    def focusInEvent(self, event):

        self.game_plotter.setFocus(
            Qt.OtherFocusReason
        )

        super().focusInEvent(event)