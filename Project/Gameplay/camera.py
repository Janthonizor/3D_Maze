import numpy as np


class Camera:

    def __init__(self):

        # --------------------
        # Camera controls
        # --------------------
        self.mouse_sensitivity = 0.2

        self.yaw = 0.0
        self.pitch = 20.0

        self.target_yaw = self.yaw
        self.target_pitch = self.pitch

        # pitch limits
        self.min_pitch = -5.0
        self.max_pitch = 90.0

        # radius constraints
        self.radius = 0.5

        # controls
        self.yaw_speed = 80.0
        self.pitch_speed = 80.0

        # camera offset
        self.height_offset = 0.6
        self.look_distance = 0.5
        self.orbit_direction = None


        self.position = np.zeros(3)
        self.look_at = np.zeros(3)

        self.forward = np.array(
            [1,0,0],
            dtype=float
        )

        self.up = np.array(
            [0,0,1],
            dtype=float
        )

        self.right = np.array([0,0,0], dtype=float)

        self.player_position = None
        self.player_up = None
        self.player_forward = None

        self.previous_position_frame = None
        self.current_position_frame = self.position.copy()

        self.previous_up_frame = None
        self.current_up_frame = self.up.copy()

        self.previous_forward_frame = None
        self.current_forward_frame = self.forward.copy()


    def initialize_frame(
            self,
            player_frame
        ):

            position, up, forward = player_frame

            self.player_position = (
                np.asarray(position)
            )

            self.player_up = up

            self.player_forward  = forward

            self.solve_camera()

            self.current_position_frame = self.position.copy()
            self.previous_position_frame = self.position.copy()

            self.current_up_frame = self.up.copy()
            self.previous_up_frame = self.up.copy()

            self.previous_forward_frame = self.forward.copy()
            self.current_forward_frame = self.forward.copy()
            
     
    def update_input(
        self,
        input_state,
        dt
    ):

        self.target_yaw -= (
            input_state["mouse_dx"] * self.mouse_sensitivity
        )
        self.target_pitch -=(
            input_state["mouse_dy"] * self.mouse_sensitivity
        )

        self.target_pitch = np.clip(
            self.target_pitch,
            self.min_pitch,
            self.max_pitch
        )

        smooth_speed = 20.0

        alpha = 1.0 - np.exp(
            -smooth_speed * dt
        )

        self.yaw += (
            self.target_yaw - self.yaw
        ) * alpha


        self.pitch += (
            self.target_pitch - self.pitch
        ) * alpha


        self.pitch = np.clip(
            self.pitch,
            self.min_pitch,
            self.max_pitch
        )


    def update_frame(
        self,
        player_frame
    ):

        position, up, forward = player_frame


        self.player_position = (
            np.asarray(position)
        )

        self.player_up = (
            up /
            np.linalg.norm(up)
        )

        self.player_forward = (
            forward /
            np.linalg.norm(forward)
        )

        self.solve_camera()


    def solve_camera(self):

        self.solve_camera_position()

        self.solve_camera_orientation()


    def solve_camera_position(self):

        up = self.player_up

        forward = self.player_forward


        # start behind player
        orbit_direction = -forward


        # yaw rotation around player up axis
        angle = np.deg2rad(self.yaw)

        orbit_direction = self.rotate(
            orbit_direction,
            up,
            angle
        )

        orbit_direction /= np.linalg.norm(
            orbit_direction
        )


        self.orbit_direction = orbit_direction


        # camera position
        self.position = (
            self.player_position
            +
            orbit_direction * self.radius
            +
            up * self.height_offset
        )


    def solve_camera_orientation(self):

        up = self.player_up 

        forward = (
            self.player_position -
            self.position
        )

        forward /= np.linalg.norm(forward)


        # build camera right axis
        right = np.cross(
            forward,
            up
        )


        # apply pitch around camera right axis
        forward = self.rotate(
            forward,
            right,
            np.deg2rad(self.pitch)
        )

        forward /= np.linalg.norm(forward)


        # rebuild up so frame stays orthogonal
        up = np.cross(
            right,
            forward
        )

        up /= np.linalg.norm(up)


        self.forward = forward
        self.up = up
        self.right = right

        self.look_at = (
            self.position +
            forward *
            self.look_distance
        )

            
    def get_frame(self):

        return (
            self.position,
            self.look_at,
            self.up
        )


    def save_previous_render_state(self):

        self.previous_position_frame = (
            self.current_position_frame.copy()
        )

        self.previous_forward_frame = (
            self.current_forward_frame.copy()
        )

        self.previous_up_frame = (
            self.current_up_frame.copy()
        )


    def update_render_state(self):

        self.current_position_frame = (
            self.position.copy()
        )

        self.current_forward_frame = (
            self.forward.copy()
        )

        self.current_up_frame = (
            self.up.copy()
        )


    def get_interpolated_frame(self, alpha):

        # position interpolation
        position = (
            self.previous_position_frame * (1.0 - alpha)
            +
            self.current_position_frame * alpha
        )


        # up vector interpolation
        up = (
            self.previous_up_frame * (1.0 - alpha)
            +
            self.current_up_frame * alpha
        )

        up_length = np.linalg.norm(up)

        if up_length > 1e-8:
            up /= up_length


        # forward vector interpolation
        forward = (
            self.previous_forward_frame * (1.0 - alpha)
            +
            self.current_forward_frame * alpha
        )

        forward_length = np.linalg.norm(forward)

        if forward_length > 1e-8:
            forward /= forward_length


        return {
            "position": position,
            "up": up,
            "forward": forward
        }

    
    @staticmethod
    def rotate( vector, axis, angle):

        axis = axis / np.linalg.norm(axis)

        cos_theta = np.cos(angle)
        sin_theta = np.sin(angle)

        return (
            vector * cos_theta
            +
            np.cross(axis, vector) * sin_theta
            +
            axis * np.dot(axis, vector) * (1 - cos_theta)
        )

    
    @staticmethod
    def build_euler_matrix(angles):
        """
        Build XYZ Euler rotation matrix.

        angles:
            [rx, ry, rz] in degrees

        Returns:
            3x3 rotation matrix
        """

        rx, ry, rz = np.deg2rad(angles)

        cx = np.cos(rx)
        sx = np.sin(rx)

        cy = np.cos(ry)
        sy = np.sin(ry)

        cz = np.cos(rz)
        sz = np.sin(rz)


        Rx = np.array([
            [1, 0, 0],
            [0, cx, -sx],
            [0, sx, cx]
        ])

        Ry = np.array([
            [cy, 0, sy],
            [0, 1, 0],
            [-sy, 0, cy]
        ])

        Rz = np.array([
            [cz, -sz, 0],
            [sz, cz, 0],
            [0, 0, 1]
        ])


        # same order as renderer
        return Rz @ Ry @ Rx

