from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget
)

from PyQt5.QtCore import pyqtSignal

from UI.Screens.asset_loading_screen import AssetLoadingScreen
from UI.Screens.main_menu_screen import MainMenuScreen
from UI.Screens.level_loading_screen import LevelLoadingScreen
from UI.Screens.game_screen import GameScreen
from UI.Screens.end_screen import EndScreen


class GameWindow(QWidget):

    start_game_signal = pyqtSignal(dict)

    def __init__(self, application, input_manager):

        super().__init__()

        self.input_manager = input_manager
        self.application = application

        self.setWindowTitle(
            "Maze Explorer"
        )
        
        self.resize(
            1200,
            800
        )


        self.create_screen_stack()

        self.create_screens()

        self.show_screen(
            "asset_loading"
        )

    def create_screen_stack(self):

        self.stack = QStackedWidget()

        layout = QVBoxLayout()

        layout.addWidget(
            self.stack
        )
        self.setStyleSheet(
            """
            QStackedWidget {
                background-color: black;
            }
            """
        )
        self.setLayout(
            layout
        )


    def create_screens(self):

        self.asset_loading_screen = AssetLoadingScreen()

        self.main_menu_screen = MainMenuScreen()

        self.level_loading_screen = LevelLoadingScreen()

        self.game_screen = GameScreen(self.input_manager)

        self.end_screen = EndScreen()


        self.stack.addWidget(
            self.asset_loading_screen
        )

        self.stack.addWidget(
            self.main_menu_screen
        )

        self.stack.addWidget(
            self.level_loading_screen
        )

        self.stack.addWidget(
            self.game_screen
        )

        self.stack.addWidget(
            self.end_screen
        )


        self.main_menu_screen.start_game_signal.connect(
            self.start_game_signal
        )



    def show_screen(self, name):

        screens = {

            "asset_loading":
                self.asset_loading_screen,

            "main_menu":
                self.main_menu_screen,

            "level_loading":
                self.level_loading_screen,

            "game":
                self.game_screen,

            "end":
                self.end_screen
        }


        self.stack.setCurrentWidget(
            screens[name]
        )


    def closeEvent(self, event):

        print("Window closing")

        if self.application:

            self.application.shutdown()

        event.accept()

   