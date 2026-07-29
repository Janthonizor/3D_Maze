import numpy as np

class Player:

    def __init__(
        self,
        start_triangle_id,
        start_mesh_id,
        start_bary
    ):

        self.current_triangle_key = (start_mesh_id, start_triangle_id)
        self.active_meshes = None
        self.triangle_cache = []
        self.depth = 10
        self.move_speed = 0.7
        self.turn_speed = 80
        
    

        # Surface state
        self.barycentric = np.asarray(start_bary, dtype = float)
        self.position = None

        
        # Local coordinate frame
        self.up = None
        self.previous_up = None

        
        self.forward = None
        self.previous_forward = None

        self.velocity = np.zeros(3, dtype = np.float32)
        self.acceleration = np.zeros(3, dtype = np.float32)

        #physics interpolation
        
        self.previous_position_frame = None
        self.current_position_frame = None

        self.previous_up_frame = None
        self.current_up_frame = None

        self.previous_forward_frame = None
        self.current_forward_frame = None
        self.debug = True

    def debug_print(self, *args):
        if self.debug:
            print(*args)


    def debug_player_state(self, header="PLAYER STATE"):
        if not self.debug:
            return

        print(f"\n===== {header} =====")
        print(f"Triangle Key : {self.current_triangle_key}")
        print(f"Position     : {self.position}")
        print(f"Barycentric  : {self.barycentric}")
        print(f"Forward      : {self.forward}")
        print(f"Up           : {self.up}") 

    # receive active surface data from controller
    def set_active_meshes(self, active_meshes):

        self.active_meshes = active_meshes

        self.build_triangle_cache()

    def update_position(self):

        mesh_id, tri_id = self.current_triangle_key

        active_mesh = self.active_meshes[mesh_id]

        self.position = (
            self.barycentric @
            active_mesh.vertices[
                active_mesh.tri_vertex_indices[tri_id]
            ]
        )
        self.current_position_frame = self.position.copy()
        self.previous_position_frame = self.position.copy()

    def create_up(self):

        mesh_id, tri_id = self.current_triangle_key

        active_mesh = self.active_meshes[mesh_id]

        self.up = (
            self.barycentric @
            active_mesh.vertex_normals[
                active_mesh.tri_vertex_indices[tri_id]
            ]
        )

        self.up /= np.linalg.norm(
            self.up
        )

        self.previous_up = self.up.copy()
        self.current_up_frame = self.up.copy()
        self.previous_up_frame = self.up.copy()

    def create_forward(self):

        mesh_id, tri_id = self.current_triangle_key

        active_mesh = self.active_meshes[mesh_id]

        v0, v1, v2 = active_mesh.vertices[
            active_mesh.tri_vertex_indices[tri_id]
        ]

        # pick a triangle edge as initial tangent direction
        forward = v1 - v0

        # project onto triangle plane
        forward -= (
            np.dot(forward, self.up)
            *
            self.up
        )

        length = np.linalg.norm(forward)

        if length < 1e-8:

            forward = v2 - v0

            forward -= (
                np.dot(forward, self.up)
                *
                self.up
            )

            length = np.linalg.norm(forward)

        forward /= length

        self.forward = forward
        self.previous_forward = forward.copy()
        self.current_forward_frame = forward.copy()
        self.previous_forward_frame = forward.copy()
    
    def create_frame(self):

        self.update_position()

        self.create_up()
        
        self.create_forward()

    def build_triangle_cache(self):
        if self.active_meshes is None:

            self.debug_print(
                "\nERROR: build_triangle_cache() called with active_meshes=None"
            )

        visited = set()

        current_layer = [
            self.current_triangle_key
        ]

        self.triangle_cache = []

        for _ in range(self.depth + 1):

            next_layer = []
            layer = []

            for triangle_key in current_layer:

                if triangle_key in visited:
                    continue

                visited.add(triangle_key)

                layer.append(
                    triangle_key
                )

                mesh_id, tri_id = triangle_key

                connections = (
                    self.active_meshes[mesh_id]
                    .tri_connections[tri_id]
                )

                for connection in connections:

                    if connection[0] is None:
                        continue

                    neighbor_key = (
                        connection[0],
                        connection[1]
                    )

                    if neighbor_key not in visited:
                        next_layer.append(
                            neighbor_key
                        )

            self.triangle_cache.append(
                layer
            )

            current_layer = next_layer

    def update_up(self, transition=False):

        mesh_id, tri_id = self.current_triangle_key

        active_mesh = self.active_meshes[mesh_id]

        normals = active_mesh.vertex_normals[
            active_mesh.tri_vertex_indices[tri_id]
        ]

        target = self.barycentric @ normals

        target /= np.linalg.norm(target)

        if transition:
            alpha = 0.01
        else:
            alpha = 0.15

        self.up = self.smooth_vector(
            self.previous_up,
            target,
            alpha
        )

        self.up /= np.linalg.norm(self.up)

        self.previous_up = self.up.copy()

    def update_forward(self):

            target = (
                self.forward -
                np.dot(self.forward, self.up)
                * self.up
            )

            length = np.linalg.norm(target)

            if length < 1e-6:

                self.debug_print(
                    "\nERROR: update_forward() produced nearly zero tangent.",
                    f"\nForward : {self.forward}",
                    f"\nUp      : {self.up}",
                    f"\nTarget  : {target}"
                )

                return

            target /= length


            if self.previous_forward is None:
                self.forward = target

            else:

                alpha = 0.6

                self.forward = self.smooth_vector(
                    self.previous_forward,
                    target,
                    alpha
                )
                            # re-orthogonalize
                self.forward -= (
                    np.dot(self.forward,self.up)
                    * self.up
                )

                self.forward /= np.linalg.norm(
                    self.forward
                )


            self.previous_forward = self.forward.copy()

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

    def project_vector_to_triangle(
        self,
        vector,
        triangle_key
    ):

        mesh_id, tri_id = triangle_key

        mesh = self.active_meshes[mesh_id]

        normal = mesh.tri_normals[tri_id]


        projected = (
            vector -
            np.dot(vector, normal)
            * normal
        )


        length = np.linalg.norm(projected)

        if length < 1e-8:
            self.debug_print(
                "\nERROR: project_vector_to_triangle() returned None",
                f"\nTriangle : {triangle_key}",
                f"\nVector   : {vector}",
                f"\nNormal   : {normal}",
                f"\nProjected: {projected}",
                f"\nLength   : {length}"
            )
            self.debug_player_state()
            return None


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

        end_bary = self.world_to_barycentric(
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
                    -self.barycentric[i] /
                    bary_delta[i]
                )

                fraction = min(
                    fraction,
                    exit_fraction
                )


        return distance * fraction

    def step_current_triangle(self, distance):

        triangle_key = self.current_triangle_key


        projected_forward = self.project_vector_to_triangle(
            self.forward,
            triangle_key
        )
        # calculate intended movement vector
        movement = projected_forward * distance

        start = self.position
        end = start + movement


        # check endpoint in current triangle
        end_bary = self.world_to_barycentric(
            end,
            triangle_key
        )

        inside = (
            np.all(end_bary >= -1e-3)
            and
            np.all(end_bary <= 1.001)
        )


        if inside:

            self.position = end
            self.barycentric = end_bary

            return distance, False


        # otherwise we crossed a boundary
        # find maximum valid distance in this triangle

        valid_distance = self.find_exit_distance(
            distance,
            projected_forward,
            triangle_key
        )


        self.position = (
            start +
            projected_forward * valid_distance
        )

        self.barycentric = self.world_to_barycentric(
            self.position,
            triangle_key
        )


        return valid_distance, True

    def find_next_triangle_at_exit_point(
        self,
    ):


        candidates = 0
        tested = 0

        for layer_id, layer in enumerate(self.triangle_cache):


            for triangle_key in layer:

                tested += 1

                bary = self.world_to_barycentric(
                    self.position,
                    triangle_key
                )

                inside = (
                    np.all(bary >= -1e-4)
                    and
                    np.all(bary <= 1.0001)
                )


                if inside:

                    candidates += 1

                    if triangle_key != self.current_triangle_key:
                        
                        
                        return (
                            triangle_key,
                            bary
                        )
                    
        self.debug_print(
            "\nERROR: No triangle found at exit point.",
            f"\nTriangles Tested : {tested}",
            f"\nCandidates Found : {candidates}",
            f"\nCurrent Triangle : {self.current_triangle_key}",
            f"\nPosition         : {self.position}",
            f"\nBarycentric      : {self.barycentric}"
        )

        return None
    
    def move_forward(self, velocity, dt):
        remaining_distance = velocity * dt
        counter = 0
        while abs(remaining_distance) > 0:
            counter+=1
            distance_travelled, crossed = self.step_current_triangle(
                remaining_distance
            )

            #self.position += self.forward * distance_travelled

            remaining_distance -= distance_travelled

            if not crossed:
                break

            result = self.find_next_triangle_at_exit_point()
            
            if result is None:

                self.debug_print(
                    "\n========== MOVEMENT REJECTED ==========",
                    f"\nRemaining Distance : {remaining_distance}",
                    f"\nCounter            : {counter}",
                    f"\nCurrent Triangle   : {self.current_triangle_key}",
                    f"\nPosition           : {self.position}",
                    f"\nBarycentric        : {self.barycentric}",
                    f"\nForward            : {self.forward}",
                    f"\nUp                 : {self.up}",
                    f"\nCache Layers       : {len(self.triangle_cache)}",
                    f"\nCache Size         : {sum(len(layer) for layer in self.triangle_cache)}"
                )

                self.debug_player_state("MOVEMENT FAILURE")
                break

            self.current_triangle_key, self.barycentric = result
            self.position = self.barycentric_to_world(
                self.barycentric,
                self.current_triangle_key
            )
            self.build_triangle_cache()

            if counter > 100:

                self.debug_print(
                    "\nERROR: move_forward() exceeded 100 iterations.",
                    f"\nRemaining Distance : {remaining_distance}",
                    f"\nCurrent Triangle   : {self.current_triangle_key}"
                )

                break

        
        self.update_up()
        self.update_forward()
    
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

    def barycentric_to_world(self, bary, triangle_key):

        mesh_id, tri_id = triangle_key

        mesh = self.active_meshes[mesh_id]

        tri_vertices = mesh.tri_vertex_indices[tri_id]

        return (
            bary[0] * mesh.vertices[tri_vertices[0]]
            +
            bary[1] * mesh.vertices[tri_vertices[1]]
            +
            bary[2] * mesh.vertices[tri_vertices[2]]
        )
        
    def world_to_barycentric(
        self,
        point,
        triangle_key
    ):

        mesh_id, tri_id = triangle_key

        active_mesh = self.active_meshes[mesh_id]

        v0, v1, v2 = active_mesh.vertices[
            active_mesh.tri_vertex_indices[tri_id]
        ]

        v0v1 = v1 - v0
        v0v2 = v2 - v0
        v0p = point - v0

        d00 = np.dot(v0v1, v0v1)
        d01 = np.dot(v0v1, v0v2)
        d11 = np.dot(v0v2, v0v2)
        d20 = np.dot(v0p, v0v1)
        d21 = np.dot(v0p, v0v2)

        denom = d00*d11 - d01*d01

        if abs(denom) < 1e-8:
            self.debug_print(
                "\nERROR: Degenerate triangle in world_to_barycentric()",
                f"\nTriangle : {triangle_key}",
                f"\nv0 : {v0}",
                f"\nv1 : {v1}",
                f"\nv2 : {v2}",
                f"\nDenominator : {denom}"
            )
            return np.array([-1, -1, -1])

        v = (d11*d20 - d01*d21) / denom
        w = (d00*d21 - d01*d20) / denom
        u = 1 - v - w

        return np.array([u, v, w])
 
    def get_frame(self):
        return self.position, self.up, self.forward
    
    def get_node_id(self):
        return self.current_triangle_key[0]

    def save_previous_render_state(self):

        if self.current_position_frame is not None:
            self.previous_position_frame = (
                self.current_position_frame.copy()
            )

        if self.current_up_frame is not None:
            self.previous_up_frame = (
                self.current_up_frame.copy()
            )

        if self.current_forward_frame is not None:
            self.previous_forward_frame = (
                self.current_forward_frame.copy()
            )
            
    def update_render_state(self):

        if self.position is not None:
            self.current_position_frame = (
                self.position.copy()
            )

        if self.up is not None:
            self.current_up_frame = (
                self.up.copy()
            )

        if self.forward is not None:
            self.current_forward_frame = (
                self.forward.copy()
            )

    def get_interpolated_frame(self, alpha):

        # fallback if interpolation has not initialized yet
        if (
            self.previous_position_frame is None
            or self.current_position_frame is None
        ):
            return {
                "position": self.position,
                "up": self.up,
                "forward": self.forward
            }


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
    