from Navigation.active_surface_streamer import ActiveSurfaceStreamer
from Navigation.triangle_query import TriangleQuery
from Collision.triangle_raycast import *
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
            level,
            self.current_node
        )

        self.triangle_query = None

        self.physics_dt = 1.0 / 120.0

        self.accumulator = 0.0

        self.alpha = 0.0

        self.player = None

        self.camera = None

        self.timer = None

        self.camera_collision_timer = 0.0

        self.max_physics_steps = 3


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
        self.window.game_screen.hud.update_stamina(
            self.player.state.stamina,
            self.player.state.max_stamina,
            self.player.state.sprint_locked
        )

        self.player.update_render_state()

        self.update_surface()

        self.camera.save_previous_render_state()

        self.camera.update_input(
            input_state,
            dt
        )

        self.camera.update_frame(
            self.player.get_frame()
        )

        self.camera.update_render_state()

        cam_look = self.renderer.plotter.camera.GetDirectionOfProjection()

        cam_pos = self.renderer.plotter.camera.position

        self.hit = self.triangle_query.raycast(
            self.player.position, 
            cam_pos,
            cam_look,
            1.5
        )


        
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

        tick_start = time.perf_counter()

        frame_time = (
            tick_start
            -
            self.previous_time
        )

        self.previous_time = tick_start

        self.accumulator += frame_time

        input_state = self.get_input()

        physics_count = 0

        while (self.accumulator >= self.physics_dt
            and physics_count < self.max_physics_steps
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

            "sprint":
                self.input_manager.down(Qt.Key_Shift),

            "mouse_dx":
                mouse_dx,

            "mouse_dy":
                mouse_dy
        }


    def update_player(self, input_state, dt):

        move = 0
        turn = 0

        if input_state["forward"]:
            move += 1

        if input_state["back"]:
            move -= 1

        if input_state["left"]:
            turn += 1

        if input_state["right"]:
            turn -= 1

        sprint = input_state["sprint"]

        self.player.update(
            move=move,
            turn=turn,
            sprint=sprint,
            dt=dt
        )


    def update_surface(self):

        start = time.perf_counter()

        new_node = self.player.get_node_id()

        if new_node == self.current_node:
            return


        update_start = time.perf_counter()

        self.surface.update_active_meshes(
            new_node
        )

        update_time = time.perf_counter() - update_start


        self.current_node = new_node


        visible_start = time.perf_counter()

        self.get_visible_nodes()

        visible_time = time.perf_counter() - visible_start


        renderer_start = time.perf_counter()

        self.update_renderer_visibility()

        renderer_time = time.perf_counter() - renderer_start


        total_time = time.perf_counter() - start


        if total_time > 0.010:
            print(
                f"""
    Surface update spike: {total_time*1000:.2f} ms
        update_active_meshes: {update_time*1000:.2f} ms
        get_visible_nodes:     {visible_time*1000:.2f} ms
        renderer_visibility:   {renderer_time*1000:.2f} ms
    """
            )

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


        #self.update_collision_meshes()


    def stop(self):

            if self.timer:

                self.timer.stop()

                self.timer.deleteLater()

                self.timer = None

