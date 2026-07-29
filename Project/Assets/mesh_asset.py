import numpy as np
from Rendering.face import Face


class MeshAsset:

    def __init__(
        self,
        filename
    ):

        self.filename = filename

        # local mesh data
        self.vertices = []
        self.uvs = []
        self.normals = []
        self.faces = []


        self.load_obj()

    def load_obj(self):

        with open(self.filename, "r") as f:


            for line in f:

                line = line.strip()


                # --------------------
                # Vertex
                # --------------------

                if line.startswith("v "):

                    data = line[2:].split()

                    self.vertices.append(
                        np.array([
                            float(data[0]),
                            float(data[1]),
                            float(data[2])
                        ])
                    )


                # --------------------
                # UV
                # --------------------

                elif line.startswith("vt "):

                    data = line[3:].split()

                    self.uvs.append(
                        np.array([
                            float(data[0]),
                            float(data[1])
                        ])
                    )


                # --------------------
                # Normal
                # --------------------

                elif line.startswith("vn "):

                    data = line[3:].split()

                    self.normals.append(
                        np.array([
                            float(data[0]),
                            float(data[1]),
                            float(data[2])
                        ])
                    )


                # --------------------
                # Face
                # --------------------

                elif line.startswith("f "):

                    data = line[2:].split()


                    vertex_indices = []
                    uv_indices = []
                    normal_indices = []


                    for section in data:

                        values = section.split("/")


                        # vertex index always exists

                        vertex_indices.append(
                            int(values[0]) - 1
                        )


                        # UV index

                        if len(values) > 1 and values[1]:

                            uv_indices.append(
                                int(values[1]) - 1
                            )


                        # normal index

                        if len(values) > 2 and values[2]:

                            normal_indices.append(
                                int(values[2]) - 1
                            )


                    self.faces.append(
                        Face(
                            vertex_indices,
                            uv_indices if uv_indices else None,
                            normal_indices if normal_indices else None
                        )
                    )


        self.vertices = np.array(
            self.vertices,
            dtype = float
        )

        self.uvs = np.array(
            self.uvs,
            dtype=float
        )

        self.normals = np.array(
            self.normals,
            dtype=float
        )
    