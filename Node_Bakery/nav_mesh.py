import numpy as np
from nav_triangle import NavTriangle
from nav_data import NavData

class NavMesh:

    def __init__(
        self,
        node_key,
        vertices,
        triangle_indices
    ):

        self.node_key = np.int16(node_key)

        self.vertices = np.asarray(vertices, dtype=np.float32)

        self.triangles = [
            NavTriangle(
                i,
                indices
            )
            for i, indices in enumerate(triangle_indices)
        ]
        num_triangles = len(self.triangles)

        self.tri_normals = np.zeros(
            (num_triangles, 3),
            dtype=np.float32
        )

        self.tri_centers = np.zeros(
            (num_triangles, 3),
            dtype=np.float32
        )
        self.boundary_triangle_indices = np.zeros(num_triangles, dtype = np.uint16)

        self.tri_connections = [
            [
                [None, None],
                [None, None],
                [None, None]
            ]
            for _ in range(num_triangles)
        ]

        self.edge_triangles = {}

        self.boundary_triangles = [[],[],[],[],[],[]]

        self.vertex_edges = {}
        
        self.boundary_edges = []

        self.vertex_normals = np.zeros_like(self.vertices, dtype=np.float32)

        self.validate_vertices()

        self.build_adjacency()

        self.compute_normals()

        self.compute_vertex_normals()

        self.adjust_boundary_vertex_normals()

        self.get_boundary_triangles()

        self.build_tri_connections()

    def validate_vertices(self):

        referenced_vertices = set()

        for tri in self.triangles:
            referenced_vertices.update(
                tri.vertex_indices
            )

        all_vertices = set(
            range(len(self.vertices))
        )

        unused_vertices = (
            all_vertices -
            referenced_vertices
        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        assert len(unused_vertices) == 0, (
            f"Unused vertices remain: {len(unused_vertices)}"
        )

        max_index = max(
            referenced_vertices
        )

        assert max_index < len(self.vertices), (
            f"Triangle references vertex {max_index}, "
            f"but only {len(self.vertices)} vertices exist"
        )

        min_index = min(
            referenced_vertices
        )

        assert min_index >= 0, (
            f"Negative vertex index found: {min_index}"
        )

    def build_adjacency(self):

        for tri in self.triangles:

            ids = tri.vertex_indices

            edges = [
                (ids[0], ids[1]),
                (ids[1], ids[2]),
                (ids[2], ids[0])
            ]

            for edge in edges:

                edge = tuple(sorted(edge))

                if edge not in self.edge_triangles:
                    self.edge_triangles[edge] = []

                self.edge_triangles[edge].append(tri)


                # store vertex -> connected edges
                for vertex_id in edge:

                    if vertex_id not in self.vertex_edges:
                        self.vertex_edges[vertex_id] = []

                    self.vertex_edges[vertex_id].append(edge)


        for edge, triangles in self.edge_triangles.items():

            if len(triangles) == 2:

                tri_a = triangles[0]   # NavTriangle object
                tri_b = triangles[1]   # NavTriangle object

                tri_a.neighbor_ids.append(
                    tri_b.id
                )

                tri_b.neighbor_ids.append(
                    tri_a.id
                )

            elif len(triangles) == 1:

                self.boundary_edges.append(
                    edge
                )

            elif len(triangles) > 2:

                print(
                    "WARNING: non-manifold edge",
                    edge,
                    [
                        tri.id
                        for tri in triangles
                    ]
                )

    #checked
    def compute_normals(self):

        for index, tri in enumerate(self.triangles):

            # get triangle vertices
            v0 = self.vertices[
                tri.vertex_indices[0]
            ].astype(np.float32)

            v1 = self.vertices[
                tri.vertex_indices[1]
            ].astype(np.float32)

            v2 = self.vertices[
                tri.vertex_indices[2]
            ].astype(np.float32)


            # edge vectors
            edge1 = v1 - v0
            edge2 = v2 - v0


            # cross product gives normal direction
            normal = np.cross(
                edge1,
                edge2
            )


            length = np.linalg.norm(
                normal
            )

            #assert length > 1e-12, (
                #f"Degenerate triangle: {index}"
            #)

            tri.normal = normal


            # useful for barycentric tests / debugging
            center = (
                v0 +
                v1 +
                v2
            )/3.0
            tri.center = center

            self.tri_normals[index] = normal
            self.tri_centers[index] = center

    # checked
    def compute_vertex_normals(self):

        self.vertex_normals = np.zeros_like(
            self.vertices
        )

        for tri in self.triangles:
            for vertex_id in tri.vertex_indices:

                self.vertex_normals[vertex_id] += tri.normal
        

        for i in range(len(self.vertex_normals)):

            length = np.linalg.norm(
                self.vertex_normals[i]
            )

            #assert length > 1e-12, (
                #f"Invalid vertex normal: {i}"
            #)
            if length > 0.001:
                self.vertex_normals[i] /= length

    def get_boundary_triangles(self):

        boundary = []

        for tri in self.triangles:

            if len(tri.neighbor_ids) == 2:
                boundary.append(tri)


        if len(boundary) == 0:
            return




        BOX_HALF = 3.0

        for tri in boundary:

            x, y, z = tri.center

            if x > BOX_HALF:
                self.boundary_triangles[0].append(tri.id)   # +x

            if x < -BOX_HALF:
                self.boundary_triangles[1].append(tri.id)   # -x

            if y > BOX_HALF:
                self.boundary_triangles[2].append(tri.id)   # +y

            if y < -BOX_HALF:
                self.boundary_triangles[3].append(tri.id)   # -y

            if z > BOX_HALF:
                self.boundary_triangles[4].append(tri.id)   # +z

            if z < -BOX_HALF:
                self.boundary_triangles[5].append(tri.id)   # -z


        for loop_id, triangles in enumerate(self.boundary_triangles):

            if len(triangles) == 0:
                continue


            # Need objects temporarily for sorting
            tri_objects = [
                self.triangles[tri_id]
                for tri_id in triangles
            ]


            sorted_objects = sort_boundary_loop(
                tri_objects,
                loop_id
            )


            # Convert back to ids
            self.boundary_triangles[loop_id] = [
                tri.id
                for tri in sorted_objects
            ]

    def get_boundary_vertices(self):

        boundary_vertices = set()

        for edge in self.boundary_edges:

            v0, v1 = edge

            boundary_vertices.add(v0)
            boundary_vertices.add(v1)

        return boundary_vertices
    
    def get_vertex_boundary_edges(self, vertex_id):

        edges = self.vertex_edges[vertex_id]

        boundary_edges = []

        for edge in edges:

            if edge in self.boundary_edges:
                boundary_edges.append(edge)

        return boundary_edges

    def adjust_boundary_vertex_normals(self):

        boundary_vertices = self.get_boundary_vertices()

        for vertex_id in boundary_vertices:

            boundary_edges = self.get_vertex_boundary_edges(
                vertex_id
            )

            if len(boundary_edges) != 2:
                continue

            vertex = self.vertices[vertex_id]

            normal = np.zeros(3, dtype=np.float32)

            for edge in boundary_edges:

                other = (
                    edge[1]
                    if edge[0] == vertex_id
                    else edge[0]
                )

                direction = (
                    self.vertices[other] - vertex
                )

                direction /= np.linalg.norm(direction)

                normal += direction


            normal /= np.linalg.norm(normal)

            self.vertex_normals[vertex_id] = normal

    def build_tri_connections(self):

        num_triangles = len(self.triangles)

        self.tri_connections = np.full(
            (num_triangles, 3, 2),
            -1,
            dtype=np.int32
        )

        for tri in self.triangles:

            for i, neighbor_id in enumerate(tri.neighbor_ids):

                if neighbor_id is not None:

                    self.tri_connections[
                        tri.id,
                        i
                    ] = [
                        -1,
                        neighbor_id
                    ]

    def export(self):
        
        tri_vertex_indices = [
            tri.vertex_indices
            for tri in self.triangles
        ]

        return NavData(
            self.node_key,
            self.vertices,
            self.vertex_normals,
            tri_vertex_indices,
            self.tri_normals,
            self.tri_centers,
            self.tri_connections,
            self.boundary_triangles

        )

def sort_boundary_loop(triangles, loop_id):#

    sorted_triangles = []

    values = []

    for tri in triangles:

        n = tri.normal

        if loop_id in (0, 1):
            # around X 
            angle = np.arctan2(
                n[2],
                n[1]
            )

        elif loop_id in (2, 3):
            # around Y
            angle = np.arctan2(
                n[0],
                n[2]
            )


        elif loop_id in (4, 5):
            # around Z
            angle = np.arctan2(
                n[1],
                n[0]
            )


        # normalize to 0-1
        if angle < 0:
            angle += 2*np.pi


        angle /= (2*np.pi)


        values.append(
            (angle, tri)
        )

    values.sort(
        key=lambda x: x[0]
    )

    sorted_triangles = [
        tri
        for angle, tri in values
    ]

    return sorted_triangles
