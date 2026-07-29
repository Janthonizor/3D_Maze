class NavData:
    def __init__(
        self,
        node_key,
        vertices,
        vertex_normals,
        tri_vertex_indices,
        tri_normals,
        tri_centers,
        boundary_triangles
    ):
        self.node_key = node_key
        self.vertices = vertices
        self.vertex_normals = vertex_normals
        self.tri_vertex_indices = tri_vertex_indices
        self.tri_normals = tri_normals
        self.tri_centers = tri_centers
        self.boundary_triangles = boundary_triangles