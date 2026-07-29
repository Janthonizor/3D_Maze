
import numpy as np
import vtk
from collections import deque
import time

class Renderer:

    def __init__(
        self,
        plotter,
        maze_map,
        assets
    ):

        self.plotter = plotter
        
        self.plotter.ren_win.SetSize(
            1600,
            900
        )
 

        self.render_distance = 3

        self.maze_map = maze_map

        self.assets = assets
        self.actor_pairs = {}
        self.visible_node_ids = set()



        self.player_sphere = None
        self.player_up_arrow = None
        self.player_forward_arrow = None
        self.player_offset = 0.2

        self.snail = assets.snail
        self.snail_parts = []

    def create_player_actor(self):
        
        for part in self.snail:
            actor = self.plotter.add_mesh(
                part["mesh"],
                color=part["material"]["color"],
                smooth_shading=False,
                specular=part["material"]["specular"],
                specular_power=part["material"]["specular_power"]
            )
            self.snail_parts.append(actor)

    def update_frame(
        self,
        player_frame,
        camera_frame
    ):

        player_position = player_frame["position"]
        player_up = player_frame["up"]
        player_forward = player_frame["forward"]

        camera_position = camera_frame["position"]
        camera_up = camera_frame["up"]
        camera_forward = camera_frame["forward"]


        actor_position = (
            player_position
            +
            self.player_offset * player_up
        )

        for actor in self.snail_parts:
            self.orient_actor(
                actor,
                actor_position,
                player_forward,
                player_up
            )


        camera_look_at = (
            camera_position
            +
            camera_forward
        )


        self.plotter.camera.position = camera_position

        self.plotter.camera.focal_point = camera_look_at

        self.plotter.camera.up = camera_up

        self.plotter.camera.view_angle = 110

    def add_all_actors(self):

        count = 0

        for _, node in self.maze_map.nodes.items():

            # position actors once
            node.mesh_actor.SetPosition(
                *node.position
            )

            node.edge_actor.SetPosition(
                *node.position
            )

            # add to VTK scene
            self.plotter.add_actor(
                node.mesh_actor
            )

            self.plotter.add_actor(
                node.edge_actor
            )

            # start hidden
            node.mesh_actor.VisibilityOff()
            node.edge_actor.VisibilityOff()

            count += 1


    def update_visible_nodes(
        self,
        visible_node_ids
    ):

        visible_node_ids = set(
            visible_node_ids
        )

        nodes_to_add = (
            visible_node_ids
            -
            self.visible_node_ids
        )

        nodes_to_remove = (
            self.visible_node_ids
            -
            visible_node_ids
        )


        # -------------------------
        # Enable new nodes
        # -------------------------

        for node_id in nodes_to_add:

            node = self.maze_map.nodes[node_id]

            node.mesh_actor.VisibilityOn()

            node.edge_actor.VisibilityOn()


        # -------------------------
        # Disable old nodes
        # -------------------------

        for node_id in nodes_to_remove:

            node = self.maze_map.nodes[node_id]

            node.mesh_actor.VisibilityOff()

            node.edge_actor.VisibilityOff()


        self.visible_node_ids = visible_node_ids

    def render(self):
        self.plotter.render()

    def on_resize(self, width, height):
        print(width, height)

    @staticmethod
    def orient_actor(
        actor,
        position,
        forward,
        up
    ):

        forward = np.asarray(
            forward,
            dtype=float
        )

        up = np.asarray(
            up,
            dtype=float
        )


        # normalize

        forward /= np.linalg.norm(
            forward
        )

        up /= np.linalg.norm(
            up
        )


        # -------------------------
        # build player frame
        # -------------------------

        # right handed system

        right = np.cross(
            forward,
            up
        )

        right /= np.linalg.norm(
            right
        )


        # re-orthogonalize up

        up = np.cross(
            right,
            forward
        )

        up /= np.linalg.norm(
            up
        )


        # -------------------------
        # create transform
        # -------------------------

        matrix = vtk.vtkMatrix4x4()


        # local X -> forward

        matrix.SetElement(
            0,0,
            forward[0]
        )
        matrix.SetElement(
            1,0,
            forward[1]
        )
        matrix.SetElement(
            2,0,
            forward[2]
        )


        # local Y -> right

        matrix.SetElement(
            0,1,
            right[0]
        )
        matrix.SetElement(
            1,1,
            right[1]
        )
        matrix.SetElement(
            2,1,
            right[2]
        )


        # local Z -> up

        matrix.SetElement(
            0,2,
            up[0]
        )
        matrix.SetElement(
            1,2,
            up[1]
        )
        matrix.SetElement(
            2,2,
            up[2]
        )


        # translation

        matrix.SetElement(
            0,3,
            position[0]
        )

        matrix.SetElement(
            1,3,
            position[1]
        )

        matrix.SetElement(
            2,3,
            position[2]
        )


        matrix.SetElement(
            3,3,
            1
        )


        actor.SetUserMatrix(
            matrix
        )

        return actor


