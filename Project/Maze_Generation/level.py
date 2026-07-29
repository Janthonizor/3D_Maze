from .maze_gen import generate_maze
import numpy as np
import colorsys
import vtk
from vtkmodules.util import numpy_support

class Level:

    def __init__(
        self,
        N,
        grid_spacing,
        branchiness,
        seed
    ):

        self.N = N
        self.grid_spacing = grid_spacing
        self.branchiness = branchiness

        self.seed = seed

        self.maze_map = None

        self.generate()

    def generate(self):

        self.maze_map = generate_maze(
            self.N,
            self.grid_spacing,
            self.branchiness,
            self.seed
        )

    def build_node_color_maps(
        self,
        assets
    ):

        # find world bounds

        positions = np.array([
            node.position
            for node in self.maze_map.nodes.values()
        ])


        min_position = positions.min(
            axis=0
        )

        max_position = positions.max(
            axis=0
        )


        for _, node in self.maze_map.nodes.items():

            render_mesh = assets.render_meshes[
                node.type_id
            ]


            # local mesh points -> world coordinates

            world_points = (
                render_mesh.points
                +
                node.position
            )


            colors = self.generate_point_colors(
                world_points,
                min_position,
                max_position
            )
            vtk_colors = self.convert_colors_to_vtk(colors)
            node.colors = vtk_colors

    def build_actors(self, assets):

        texture = assets.texture

        for node in self.maze_map.nodes.values():

            mesh_polydata = assets.render_meshes[
                node.type_id
            ]

            edge_polydata = assets.edge_meshes[
                node.type_id
            ]

            polydata = mesh_polydata.copy()


            polydata.GetPointData().SetScalars(
                node.colors
            )

            mapper = vtk.vtkPolyDataMapper()

            mapper.SetInputData(
                polydata
            )

            mapper.ScalarVisibilityOn()
            mapper.SetScalarModeToUsePointData()
            mapper.SetColorModeToDirectScalars()
            mapper.InterpolateScalarsBeforeMappingOff()


            actor = vtk.vtkActor()

            actor.SetMapper(
                mapper
            )

            actor.SetTexture(
                texture
            )

            actor.GetProperty().SetLighting(
                False
            )


            # -----------------------
            # Edge mesh
            # -----------------------

            edge_mapper = vtk.vtkPolyDataMapper()

            edge_mapper.SetInputData(
                edge_polydata
            )

            edge_actor = vtk.vtkActor()

            edge_actor.SetMapper(
                edge_mapper
            )

            edge_actor.GetProperty().SetColor(
                0, 0, 0
            )
            edge_actor.GetProperty().SetLineWidth(
                2.0
            )
            edge_mapper.SetResolveCoincidentTopologyToPolygonOffset()


            # -----------------------
            # Store
            # -----------------------

            node.mesh_actor = actor
            node.edge_actor = edge_actor

    def assign_nav_data(self,assets):
        for node in self.maze_map.nodes.values():
            node.nav_data = assets.nav_library[node.type_id]
            

    @staticmethod
    def convert_colors_to_vtk(colors):

        colors = np.asarray(
            colors,
            dtype=float
        )

        colors = (
            colors * 255
        ).clip(
            0,
            255
        ).astype(
            np.uint8
        )

        vtk_colors = numpy_support.numpy_to_vtk(
            colors,
            deep=True,
            array_type=vtk.VTK_UNSIGNED_CHAR
        )

        vtk_colors.SetNumberOfComponents(
            3
        )

        vtk_colors.SetName(
            "Scalars"
        )

        return vtk_colors
    @staticmethod
    def generate_point_colors(
        points,
        min_position,
        max_position
    ):

        points = np.asarray(
            points,
            dtype=float
        )


        normalized = (
            points - min_position
        ) / (
            max_position - min_position
        )


        colors = np.zeros(
            (len(points), 3),
            dtype=float
        )


        for i, (x, y, z) in enumerate(normalized):

            hue = (
                4*x +
                4*1.2*y +
                4*1.5*z
            ) / 15


            colors[i] = colorsys.hsv_to_rgb(
                hue % 1,
                0.75,
                1
            )


        return colors
