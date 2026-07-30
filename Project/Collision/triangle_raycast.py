import numpy as np

def ray_triangle_intersection(
    origin,
    direction,
    vertices
):

    epsilon = 1e-8

    edge1 = vertices[1] - vertices[0]
    edge2 = vertices[2] - vertices[0]

    h = np.cross(
        direction,
        edge2
    )

    a = np.dot(
        edge1,
        h
    )

    if abs(a) < epsilon:
        return None

    f = 1.0 / a

    s = origin - vertices[0]

    u = f * np.dot(
        s,
        h
    )

    if u < 0 or u > 1:
        return None

    q = np.cross(
        s,
        edge1
    )

    v = f * np.dot(
        direction,
        q
    )

    if v < 0 or u + v > 1:
        return None

    # distance along ray
    distance = f * np.dot(
        edge2,
        q
    )

    if distance > epsilon:
        return distance

    return None


def raycast_surface(
    triangle_query,
    root_triangle,
    origin,
    direction,
    max_cache_depth,
    max_ray_distance,
    cull_distance,
    cull_position = None
):
    if cull_position is None:

        cull_position = origin

    cull_distance_squared = cull_distance**2

    direction = direction/np.linalg.norm(direction)

    triangle_cache = triangle_query.get_cache(root_triangle, max_cache_depth)

    for _ , layer in enumerate(triangle_cache):

        for triangle in layer:

            tri_center = triangle_query.get_tri_center(triangle)

            offset = tri_center-cull_position

            dist_from_cull_target = np.dot(offset,offset)

            if dist_from_cull_target > cull_distance_squared:
                continue

            vertices = triangle_query.get_tri_verts(triangle)

            distance = ray_triangle_intersection(
                origin,
                direction,
                vertices
            )

            if distance == None:
                continue

            if distance > max_ray_distance:
                return None

            tri_normal = triangle_query.get_tri_norm(triangle)

            epsilon = 0.005

            lifted_vertices = vertices + tri_normal * epsilon


            return triangle, lifted_vertices, distance

    return None








