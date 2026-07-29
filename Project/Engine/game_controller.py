from Navigation.active_surface_streamer import ActiveSurfaceStreamer
from Navigation.triangle_query import TriangleQuery
from Gameplay.player import Player
from Gameplay.camera import Camera
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal
import time
import numpy as np

class GameController(QObject):
    
    ready = pyqtSignal()
    finished = pyqtSignal(object)

    def __init__(
        self,
        level,
        renderer,
        window,
        input_manager
    ):
        super().__init__()
        self.level = level

        self.renderer = renderer

        self.window = window

        self.window.game_screen.game_plotter.resized.connect(
            renderer.on_resize
        )

        self.input_manager = input_manager

        self.debug = True

        self.current_node = 0

        self.visible_nodes = set()

        self.hit = None


        self.surface = ActiveSurfaceStreamer(
            level.maze_map,
            self.current_node
        )

        self.triangle_query = None

        self.physics_dt = 1.0 / 60.0

        self.accumulator = 0.0

        self.alpha = 0.0

        self.player = None

        self.camera = None

        self.timer = None

        self.camera_collision_timer = 0.0

        self.collision_meshes = []


    def initialize(self):

        self.surface.initialize_active_meshes()

        self.triangle_query = TriangleQuery(self.surface)

        self.player = Player(
            self.triangle_query,
            0,
            self.current_node,
            [1/3, 1/3, 1/3]
        )

        self.player.create_frame()

        self.camera = Camera()

        self.camera.initialize_frame(
            self.player.get_frame()
        )

        self.window.game_screen.hud.initialize(
            self.level.maze_map,
            self.player.get_frame()
        )

        self.window.game_screen.hud.update_hud(
            self.level.maze_map,
            self.current_node,
            self.player.get_frame()
        )

        self.renderer.add_all_actors()

        self.get_visible_nodes()

        self.update_renderer_visibility()

        self.renderer.update_frame(
            self.player.get_interpolated_frame(1.0),
            self.camera.get_interpolated_frame(1.0)
        )

        self.ready.emit()


    def start(self):

        self.renderer.create_player_actor()

        self.renderer.update_frame(
            self.player.get_interpolated_frame(1.0),
            self.camera.get_interpolated_frame(1.0)
        )

        self.renderer.render()


        self.accumulator = 0.0

        self.previous_time = time.perf_counter()

        self.timer = QTimer()

        self.timer.timeout.connect(self.tick)

        self.timer.start(8)


    def physics_step(
        self,
        input_state,
        dt
    ):
        self.player.save_previous_render_state()

        self.update_player(
            input_state,
            dt
        )

        self.player.update_render_state()

        self.update_surface()


        self.camera.save_previous_render_state()

        self.camera.update_input(
            input_state,
            dt
        )

        self.camera.update_frame(
            self.player.get_frame(),
            dt
        )

        cam_look = self.renderer.plotter.camera.GetDirectionOfProjection()
        cam_pos = self.renderer.plotter.camera.position

        self.hit = self.raycast_surface(
            self.triangle_query,
            self.player.current_tri,
            cam_pos, 
            cam_look,
            20,
            1.0,
            self.player.position
        )

        self.camera_collision_timer += dt

        if self.camera_collision_timer > 0.1:

            self.camera.solve_collision(
                self.collision_meshes,
                dt
            )

            self.camera_collision_timer = 0

        self.camera.update_render_state()


    def render_step(self):

        self.renderer.update_frame(
            self.player.get_interpolated_frame(
                self.alpha
            ),
            self.camera.get_interpolated_frame(
                self.alpha
            )
        )

        self.renderer.update_triangle_highlight_actor(
            self.hit
        )


        self.renderer.render()

        self.window.game_screen.hud.update_hud(
            self.level.maze_map,
            self.current_node,
            self.player.get_frame()
        )


    def tick(self):

        current_time = time.perf_counter()

        frame_time = (
            current_time
            -
            self.previous_time
        )

        self.previous_time = current_time


        self.accumulator += frame_time



        input_state = self.get_input()


        physics_count = 0



        while (
            self.accumulator >= self.physics_dt
        ):

            self.physics_step(
                input_state,
                self.physics_dt
            )

            self.accumulator -= self.physics_dt

            physics_count += 1

        

        self.alpha = (
            self.accumulator
            /
            self.physics_dt
        )

        self.render_step()


    def get_input(self):

        mouse_dx, mouse_dy = (
            self.input_manager.get_mouse_delta()
        )

        return {

            "forward":
                self.input_manager.down(Qt.Key_W),

            "back":
                self.input_manager.down(Qt.Key_S),

            "left":
                self.input_manager.down(Qt.Key_A),

            "right":
                self.input_manager.down(Qt.Key_D),

            "mouse_dx":
                mouse_dx,

            "mouse_dy":
                mouse_dy
        }


    def update_player(
        self,
        input_state,
        dt
    ):


        if input_state["forward"]:

            self.player.move_forward(
                self.player.move_speed,
                dt
            )


        if input_state["back"]:

            self.player.move_forward(
                -self.player.move_speed,
                dt
            )


        if input_state["left"]:

            self.player.rotate(
                self.player.turn_speed,
                dt
            )


        if input_state["right"]:

            self.player.rotate(
                -self.player.turn_speed,
                dt
            )


    def update_surface(self):

        new_node = self.player.get_node_id()


        if new_node == self.current_node:
            return


        self.surface.update_active_meshes(
            new_node
        )

        self.current_node = new_node


        self.get_visible_nodes()

        self.update_renderer_visibility()


    def get_visible_nodes(self):

        layers, _ = self.level.maze_map.get_stream_tree(
            self.current_node,
            self.renderer.render_distance
        )

        self.visible_nodes = {
            node_id
            for layer in layers
            for node_id in layer
        }


    def update_renderer_visibility(self):

        self.renderer.update_visible_nodes(
            self.visible_nodes
        )


        self.update_collision_meshes()


    def update_collision_meshes(self):
        current_node = self.level.maze_map.nodes[self.current_node]
        polydata = (
            current_node.mesh_actor
            .GetMapper()
            .GetInput()
        )
        current_position = current_node.position

        collision_meshes = [(polydata, current_position)]

        for node_id in self.level.maze_map.nodes[self.current_node].neighbors:

            node = self.level.maze_map.nodes[node_id]

            polydata = (
                node.mesh_actor
                .GetMapper()
                .GetInput()
            )

            collision_meshes.append(
                (
                    polydata,
                    node.position
                )
            )

        self.collision_meshes = collision_meshes


    def ray_triangle_intersection(
        self,
        origin,
        direction,
        vertices
    ):

        epsilon = 1e-8

        edge1 = vertices[1] - vertices[0]
        edge2 = vertices[2] - vertices[0]

        h = np.cross(
            direction,
            edge2
        )

        a = np.dot(
            edge1,
            h
        )

        if abs(a) < epsilon:
            return None

        f = 1.0 / a

        s = origin - vertices[0]

        u = f * np.dot(
            s,
            h
        )

        if u < 0 or u > 1:
            return None

        q = np.cross(
            s,
            edge1
        )

        v = f * np.dot(
            direction,
            q
        )

        if v < 0 or u + v > 1:
            return None

        # distance along ray
        distance = f * np.dot(
            edge2,
            q
        )

        if distance > epsilon:
            return distance

        return None


    def raycast_surface(
        self,
        triangle_query,
        root_triangle,
        origin,
        direction,
        max_depth,
        max_distance,
        cull_position = None
    ):
        if cull_position is None:

            cull_position = origin

        direction = direction/np.linalg.norm(direction)

        triangle_cache = triangle_query.get_cache(root_triangle, max_depth)

        for _ , layer in enumerate(triangle_cache):

            for triangle in layer:

                tri_center = triangle_query.get_tri_center(triangle)

                dist_from_target = np.linalg.norm(tri_center - cull_position)

                if dist_from_target > max_distance:
                    continue

                vertices = triangle_query.get_tri_verts(triangle)

                distance = self.ray_triangle_intersection(
                    origin,
                    direction,
                    vertices
                )

                if distance == None:
                    continue

                tri_normal = triangle_query.get_tri_norm(triangle)

                epsilon = 0.005

                lifted_vertices = vertices + tri_normal * epsilon


                return triangle, lifted_vertices

        return None


    def stop(self):

            if self.timer:

                self.timer.stop()

                self.timer.deleteLater()

                self.timer = None

