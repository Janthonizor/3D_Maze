from PyQt5.QtCore import QObject, pyqtSignal

from Assets.asset_library import AssetLibrary

import time


class AssetLoader(QObject):

    finished = pyqtSignal(object)
    progress = pyqtSignal(str)


    def __init__(self):

        super().__init__()

        self.running = True


    def run(self):

        try:

            self.progress.emit(
                "Initializing assets..."
            )

            time.sleep(0.8)

            if not self.running:
                return


            assets = AssetLibrary()


            self.progress.emit(
                "Loading game assets..."
            )

            assets.load_all()


            if not self.running:
                return


            self.progress.emit(
                "Assets loaded"
            )

            time.sleep(0.7)

            if not self.running:
                return


            self.finished.emit(
                assets
            )


        except Exception as e:

            print(
                "Asset loading failed:",
                e
            )


    def stop(self):

        print("Asset loader stopping")

        self.running = False