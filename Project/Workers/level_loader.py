from PyQt5.QtCore import QObject, pyqtSignal

from Maze_Generation.level import Level


class LevelLoader(QObject):

    finished = pyqtSignal(object)
    progress = pyqtSignal(str)


    def __init__(
        self,
        settings,
        assets
    ):

        super().__init__()

        self.running = True

        self.settings = settings
        self.assets = assets


    def run(self):

        try:

            self.progress.emit(
                "Loading Maze..."
            )


            level = Level(
                **self.settings
            )


            if not self.running:
                return


            self.progress.emit(
                "Generating node colors..."
            )

            print("COLOR SIGNAL SENT")


            level.build_node_color_maps(
                self.assets
            )


            if not self.running:
                return


            self.progress.emit(
                "Performing Wizardry.."
            )


            level.build_actors(
                self.assets
            )


            if not self.running:
                return


            level.assign_nav_meshes(
                self.assets
            )
            self.progress.emit(
                "Assigning data..."
            )

            if not self.running:
                return

            
            self.finished.emit(
                level
            )


            print(
                "Finished building actors:",
                sum(
                    node.mesh_actor is not None
                    for node in level.maze_map.nodes.values()
                ),
                "/",
                len(level.maze_map.nodes)
            )


        except Exception as e:

            print(
                "Level loading failed:",
                e
            )


    def stop(self):

        print("Level loader stopping")

        self.running = False