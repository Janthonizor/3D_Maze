import numpy as np

from mesh_asset import MeshAsset


CAP_ROTATIONS = {
    ( 1, 0, 0): (0,90,0),
    (-1, 0, 0): (0,-90,0),
    ( 0, 1, 0): (-90,0,0),
    ( 0,-1, 0): (90,0,0),
    ( 0, 0, 1): (0,0,0),
    ( 0, 0,-1): (0,180,0),
}


HALLWAY_ROTATIONS = {
    ( 1,0,0): (0,0,0),
    (-1,0,0): (0,0,180),
    ( 0,1,0): (0,0,90),
    ( 0,-1,0): (0,0,-90),
    ( 0,0,1): (0,-90,0),
    ( 0,0,-1): (0,90,0),
}


class AssetHolder:

    def __init__(
        self,
        asset_folder
    ):

        self.asset_folder = asset_folder

        self.node_asset = None
        self.hallway_asset = None
        self.cap_asset = None


        self.hallway_rotations = {}
        self.cap_rotations = {}


        self.load_assets()

        self.build_rotations()



    def load_assets(self):

        self.node_asset = MeshAsset(
            f"{self.asset_folder}/node.obj"
        )

        self.hallway_asset = MeshAsset(
            f"{self.asset_folder}/hallway.obj"
        )

        self.cap_asset = MeshAsset(
            f"{self.asset_folder}/cap.obj"
        )



    def build_rotations(self):

        for direction, angles in HALLWAY_ROTATIONS.items():

            self.hallway_rotations[direction] = (
                self.euler_to_matrix(angles)
            )


        for direction, angles in CAP_ROTATIONS.items():

            self.cap_rotations[direction] = (
                self.euler_to_matrix(angles)
            )



    def euler_to_matrix(self, angles):

        x, y, z = np.deg2rad(angles)


        Rx = np.array([
            [1,0,0],
            [0,np.cos(x),-np.sin(x)],
            [0,np.sin(x), np.cos(x)]
        ], dtype=np.float64)


        Ry = np.array([
            [ np.cos(y),0,np.sin(y)],
            [0,1,0],
            [-np.sin(y),0,np.cos(y)]
        ], dtype=np.float64)


        Rz = np.array([
            [np.cos(z),-np.sin(z),0],
            [np.sin(z), np.cos(z),0],
            [0,0,1]
        ],dtype=np.float64)


        return Rz @ Ry @ Rx