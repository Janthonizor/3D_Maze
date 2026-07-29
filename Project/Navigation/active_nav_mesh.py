import numpy as np

class ActiveNavMesh:

    def __init__(
        self,
        nav_data,
        mesh_id,
        translation
    ):
        self.debug = False

        self.mesh_id = mesh_id
        self.node_key = nav_data.node_key

        self.translation = np.asarray(
            translation,
            dtype=np.float32
        )

        self.vertices = (
            nav_data.vertices.copy()
            +
            self.translation
        )

        self.tri_centers = (
            nav_data.tri_centers.copy()
            +
            self.translation
        )

        self.vertex_normals = (
            nav_data.vertex_normals.copy()
        )

        self.tri_normals = (
            nav_data.tri_normals.copy()
        )

        self.tri_vertex_indices = (
            nav_data.tri_vertex_indices.copy()
        )

        self.tri_connections = (
            nav_data.tri_connections.copy()
        )
        
        mask = self.tri_connections[:,:,1] >= 0

        self.tri_connections[:,:,0][mask] = mesh_id

        self.tri_connections = [
            [
                tuple(connection)
                for connection in tri_connections
            ]
            for tri_connections in self.tri_connections
        ]

        self.boundary_triangles = [
            [
                tri_id
                for tri_id in loop
            ]
            for loop in nav_data.boundary_triangles
        ]
