import numpy as np


class MeshInstance:


    def __init__(
        self,
        asset,
        position=np.zeros(3, dtype=np.float32),
        rotation=None,
        asset_type=None
    ):

        self.asset = asset
        self.asset_type = asset_type
        
        self.position = np.asarray(
            position,
            dtype=np.float32
        )

        self.rotation = (
            np.eye(3, dtype = np.float32)
            if rotation is None
            else rotation
        )

        self.vertices = None
        self.triangles = asset.triangles

        self.boundary_loops = []

        self.transform()



    def transform(self):

        # transform mesh

        self.vertices = np.array(
            [
                self.rotation @ v + self.position
                for v in self.asset.vertices
            ],
            dtype=np.float32
        )


        # transform boundary loops

        for loop in self.asset.boundary_loops:

            ids = loop["vertices"]

            points = np.array(
                [
                    self.vertices[i]
                    for i in ids
                ],
                dtype=np.float32
            )


            normal = self.compute_loop_normal(
                points
            )


            self.boundary_loops.append(
                {
                    "ids": ids,
                    "vertices": points,
                    "normal": normal,
                    "center": np.mean(
                        points,
                        axis=0, 
                        dtype=np.float32
                    )
                }
            )



    def compute_loop_normal(
        self,
        points
    ):

        normal = np.zeros(3, dtype=np.float32)


        for i in range(
            len(points)
        ):

            a = points[i]
            b = points[
                (i+1) % len(points)
            ]

            normal += np.cross(
                a,
                b
            )


        length = np.linalg.norm(
            normal
        )


        if length < 1e-8:
            return np.zeros(3)
        else:
            normal = normal/length

        if len(self.asset.boundary_loops)>2:
            axis = np.argmax(abs(normal))

            if axis == 2:
                mult = points[0][2]*normal
                normal = mult*normal
                normal /= np.linalg.norm(normal)
            elif axis == 1: 
                mult = points[0][1] * normal
                normal = mult*normal
                normal /= np.linalg.norm(normal)
            elif axis == 0:
                mult = points[0][0] * normal
                normal = mult*normal
                normal /= np.linalg.norm(normal)

        return normal



