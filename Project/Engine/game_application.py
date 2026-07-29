from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt5.QtWidgets import QApplication

from UI.game_window import GameWindow

from Rendering.renderer import Renderer

from Engine.game_controller import GameController
from Engine.input_manager import InputManager

from Workers.asset_loader import AssetLoader
from Workers.level_loader import LevelLoader


class GameApplication(QObject):


    assets_loaded_signal = pyqtSignal(object)

    level_loaded_signal = pyqtSignal(object)

    start_game_signal = pyqtSignal(dict)

    game_finished_signal = pyqtSignal(object)

    game_ready_signal = pyqtSignal()


    def __init__(self):

        super().__init__()

        self.asset_library = None

        self.level = None

        self.renderer = None

        self.game_controller = None

        self.input_manager = InputManager()

        self.window = GameWindow(self, self.input_manager)

        self.assets_loaded_signal.connect(
            self.on_assets_loaded
        )

        self.level_loaded_signal.connect(
            self.on_level_loaded
        )

        self.game_finished_signal.connect(
            self.on_game_finished
        )

        self.window.start_game_signal.connect(
            self.load_level
        )

        self.window.end_screen.return_button.clicked.connect(
            self.end_continue_pressed
        )

        self.state = "startup"



    def start(self):

        self.show_asset_loading_screen()

        QTimer.singleShot(
            100,
            self.start_loading
        )


    def start_loading(self):

        self.thread = QThread()

        self.loader = AssetLoader()


        self.loader.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.loader.run
        )

        self.loader.progress.connect(
            self.update_asset_loading_text
        )

        self.loader.finished.connect(
            self.assets_loaded_signal.emit
        )

        self.loader.finished.connect(
            self.thread.quit
        )

        self.loader.finished.connect(
            self.loader.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater,
            
        )
        self.thread.finished.connect(
            self.clear_loader_thread
        )

        self.thread.start()

    def clear_loader_thread(self):
        self.thread = None
        self.level_loader = None


    def update_asset_loading_text(self, text):
    
        self.window.asset_loading_screen.update_text(
            text
        )

        QApplication.processEvents()
    

    def show_asset_loading_screen(self):

        self.state = "loading_assets"

        self.window.show_screen(
            "asset_loading"
        )


    def show_main_menu(self):

        self.state = "main_menu"

        self.window.show_screen(
            "main_menu"
        )


    def show_level_loading(self):

        self.state = "loading_level"

        self.window.show_screen(
            "level_loading"
        )
        QApplication.processEvents()


  
    def show_game(self):

        self.state = "playing"

        self.window.show_screen(
            "game"
        )


    def show_end_screen(self):

        self.state = "end_screen"

        self.window.show_screen(
            "end"
        )





    def on_assets_loaded(self, assets):

        self.asset_library = assets

        self.show_main_menu()



    def load_level(self, settings):

        self.show_level_loading()

        self.level_thread = QThread()

        self.level_loader = LevelLoader(
            settings,
            self.asset_library
        )

        self.level_loader.moveToThread(
            self.level_thread
        )

        self.level_thread.started.connect(
            self.level_loader.run
        )

        self.level_loader.progress.connect(
            self.update_level_loading_text
        )

        self.level_loader.finished.connect(
            self.on_level_loaded
        )

        self.level_loader.finished.connect(
            self.level_thread.quit
        )

        self.level_loader.finished.connect(
            self.level_loader.deleteLater
        )

        self.level_thread.finished.connect(
            self.level_thread.deleteLater
        )
        self.level_thread.finished.connect(
            self.clear_level_thread
        )
        

        self.level_thread.start()

    def clear_level_thread(self):

        self.level_thread = None
        self.level_loader = None

    def update_level_loading_text(self, text):
        self.window.level_loading_screen.set_text(
            text
        )

    def on_level_loaded(self, level):

        self.level = level

        self.initialize_game_session()


    def initialize_game_session(self):

        print("Initializing game session...")

        self.renderer = Renderer(
            self.window.game_screen.game_plotter,
            self.level.maze_map,
            self.asset_library
        )

        self.game_controller = GameController(
            self.level,
            self.renderer,
            self.window,
            self.input_manager
        )

        self.game_controller.ready.connect(
            self.game_ready_signal.emit
        )

        self.game_controller.initialize()

        self.start_game()


    def start_game(self):

        

        self.game_controller.start()

        self.show_game()

        self.input_manager.enable()


    def on_game_finished(self, results):

        self.cleanup_game()

        self.show_end_screen()


    def end_continue_pressed(self):

        self.show_main_menu()


    def cleanup_game(self):

        if self.game_controller:

            self.game_controller.stop()


        self.game_controller = None

        self.renderer = None

        self.level = None


    def shutdown(self):

        print("Application shutdown")


        # stop gameplay
        self.cleanup_game()


        # stop level thread
        if hasattr(self, "level_thread"):

            if self.level_thread:

                if self.level_thread.isRunning():

                    self.level_thread.quit()
                    self.level_thread.wait()


        # stop asset loader
        if hasattr(self, "loader"):
            if self.loader:
                print("Stopping asset loader")

                self.loader.stop()

        # stop level loader
        if hasattr(self, "level_loader"):
            if self.level_loader:
                print("Stopping level loader")

                self.level_loader.stop()

            
        # stop asset thread
        if hasattr(self, "thread"):

            if self.thread:

                if self.thread.isRunning():

                    self.thread.quit()
                    self.thread.wait()


        print("Shutdown complete")

    def closeEvent(self, event):
        self.application.shutdown()
        event.accept()

