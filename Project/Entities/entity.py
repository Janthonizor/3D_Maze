class SurfaceEntity:

    def __init__(
        self,
        node_id,
        triangle_id,
        barycentric,
        mesh
    ):

        self.node_id = node_id
        self.triangle_id = triangle_id

        self.barycentric = barycentric

        self.mesh = mesh

        self.update_surface_frame()

        self.actor = None
        self.active = True