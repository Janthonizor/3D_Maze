from .active_nav_mesh import ActiveNavMesh
class ActiveSurfaceStreamer:

    def __init__(
        self,
        level,
        start_node_id
    ):

        self.level = level

        self.maze_map = level.maze_map

        self.current_node_id = start_node_id

        self.active_meshes = {}

        self.axis_dict = {
            (1,0,0):(1,0),
            (-1,0,0):(0,1),
            (0,1,0):(3,2),
            (0,-1,0):(2,3),
            (0,0,1):(5,4),
            (0,0,-1):(4,5)
        }

    def get_mesh(self, node_id):

        return self.level.nav_meshes[node_id]

    def stitch_mesh(
        self,
        adjacent_mesh,
        new_mesh,
        direction
    ):

        loopA, loopB = self.axis_dict[
            tuple(direction.astype(int))
        ]

        A = adjacent_mesh.boundary_triangles[loopA]
        B = new_mesh.boundary_triangles[loopB]

        assert len(A) == len(B) and len(A) > 0

        for triA_id, triB_id in zip(A, B):

            adjacent_mesh.tri_connections[triA_id][2] = (
                new_mesh.mesh_id,
                triB_id
            )

            new_mesh.tri_connections[triB_id][2] = (
                adjacent_mesh.mesh_id,
                triA_id
            )

    def unstitch_mesh(
        self,
        adjacent_mesh,
        discard_mesh,
        direction
    ):
        self.debug = False
        loopA, loopB = self.axis_dict[
            tuple(direction.astype(int))
        ]

        A = adjacent_mesh.boundary_triangles[loopA]
        B = discard_mesh.boundary_triangles[loopB]

        assert len(A) == len(B)

        for triA_id, triB_id in zip(A, B):

            adjacent_mesh.tri_connections[triA_id][2] = (
                -1,
                -1
            )

            discard_mesh.tri_connections[triB_id][2] = (
                -1,
                -1
            )

    def initialize_active_meshes(self):

        current_mesh = self.get_mesh(self.current_node_id)

        self.active_meshes[self.current_node_id] = current_mesh

        new_neighbor_ids = self.maze_map.nodes[self.current_node_id].neighbors

        for new_neighbor_id in new_neighbor_ids:

            new_mesh = self.get_mesh(new_neighbor_id)

            self.stitch_mesh(
                current_mesh,
                new_mesh,
                self.maze_map.get_node_direction(self.current_node_id, new_neighbor_id)
            )

            self.active_meshes[new_neighbor_id] = new_mesh

    def update_active_meshes(self, new_node_id):

        assert new_node_id in self.active_meshes

        assert len(self.active_meshes) <= 7

        if new_node_id == self.current_node_id:
            return

        old_current_id = self.current_node_id

        old_neighbors = (
            set(self.active_meshes.keys())
            - {old_current_id, new_node_id}
        )
   
        old_mesh = self.active_meshes[old_current_id]

        for neighbor_id in old_neighbors:

            neighbor_mesh = self.active_meshes[neighbor_id]

            self.unstitch_mesh(
                old_mesh,
                neighbor_mesh,
                self.maze_map.get_node_direction(
                    old_current_id,
                    neighbor_id
                )
            )

            del self.active_meshes[neighbor_id]

        self.current_node_id = new_node_id

        current_mesh = self.active_meshes[new_node_id]

        neighbors = self.maze_map.nodes[
            new_node_id
        ].neighbors

        for neighbor_id in neighbors:

            if neighbor_id in self.active_meshes:
                continue

            new_mesh = self.get_mesh(neighbor_id)

            self.stitch_mesh(
                current_mesh,
                new_mesh,
                self.maze_map.get_node_direction(
                    new_node_id,
                    neighbor_id
                )
            )

            self.active_meshes[neighbor_id] = new_mesh
