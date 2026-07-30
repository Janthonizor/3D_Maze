
    def solve_collision(
        self,
        triangle_query,
        player_tri,
        dt
    ):


        rev_cam_direction = (
            self.position - self.player_position
        )

        distance = np.linalg.norm(
            rev_cam_direction
        )

        rev_cam_direction /= distance

        center_point = (
            self.player_position +
            rev_cam_direction * self.max_radius
        )


        offset = 0.25


        ray_points = [
            center_point,

            center_point + self.up * offset,

            center_point - self.up * offset,

            center_point - self.right * offset,

            center_point + self.right * offset

        ]



        # -------------------------
        # Ray trace
        # -------------------------
        hit_distances  = []

        for point in ray_points:

            ray_direction = (
                point-self.player_position
            )

            ray_direction /= np.linalg.norm(ray_direction)

            hit = raycast_surface(
                triangle_query,
                player_tri,
                self.player_position,
                ray_direction,
                15,
                self.max_radius,
                self.radius_padding*2,
                self.position
            )

            if hit is None:
                continue

            hit_distances.append(hit[2])

        if hit_distances:
            min_hit_distance = min(hit_distances)

        else:
            min_hit_distance = self.max_radius

        self.update_radius_from_collision(
            min_hit_distance
        )

        self.update_radius(
            dt
        )

        self.update_position_from_radius()


    def update_radius_from_collision(
        self,
        collision_distance
    ):

        # apply safety padding
        safe_radius = (
            collision_distance -
            self.radius_padding
        )

        self.target_radius = np.clip(
            safe_radius,
            self.min_radius,
            self.max_radius
        )


    def update_position_from_radius(self):

        up = self.player_up / np.linalg.norm(self.player_up)

        # vector from player to camera
        offset = self.position - self.player_position

        # remove vertical component
        vertical = np.dot(offset, up) * up

        horizontal = offset - vertical

        horizontal_length = np.linalg.norm(horizontal)

        if horizontal_length < 1e-8:
            return

        # preserve orbit direction but force radius
        horizontal_direction = horizontal / horizontal_length

        self.position = (
            self.player_position
            +
            horizontal_direction * self.radius
            +
            up * self.height_offset
        )



    def update_radius(
        self,
        dt
    ):

        if abs(
            self.radius -
            self.target_radius
        ) < 1e-4:

            return


        alpha = 1.0 - np.exp(
            -self.radius_smooth_speed * dt
        )


        self.radius = (
            (1-alpha)
            *
            self.radius
            +
            alpha
            *
            self.target_radius
        )

