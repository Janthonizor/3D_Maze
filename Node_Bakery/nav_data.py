import numpy as np
class NavData:
    def __init__(
            self, 
            node_key,
            vertices, 
            vertex_normals,
            tri_vertex_indices,
            tri_normals,
            tri_centers,
            tri_connections,
            boundary_triangles
    ):
        #node_key ranges from 0-63
        self.node_key = np.uint8(node_key)
        self.vertices = np.asarray(vertices, dtype = np.float32)
        self.vertex_normals = np.asarray(vertex_normals, dtype = np.float32)
        self.tri_centers = np.asarray(tri_centers, dtype = np.float32)
        self.tri_normals = np.asarray(tri_normals, dtype = np.float32)
        self.tri_vertex_indices = np.asarray(tri_vertex_indices, dtype = np.uint16)
        self.tri_connections = np.asarray(
            tri_connections,
            dtype=np.int32
        )
        self.boundary_triangles = [
            np.asarray(loop, dtype=np.uint16)
            for loop in boundary_triangles
        ]