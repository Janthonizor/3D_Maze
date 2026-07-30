import numpy as np
from collections import deque


class Player:

    def __init__(
        self,
        triangle_query,
        start_triangle_id,
        start_mesh_id,
        start_bary
    ):
        self.triangle_query = triangle_query

        self.current_tri = (start_mesh_id, start_triangle_id)

        self.move_speed = 20

        self.turn_speed = 400

        self.forward_n = 0.7

        self.up_n = 0.2
        
        self.barycentric = np.asarray(start_bary, dtype = float)

        self.bary_epsilon = 1e-6

        self.movement_epsilon = 1e-4
        self.position = None

        self.up = None

        self.previous_up = None
 
        self.forward = None

        self.previous_forward = None

        self.velocity = np.zeros(3, dtype = np.float32)
        self.acceleration = np.zeros(3, dtype = np.float32)

        
        self.previous_position_frame = None
        self.current_position_frame = None

        self.previous_up_frame = None
        self.current_up_frame = None

        self.previous_forward_frame = None
        self.current_forward_frame = None

        # debugging

        self.movement_history = deque(maxlen = 20)
        self.triangle_bary_log = deque(maxlen = 20)



    def initialize_position(self):

        tri_verts = self.triangle_query.get_tri_verts(self.current_tri)

        self.position = (
            self.barycentric @ tri_verts
        )

        self.current_position_frame = self.position.copy()
        self.previous_position_frame = self.position.copy()


    def initialize_up(self):

        tri_vert_norms = self.triangle_query.get_tri_vert_norms(self.current_tri)

        self.up = (
            self.barycentric @ tri_vert_norms
        )

        self.up /= np.linalg.norm(
            self.up
        )

        self.previous_up = self.up.copy()
        self.current_up_frame = self.up.copy()
        self.previous_up_frame = self.up.copy()


    def initialize_forward(self):

        v0, v1, _ = self.triangle_query.get_tri_verts(self.current_tri)

        forward = v1 - v0

        forward -= (
            np.dot(forward, self.up)
            *
            self.up
        )

        length = np.linalg.norm(forward)

        assert length > 1e-3, (
            f"Degenerate forward vector on triangle {self.current_tri}. "
            f"Length={length}"
        )

        forward /= length

        self.forward = forward

        self.previous_forward = forward.copy()
        self.current_forward_frame = forward.copy()
        self.previous_forward_frame = forward.copy()

    
    def create_frame(self):

        self.initialize_position()

        self.initialize_up()
        
        self.initialize_forward()

    
    def update_up(self):

        tri_vert_norms = self.triangle_query.get_tri_vert_norms(self.current_tri)

        target = self.barycentric @ tri_vert_norms

        length = np.linalg.norm(target)

        assert length > 1e-3, (
            f"Degenerate interpolated normal on triangle {self.current_tri}. "
            f"Length={length}"
        )

        target /= length

        up_alpha = (self.up_n * self.move_speed) / (1 + self.up_n * self.move_speed)

        self.up = self.smooth_vector(
            self.previous_up,
            target,
            up_alpha
        )

        self.up /= np.linalg.norm(self.up)

        self.previous_up = self.up.copy()


    def update_forward(self):

        target = (
            self.forward
            - np.dot(self.forward, self.up) * self.up
        )

        length = np.linalg.norm(target)

        assert length > 1e-3, (
            f"Forward projection onto triangle plane failed {self.current_tri}"
        )

        target /= length

        alpha = (self.forward_n * self.move_speed) / (1 + self.forward_n * self.move_speed)

        self.forward = self.smooth_vector(
            self.previous_forward,
            target,
            alpha
        )

        self.forward -= (
            np.dot(self.forward, self.up)
            * self.up
        )

        self.forward /= np.linalg.norm(
            self.forward
        )

        self.previous_forward = self.forward.copy()

    
    def project_vector_to_triangle(
        self,
        vector,
        triangle_key
    ):

        normal = self.triangle_query.get_tri_norm(triangle_key)

        projected = (
            vector -
            np.dot(vector, normal)
            * normal
        )

        length = np.linalg.norm(projected)

        assert length > 1e-8, (
            f"Forward vector parallel to triangle normal on {triangle_key}"
        )

        return projected


    def find_exit_distance(
        self,
        distance,
        projected_forward,
        triangle_key
    ):

        end_position = (
            self.position +
            projected_forward * distance
        )

        end_bary = self.triangle_query.world_to_barycentric(
            end_position,
            triangle_key
        )

        bary_delta = (
            end_bary -
            self.barycentric
        )

        fraction = 1.0

        for i in range(3):

            if bary_delta[i] < 0:

                exit_fraction = (
                    -self.barycentric[i]
                    /
                    bary_delta[i]
                )

                fraction = min(
                    fraction,
                    exit_fraction
                )


        exit_bary = (
            self.barycentric +
            bary_delta * fraction
        )


        exit_bary = self.clean_bary(
            exit_bary,
            self.bary_epsilon
        )


        exit_distance = distance * fraction


        return exit_distance, exit_bary


    def step_current_triangle(self, distance):

        projected_forward = self.project_vector_to_triangle(
            self.forward,
            self.current_tri
        )

        movement = projected_forward * distance

        start = self.position
        end = start + movement

        
        end_bary = self.triangle_query.world_to_barycentric(
            end,
            self.current_tri
        )

        # check if end point in current_tri

        if (
            np.all(end_bary >= -self.bary_epsilon)
            and 
            np.all(end_bary <= 1 + self.bary_epsilon)
        ):

            self.barycentric = self.clean_bary(end_bary, self.bary_epsilon)

            self.position = self.triangle_query.barycentric_to_world(
                self.barycentric,
                self.current_tri
            )

            return distance, False


        # we crossed a boundary

        # find maximum valid distance in this triangle
        # keep bary as the primary source of truth

        valid_distance, edge_bary = self.find_exit_distance(
            distance,
            projected_forward,
            self.current_tri
        )

        self.barycentric = edge_bary

        self.position = self.triangle_query.barycentric_to_world(
            edge_bary, 
            self.current_tri
        )

        return valid_distance, True


    def find_next_triangle_at_exit_point(
        self,
    ):

        tri_connections = self.triangle_query.get_tri_connections(self.current_tri)

        candidates = 0

        
        for connection in tri_connections:

            connected_tri = connection

            if (connected_tri[1] < 0):
                continue

            candidates += 1

            bary = self.triangle_query.world_to_barycentric(
                self.position,
                connected_tri
            )

            self.triangle_bary_log.append(
                {
                    "current triangle": self.current_tri,
                    "current barycentric": self.barycentric,
                    "attempted tri": connection,
                    "attempted bary": bary
                }
            )

            if (
                np.all(bary >= -self.bary_epsilon)
                and
                np.all(bary <= 1 + self.bary_epsilon)
            ):

                return (
                    connected_tri,
                    bary
                )

        assert False, (
            f"No connected triangle found from {self.current_tri}\n"
            + "\n".join(
                str(entry)
                for entry in self.triangle_bary_log
            )
        )

  
    def move_forward(self, velocity, dt):

        remaining_distance = velocity * dt

        counter = 0

        while abs(remaining_distance) > self.movement_epsilon:

            counter+=1

            distance_travelled, crossed = self.step_current_triangle(
                remaining_distance
            )
            self.movement_history.append(
                {
                    "counter": counter,
                    "triangle": self.current_tri,
                    "barycentric": self.barycentric.copy(),
                    "position": self.position.copy(),
                    "distance_travelled": distance_travelled,
                    "crossed": crossed,
                    "remaining_distance": remaining_distance
                }
            )

            assert counter <= 20, (
                str(entry) for entry in self.movement_history
            )

            remaining_distance -= distance_travelled

            if not crossed:
                break

            result = self.find_next_triangle_at_exit_point()
            
            self.current_tri, self.barycentric = result

            self.position = self.triangle_query.barycentric_to_world(
                self.barycentric,
                self.current_tri
            )
        
        self.update_up()

        self.update_forward()


    def clean_bary(self, bary, epsilon):

        bary = bary.copy()

        # remove floating point noise
        bary[np.abs(bary) < epsilon] = 0.0

        # clamp tiny negatives caused by precision
        bary[bary < 0] = 0.0

        # renormalize
        bary /= np.sum(bary)

        return bary
    
    def rotate(self, angular_velocity, dt):
        
        angle = np.deg2rad(
            angular_velocity * dt
        )

        axis = self.up

        v = self.forward

        self.forward = (
            v * np.cos(angle)
            +
            np.cross(axis, v) * np.sin(angle)
            +
            axis * np.dot(axis, v)
            * (1 - np.cos(angle))
        )

        self.forward /= np.linalg.norm(
            self.forward
        )

        self.previous_forward = self.forward.copy()

    
    def get_frame(self):
        return self.position, self.up, self.forward

    
    def get_node_id(self):

        return self.current_tri[0]


    def save_previous_render_state(self):

        self.previous_position_frame = (
            self.current_position_frame.copy()
        )

        self.previous_up_frame = (
            self.current_up_frame.copy()
        )

        self.previous_forward_frame = (
            self.current_forward_frame.copy()
        )

            
    def update_render_state(self):

        self.current_position_frame = (
            self.position.copy()
        )

        self.current_up_frame = (
            self.up.copy()
        )

        self.current_forward_frame = (
            self.forward.copy()
        )


    def get_interpolated_frame(self, alpha):

        position = (
            self.previous_position_frame * (1.0 - alpha)
            +
            self.current_position_frame * alpha
        )

        up = (
            self.previous_up_frame * (1.0 - alpha)
            +
            self.current_up_frame * alpha
        )

        up /= np.linalg.norm(up)

        forward = (
            self.previous_forward_frame * (1.0 - alpha)
            +
            self.current_forward_frame * alpha
        )

        forward /= np.linalg.norm(forward)

        return {
            "position": position,
            "up": up,
            "forward": forward
        }


    @staticmethod
    def smooth_vector( a, b, alpha):

        dot = np.dot(a,b)
        dot = np.clip(dot,-1,1)

        angle = np.arccos(dot)

        if angle < 1e-6:
            return b

        sin_angle = np.sin(angle)

        return (
            np.sin((1-alpha)*angle)/sin_angle * a +
            np.sin(alpha*angle)/sin_angle * b
        ) 
    
    