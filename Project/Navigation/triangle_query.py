import numpy as np
from collections import deque

class TriangleQuery:

    def __init__(self, active_surface):

        self.surface = active_surface

        self.cache_root = None
        self.cache_depth = -1

        self.cache = []

        # flat numpy cache
        self.cached_keys = np.empty(0, dtype=np.int32)
        self.cached_vertices = np.empty((0,3,3), dtype=np.float64)
        self.cached_centers = np.empty((0,3), dtype=np.float64)
        self.cached_normals = np.empty((0,3), dtype=np.float64)
        self.cached_neighbors = np.empty((0,3), dtype=np.int32)


    def build_cache(self, root_triangle, depth):

        if (
            root_triangle == self.cache_root and
            depth == self.cache_depth
        ):
            return

        self.cache_root = root_triangle
        self.cache_depth = depth

        visited = set()
        queue = deque([(root_triangle, 0)])

        triangle_keys = []

        while queue:

            tri_key, level = queue.popleft()

            if tri_key in visited:
                continue

            visited.add(tri_key)

            mesh_id, tri_id = tri_key

            mesh = self.surface.active_meshes[mesh_id]

            triangle_keys.append(tri_key)

            if level < depth:

                neighbors = mesh.tri_connections[tri_id]

                for neighbor_key in neighbors:

                    if neighbor_key not in visited:
                        queue.append(
                            (neighbor_key, level + 1)
                        )

        self._flatten_cache(triangle_keys)


    def _flatten_cache(self, triangle_keys):

        n = len(triangle_keys)

        self.cached_keys = np.empty(
            n,
            dtype=object
        )

        self.cached_vertices = np.empty(
            (n,3,3),
            dtype=np.float32
        )

        self.cached_centers = np.empty(
            (n,3),
            dtype=np.float32
        )

        self.cached_normals = np.empty(
            (n,3),
            dtype=np.float32
        )


        for i, key in enumerate(triangle_keys):

            mesh_id, tri_id = key

            mesh = self.surface.active_meshes[mesh_id]

            self.cached_keys[i] = key


            vertex_ids = mesh.tri_vertex_indices[tri_id]

            self.cached_vertices[i] = (
                mesh.vertices[vertex_ids]
            )


            self.cached_centers[i] = (
                mesh.tri_centers[tri_id]
            )


            self.cached_normals[i] = (
                mesh.vertex_normals[vertex_ids].mean(axis=0)
            )


    def raycast(self, cull_pos, cam_pos, direction, max_distance):

        delta = self.cached_centers - cull_pos

        dist_sq = np.einsum(
            "ij,ij->i",
            delta,
            delta
        )

        mask = dist_sq < max_distance * max_distance

        if not np.any(mask):
            return (
                np.empty(0, dtype=np.int32),
                np.empty((0,3,3), dtype=np.float32),
                np.empty(0, dtype=np.float32)
            )


        triangles = self.cached_vertices[mask]

        ray_direction = np.broadcast_to(
            direction,
            triangles.shape[:2]
        )

        # -------------------------
        # vectorized Moller-Trumbore
        # -------------------------

        v0 = triangles[:,0]
        v1 = triangles[:,1]
        v2 = triangles[:,2]


        edge1 = v1 - v0
        edge2 = v2 - v0


        h = np.cross(
            ray_direction,
            edge2
        )

        a = np.einsum(
            "ij,ij->i",
            edge1,
            h
        )

        valid = np.abs(a) > 1e-8

        f = np.zeros_like(a)
        f[valid] = 1.0 / a[valid]

        s = cam_pos - v0

        u = f * np.einsum(
            "ij,ij->i",
            s,
            h
        )

        valid &= (u >= 0) & (u <= 1)

        q = np.cross(
            s,
            edge1
        )

        v = f * np.einsum(
            "ij,ij->i",
            ray_direction,
            q
        )

        valid &= (v >= 0)
        valid &= (u + v <= 1)

        t = f * np.einsum(
            "ij,ij->i",
            edge2,
            q
        )

        valid &= t > 0
        valid &= t < max_distance


        # original cache indices
        triangle_ids = np.where(mask)[0][valid]

        # corresponding vertices
        vertices = triangles[valid]

        # corresponding distances
        distances = t[valid]
        normals = self.cached_normals[mask]


        return triangle_ids, vertices, distances, normals



    def get_mesh(self,triangle):

        return self.surface.active_meshes[triangle[0]]


    def get_tri_verts(self, triangle):

        mesh = self.get_mesh(triangle)

        vertex_ids = mesh.tri_vertex_indices[triangle[1]]

        return mesh.vertices[vertex_ids]


    def get_tri_norm(self, triangle):

        mesh = self.get_mesh(triangle)

        tri_normal = mesh.tri_normals[triangle[1]]

        return tri_normal


    def get_tri_center(self, triangle):

        mesh = self.get_mesh(triangle)

        tri_center = mesh.tri_centers[triangle[1]]

        return tri_center
    

    def get_tri_vert_norms(self, triangle):

        mesh = self.get_mesh(triangle)

        tri_vert_norms = mesh.vertex_normals[mesh.tri_vertex_indices[triangle[1]]]

        return tri_vert_norms


    def get_tri_connections(self, triangle):

        mesh = self.get_mesh(triangle)

        tri_neighbor_ids = tuple(mesh.tri_connections[triangle[1]])

        return tuple(tri_neighbor_ids)
    
    
    def world_to_barycentric(
            self,
            point,
            triangle_key
        ):
    
            v0, v1, v2 = self.get_tri_verts(triangle_key)
    
            v0v1 = v1 - v0
            v0v2 = v2 - v0
            v0p = point - v0
    
            d00 = np.dot(v0v1, v0v1)
            d01 = np.dot(v0v1, v0v2)
            d11 = np.dot(v0v2, v0v2)
            d20 = np.dot(v0p, v0v1)
            d21 = np.dot(v0p, v0v2)
    
            denom = d00*d11 - d01*d01
    
            assert denom > 1e-8, (
                f"Degenerate triangle in world_to_barycentric: {triangle_key}"
            )
    
            v = (d11*d20 - d01*d21) / denom
            w = (d00*d21 - d01*d20) / denom
            u = 1 - v - w
    
            return np.array([u, v, w])


    def barycentric_to_world(self, bary, triangle):
    
            mesh = self.get_mesh(triangle)
    
            tri_vertices = mesh.tri_vertex_indices[triangle[1]]
    
            return (
                bary[0] * mesh.vertices[tri_vertices[0]]
                +
                bary[1] * mesh.vertices[tri_vertices[1]]
                +
                bary[2] * mesh.vertices[tri_vertices[2]]
            )


