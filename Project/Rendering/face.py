import numpy as np


class Face:

    def __init__(
        self,
        vertex_indices,
        uv_indices=None,
        normal_indices=None
    ):

        self.vertex_indices = np.array(
            vertex_indices
        )

        self.uv_indices = (
            np.array(uv_indices)
            if uv_indices is not None
            else None
        )

        self.normal_indices = (
            np.array(normal_indices)
            if normal_indices is not None
            else None
        )