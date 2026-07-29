import numpy as np
class ActiveNavMesh:

    def __init__(
        self,
        nav_data,
        mesh_id,
        translation
    ):

        self.mesh_id = mesh_id

        self.translation = np.asarray(
            translation,
            dtype=float
        )


        self.vertices = (
            nav_data.vertices.copy()
            +
            self.translation
        )

        self.node_key = nav_data.node_key


        # -------------------------------
        # Create runtime triangles
        # -------------------------------

        self.triangles = [
            ActiveTriangle(
                mesh_id,
                tri,
                self.translation
            )
            for tri in nav_data.triangles
        ]
        self.tri_connections = nav_data.tri_connections


        # -------------------------------
        # Restore local triangle graph
        # -------------------------------

        for active_tri, nav_tri in zip(
            self.triangles,
            nav_data.triangles
        ):

            active_tri.neighbors = [
                self.triangles[nbr_id]
                for nbr_id in nav_tri.neighbor_ids
            ]


        # -------------------------------
        # Restore boundary loops
        # -------------------------------

        self.boundary_triangles = {}

        for loop_id, triangle_ids in nav_data.boundary_triangles.items():

            self.boundary_triangles[loop_id] = [
                self.triangles[tri_id]
                for tri_id in triangle_ids
            ]

class ActiveTriangle:

    def __init__(
        self,
        mesh_id,
        nav_triangle,
        translation
    ):

        self.id = nav_triangle.id

        self.mesh_id = mesh_id

        self.global_id = (
            mesh_id,
            self.id
        )

        self.vertex_indices = nav_triangle.vertex_indices.copy()
        self.normal = nav_triangle.normal.copy()
        self.center = nav_triangle.center.copy() + translation

        # runtime references
        self.neighbors = []