import numpy as np

DIRECTION_BITS = {
    ( 1, 0, 0): 0,
    (-1, 0, 0): 1,
    ( 0, 1, 0): 2,
    ( 0,-1, 0): 3,
    ( 0, 0, 1): 4,
    ( 0, 0,-1): 5,
}

DIRECTION_NAMES = {
    ( -1, 0, 0): "+x",
    (1, 0, 0): "-x",
    ( 0, -1, 0): "+y",
    ( 0,1, 0): "-y",
    ( 0, 0, -1): "+z",
    ( 0, 0,1): "-z",
}

class MazeNode:

    def __init__(self, node_id, position):

        self.id = node_id

        self.position = np.array(
            position,
            dtype=float
        )

        self.neighbors = []
        self.hallway_neighbors = {}
        self.type_id = 0
        self.colors = None
        self.mesh_actor = None
        self.edge_actor = None
        self.nav_mesh = None
        self.entities = {}

    def add_neighbor(self, node_id):

        if node_id not in self.neighbors:
            self.neighbors.append(node_id)

    def add_hallway_bit(self, direction):

        key = tuple(np.array(direction).astype(int))

        bit = DIRECTION_BITS[key]

        self.type_id |= (1 << bit)
    
    def has_hallway(self, direction):

        key = tuple(direction)

        bit = DIRECTION_BITS[key]

        return (
            self.type_id >> bit
        ) & 1

    