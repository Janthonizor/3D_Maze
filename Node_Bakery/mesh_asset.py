import numpy as np





class Triangle:

    def __init__(
        self,
        id,
        vertex_indices
    ):

        # local triangle id
        self.id = id

        self.vertex_indices = np.array(
            vertex_indices,
            dtype=int
        )


class MeshAsset:

    def __init__(
        self,
        filename
    ):

        self.filename = filename

        # --------------------
        # Local mesh data
        # --------------------

        self.vertices = []
        self.triangles = []


        # --------------------
        # Topology data
        # --------------------

        self.edge_triangles = {}

        self.boundary_edges = []
        self.boundary_vertices = []
        self.boundary_neighbors = {}


        self.boundary_loops = []


        self.load_obj()

        self.remove_unused_vertices()

        self.validate_vertices()

        self.build_boundary()

    def load_obj(self):

        triangle_id = 0


        with open(self.filename, "r") as f:

            for line in f:

                line = line.strip()


                # --------------------
                # Vertex
                # --------------------

                if line.startswith("v "):

                    data = line[2:].split()

                    self.vertices.append(
                        np.array(
                            [
                                np.float64(data[0]),
                                np.float64(data[1]),
                                np.float64(data[2])
                            ]
                        )
                    )



                # --------------------
                # Face
                # --------------------

                elif line.startswith("f "):

                    data = line[2:].split()

                    vertex_indices = []


                    for section in data:

                        vertex_indices.append(
                            np.int32(section.split("/")[0]) - 1
                        )



                    # triangle

                    if len(vertex_indices) == 3:

                        self.triangles.append(
                            Triangle(
                                triangle_id,
                                vertex_indices
                            )
                        )

                        triangle_id += 1



                    # quad -> triangles

                    elif len(vertex_indices) == 4:

                        self.triangles.append(
                            Triangle(
                                triangle_id,
                                [
                                    np.int32(vertex_indices[0]),
                                    np.int32(vertex_indices[1]),
                                    np.int32(vertex_indices[2])
                                ]
                            )
                        )

                        triangle_id += 1


                        self.triangles.append(
                            Triangle(
                                triangle_id,
                                [
                                    vertex_indices[0],
                                    vertex_indices[2],
                                    vertex_indices[3]
                                ]
                            )
                        )

                        triangle_id += 1



        self.vertices = np.array(
            self.vertices,
            dtype=float
        )

    def remove_unused_vertices(self):

        used_vertices = set()

        # collect all referenced vertices
        for tri in self.triangles:
            for vertex_id in tri.vertex_indices:
                used_vertices.add(vertex_id)


        used_vertices = sorted(used_vertices)


        # old index -> new index
        vertex_map = {
            old_id: new_id
            for new_id, old_id in enumerate(used_vertices)
        }


        # rebuild vertex array
        self.vertices = self.vertices[
            used_vertices
        ]


        # remap triangles
        for tri in self.triangles:

            tri.vertex_indices = np.array(
                [
                    vertex_map[i]
                    for i in tri.vertex_indices
                ],
                dtype=int
            )

    def validate_vertices(self):

        used = set()

        for tri in self.triangles:
            used.update(tri.vertex_indices)

        assert len(used) == len(self.vertices), (
            f"Unused vertices remain: "
            f"{len(self.vertices)-len(used)}"
        )

    def build_boundary(self):

        edge_map = {}



        # --------------------
        # Edge -> triangle map
        # --------------------

        for tri in self.triangles:


            verts = tri.vertex_indices


            edges = [
                (verts[0], verts[1]),
                (verts[1], verts[2]),
                (verts[2], verts[0])
            ]


            for edge in edges:


                edge = tuple(
                    sorted(edge)
                )


                if edge not in edge_map:

                    edge_map[edge] = []


                edge_map[edge].append(
                    tri.id
                )



        self.edge_triangles = edge_map



        # --------------------
        # Find boundary edges
        # --------------------

        for edge, triangles in edge_map.items():


            if len(triangles) == 1:


                self.boundary_edges.append(
                    edge
                )


                a, b = edge


                if a not in self.boundary_neighbors:

                    self.boundary_neighbors[a] = []


                if b not in self.boundary_neighbors:

                    self.boundary_neighbors[b] = []



                self.boundary_neighbors[a].append(b)

                self.boundary_neighbors[b].append(a)



        self.boundary_vertices = list(
            self.boundary_neighbors.keys()
        )


        self.build_boundary_loops()

    def build_boundary_loops(self):

        visited = set()


        for start in self.boundary_vertices:

            if start in visited:
                continue


            loop = []

            current = start
            previous = None


            while True:

                loop.append(current)

                visited.add(current)


                neighbors = self.boundary_neighbors[current]


                if len(neighbors) != 2:
                    raise Exception(
                        f"Non-manifold boundary at vertex {current}: {neighbors}"
                    )


                if previous is None:

                    next_vertex = neighbors[0]

                else:

                    next_vertex = (
                        neighbors[0]
                        if neighbors[1] == previous
                        else neighbors[1]
                    )


                previous = current
                current = next_vertex


                if current == start:
                    break


            self.boundary_loops.append(
                {
                    "vertices": loop
                }
            )