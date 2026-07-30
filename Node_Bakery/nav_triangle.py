import numpy as np

class NavTriangle:

    def __init__(
        self,
        id,
        vertex_indices
    ):

        self.id = id

        # indices into node vertex array
        self.vertex_indices = np.array(
            vertex_indices,
            dtype=np.int32
        )

        # local adjacency
        self.neighbor_ids = []

        # baked geometry data
        self.normal = None
        self.center = None


