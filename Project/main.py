import sys

from PyQt5.QtWidgets import QApplication

from Engine.game_application import GameApplication

def main():

    app = QApplication(sys.argv)

    game = GameApplication()


    game.window.show()

    game.start()

    sys.exit(
        app.exec()
    )

if __name__ == "__main__":
    main()


