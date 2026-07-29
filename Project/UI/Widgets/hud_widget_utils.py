from Maze_Generation.maze_gen import id_to_grid

def normalized_to_screen(
    self,
    padd_fract,
    x,
    y
):

    size = min(
        self.width(),
        self.height()
    )


    # center of widget

    cx = self.width() / 2
    cy = self.height() / 2


    # padding percentage
    # 0.8 means use 80% of available space


    scale = (
        size / 2
    ) * padd_fract


    screen_x = (
        cx + x * scale
    )


    # flip y because Qt grows downward

    screen_y = (
        cy - y * scale
    )


    return int(screen_x), int(screen_y)

import numpy as np


def project_node(
    id,
    N
):
    i,j,k = id_to_grid(id, N)

    vi = np.array([
        np.sqrt(3)/2,
        1/2
    ])

    vj = np.array([
        -np.sqrt(3)/2,
        1/2
    ])

    vk = np.array([
        0,
        -1
    ])

    i += 1
    j += 1
    k += 1

    scale = 1 / N

    ij_point = (
        vi * ((N-i+1) * scale) +
        vj * ((N-j+1) * scale)
    )

    ik_point = (
        vi * ((N-i+1) * scale) +
        vk * ((N - k + 1) * scale)
    )

    jk_point = (
        vj * ((N-j+1) * scale) +
        vk * ((N - k + 1) * scale)
    )

    return (
        ij_point,
        ik_point,
        jk_point
    )


def create_hex_grids(N):

    # basis vectors

    vi = np.array([
        np.sqrt(3)/2,
        1/2
    ])

    vj = np.array([
        -np.sqrt(3)/2,
        1/2
    ])

    vk = np.array([
        0,
        -1
    ])


    # create coordinate grid

    i, j = np.meshgrid(
        np.arange(N),
        np.arange(N),
        indexing="ij"
    )


    # normalized coordinates

    i = (i + 1) / N
    j = (j + 1) / N


    # IJ rhombus

    ij_grid = (
        i[..., None] * vi +
        j[..., None] * vj
    )


    # IK rhombus

    ik_grid = (
        i[..., None] * vi +
        j[..., None] * vk
    )


    # JK rhombus

    jk_grid = (
        i[..., None] * vj +
        j[..., None] * vk
    )


    return (
        ij_grid,
        ik_grid,
        jk_grid
    )
def isometric_projection(points):

    points = np.asarray(
        points,
        dtype=float
    )


    camera_position = np.array(
        [1.0,1.0,1.0]
    )

    target = np.array(
        [0.0,0.0,0.0]
    )


    forward = target - camera_position
    forward /= np.linalg.norm(forward)


    world_up = np.array(
        [0.0,0.0,1.0]
    )


    right = np.cross(
        forward,
        world_up
    )

    right /= np.linalg.norm(right)


    up = np.cross(
        right,
        forward
    )

    up /= np.linalg.norm(up)


    # points are directions from origin

    depths = points @ forward


    projected_points = np.column_stack(
        (
            points @ right,
            points @ up
        )
    )


    return projected_points, depths