import numpy as np
import random
from .maze_map import MazeMap
from .maze_node import MazeNode

def generate_maze(
    N,
    grid_spacing,
    branchiness,
    seed=None
):

    maze_map = MazeMap(
        N,
        grid_spacing
    )

    # create MazeNodes
    for k in range(N):
        for j in range(N):
            for i in range(N):

                node_id = grid_to_id(
                    i,
                    j,
                    k,
                    N
                )

                position = grid_spacing * np.array(
                    [i,j,k]
                )

                maze_node = MazeNode(
                    node_id,
                    position
                )

                maze_map.add_node(
                    maze_node
                )


    # generate maze connections
    nodes = maze_map.nodes

    visited = set()
    stack = []

    start = 0

    visited.add(start)
    stack.append(start)


    rng = random.Random(seed)


    while stack:

        if rng.randint(0,100) <= branchiness:
            selector = rng.randint(
                0,
                len(stack)-1
            )
        else:
            selector = -1


        current = stack[selector]


        neighbors = get_grid_neighbors(
            current,
            N
        )


        unvisited = [
            n for n in neighbors
            if n not in visited
        ]


        if unvisited:

            next_node = rng.choice(
                unvisited
            )


            nodes[current].add_neighbor(
                next_node
            )

            nodes[next_node].add_neighbor(
                current
            )


            visited.add(
                next_node
            )

            stack.append(
                next_node
            )

        else:

            stack.pop(selector)


    for node in maze_map.nodes.values():

        for neighbor_id in node.neighbors:

            neighbor = maze_map.get_node(
                neighbor_id
            )

            direction = np.sign(
                neighbor.position - node.position
            ).astype(int)

            key = tuple(direction)

            node.add_hallway_bit(direction)

            node.hallway_neighbors[key] = neighbor_id

    return maze_map

def grid_to_id(i,j,k,N):
    return i + N*j + N**2*k

def id_to_grid(node_id,N):

    i = node_id % N
    j = (node_id // N) % N
    k = node_id // (N**2)

    return i,j,k

def get_grid_neighbors(node_id,N):

    i,j,k = id_to_grid(
        node_id,
        N
    )

    neighbors = []

    directions = [
        (1,0,0),
        (-1,0,0),
        (0,1,0),
        (0,-1,0),
        (0,0,1),
        (0,0,-1)
    ]


    for di,dj,dk in directions:

        ni = i + di
        nj = j + dj
        nk = k + dk


        if (
            0 <= ni < N and
            0 <= nj < N and
            0 <= nk < N
        ):

            neighbors.append(
                grid_to_id(
                    ni,
                    nj,
                    nk,
                    N
                )
            )


    return neighbors
