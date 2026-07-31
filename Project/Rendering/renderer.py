
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
        self.foreground_renderer = None
        self.create_foreground_renderer()
        
        self.plotter.ren_win.SetSize(
            1600,
            900
        )
 
        self.selected_triangle_actor = None
        self.selected_triangle_key = None
        self.render_distance = 2

        self.maze_map = maze_map

        self.assets = assets
        self.actor_pairs = {}
        self.visible_node_ids = set()



        self.player_sphere = None
        self.player_up_arrow = None
        self.player_forward_arrow = None
        self.player_offset = 0.2

        self.reticle = None
        self.reticle_base_points = np.array([
            [-0.2,0,0],
            [0.2,0,0],
            [0,-0.2,0],
            [0, 0.2,0],
            [-1,0,0],
            [1,0,0],
            [0,-1,0],
            [0,1,0]
        ])
        self.reticle_points = None

        self.snail = assets.snail
        self.snail_parts = []

    def create_foreground_renderer(self):
        self.foreground_renderer = vtk.vtkRenderer()
        self.foreground_renderer.SetLayer(1)
        self.plotter.ren_win.SetNumberOfLayers(2)
        self.plotter.ren_win.AddRenderer(
            self.foreground_renderer
        )

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

    def initialize_reticle(self):

        self.reticle_points = vtk.vtkPoints()

        # center
        for point in self.reticle_base_points:
            self.reticle_points.InsertNextPoint(
                *point
            )


        lines = vtk.vtkCellArray()

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 0)
        line.GetPointIds().SetId(1, 4)
        lines.InsertNextCell(line)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 1)
        line.GetPointIds().SetId(1, 5)
        lines.InsertNextCell(line)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 2)
        line.GetPointIds().SetId(1, 6)
        lines.InsertNextCell(line)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 3)
        line.GetPointIds().SetId(1, 7)
        lines.InsertNextCell(line)


        polydata = vtk.vtkPolyData()

        polydata.SetPoints(self.reticle_points)
        polydata.SetLines(lines)


        mapper = vtk.vtkPolyDataMapper2D()

        mapper.SetInputData(
            polydata
        )


        self.reticle = vtk.vtkActor2D()

        self.reticle.SetMapper(
            mapper
        )


        self.reticle.GetProperty().SetColor(
            1,
            1,
            1
        )

        self.reticle.GetProperty().SetLineWidth(
            1
        )
        self.update_reticle_scale(self.plotter.width(), self.plotter.height())

        width = self.plotter.width()

        height = self.plotter.height()

        self.reticle.SetPosition(
            width / 2,
            height / 2
        )

        self.foreground_renderer.AddActor2D(
            self.reticle
        )

    def update_reticle_scale(self, width, height):

        size = min(width, height) * 0.03

        for i, point in enumerate(self.reticle_base_points):

            scaled = point * size

            self.reticle_points.SetPoint(
                i,
                *scaled
            )

        self.reticle_points.Modified()

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

        self.plotter.camera.view_angle = 100

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

        self.initialize_reticle()

    def update_triangle_highlight_actor(
        self,
        raycast_result
    ):

        triangle_ids, vertices, distances, normals = raycast_result


        # -------------------------
        # No selection
        # -------------------------

        if len(triangle_ids) == 0:

            if self.selected_triangle_actor is not None:
                self.selected_triangle_actor.VisibilityOff()

            return


        # closest hit
        best = np.argmin(distances)

        triangle_key = triangle_ids[best]

        adjust_direction = normals[best]

        vertices = vertices[best]+adjust_direction*0.01

        # -------------------------
        # Create actor if needed
        # -------------------------

        if self.selected_triangle_actor is None:
            print("no actor")
            points = vtk.vtkPoints()
            points.InsertNextPoint(0, 0, 0)
            points.InsertNextPoint(0, 0, 0)
            points.InsertNextPoint(0, 0, 0)

            lines = vtk.vtkCellArray()

            for a, b in [
                (0, 1),
                (1, 2),
                (2, 0)
            ]:

                line = vtk.vtkLine()

                line.GetPointIds().SetId(
                    0,
                    a
                )

                line.GetPointIds().SetId(
                    1,
                    b
                )

                lines.InsertNextCell(
                    line
                )


            polydata = vtk.vtkPolyData()

            polydata.SetPoints(
                points
            )

            polydata.SetLines(
                lines
            )


            mapper = vtk.vtkPolyDataMapper()

            mapper.SetInputData(
                polydata
            )

            #mapper.SetResolveCoincidentTopologyToPolygonOffset()

            actor = vtk.vtkActor()

            actor.SetMapper(
                mapper
            )


            actor.GetProperty().SetColor(
                1,
                0,
                0
            )

            actor.GetProperty().SetLineWidth(
                3
            )

            

            self.selected_triangle_actor = actor

            self.plotter.add_actor(
                actor
            )


        
        polydata = (
            self.selected_triangle_actor
            .GetMapper()
            .GetInput()
        )


        points = polydata.GetPoints()

        for i in range(len(vertices)):

            points.SetPoint(i, *vertices[i])

        points.Modified()

        polydata.Modified()


        # -------------------------
        # Show highlight
        # -------------------------
        self.selected_triangle_key = raycast_result[0]
        
        self.selected_triangle_actor.VisibilityOn()

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

        self.screen_size = (
            width,
            height
        )

        self.reticle.SetPosition(
            width / 2,
            height / 2
        )

        self.update_reticle_scale(
            width,
            height
        )

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


