import numpy as np
import pyvista as pv

class RenderMesh:

    def __init__(
        self,
        mesh_asset,
        texture
    ):

        self.mesh_asset = mesh_asset

        # Rendering data
        self.texture = texture

        self.vertices = []
        self.uvs = []
        self.faces = []
        self.polydata = None
        self.build()
        self.build_polydata()



    def build(self):

        vertex_map = {}


        for face in self.mesh_asset.faces:

            render_face = [3]


            for i in range(3):

                vertex_index = face.vertex_indices[i]

                if face.uv_indices is not None:
                    uv_index = face.uv_indices[i]
                else:
                    uv_index = None

                if face.normal_indices is not None:
                    normal_index = face.normal_indices[i]
                else:
                    normal_index = None


                key = (
                    vertex_index,
                    uv_index,
                    normal_index
                )


                if key not in vertex_map:

                    vertex_map[key] = len(
                        self.vertices
                    )


                    # copy vertex position

                    self.vertices.append(
                        self.mesh_asset.vertices[
                            vertex_index
                        ]
                    )


                    # copy UV

                    if uv_index is not None:

                        self.uvs.append(
                            self.mesh_asset.uvs[
                                uv_index
                            ]
                        )


                render_face.append(
                    vertex_map[key]
                )


            self.faces.append(
                render_face
            )


        self.vertices = np.array(
            self.vertices,
            dtype=float
        )


        self.faces = np.array(
            self.faces,
            dtype=int
        )


        self.uvs = np.array(
            self.uvs,
            dtype=float
        )
        """
        print("\n--- RENDER MESH DEBUG ---")
        print("asset:", self.mesh_asset.filename)
        print("vertices:", self.vertices.shape)
        print("uvs:", self.uvs.shape)
        print("faces:", self.faces.shape)
        print("-------------------------\n")
        """

    def build_polydata(self):

        self.polydata = pv.PolyData(
            self.vertices,
            self.faces
        )


        if len(self.uvs) > 0:

            self.polydata.active_texture_coordinates = (
                self.uvs
            )