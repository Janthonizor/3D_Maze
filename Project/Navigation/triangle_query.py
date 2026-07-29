import numpy as np

class TriangleQuery:

    def __init__(self, active_surface):
        self.surface = active_surface
        self.cache_root = None
        self.cache_depth = None
        self.visited = None
        self.cache = None

    

    def get_cache(self, root_triangle, max_depth):
        assert isinstance(max_depth, int), (
            f"max_depth must be int, got {type(max_depth)}: {max_depth}"
        )
        if root_triangle != self.cache_root:

            self.build_new_cache(root_triangle, max_depth)

        elif max_depth > self.cache_depth:

            self.expand_cache(max_depth)

        return self.cache[:max_depth + 1]
        

    def build_new_cache(self, root_triangle, max_depth):

        self.cache_root = root_triangle

        self.cache_depth = 0

        self.visited = {root_triangle}

        self.cache = [[root_triangle]]

        self.expand_cache(max_depth)


    def expand_cache(self, target_depth):

        while self.cache_depth < target_depth:

            next_layer = []

            for triangle in self.cache[-1]:

                connected_triangles = self.get_tri_connections(triangle)

                for connected_triangle in connected_triangles:

                    if connected_triangle[1] < 0:
                        continue

                    if connected_triangle not in self.visited:

                        self.visited.add(connected_triangle)

                        next_layer.append(connected_triangle)

            if not next_layer:
                break

            self.cache.append(next_layer)

            self.cache_depth += 1


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


