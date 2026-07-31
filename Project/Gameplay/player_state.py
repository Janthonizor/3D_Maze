import numpy as np


class PlayerState:

    def __init__(self):

        # Movement state
        self.sprinting = False
        self.sprint_locked = False

        # Resources
        self.stamina = 1000.0
        self.max_stamina = 1000.0

        # Tuning
        self.stamina_drain_rate = 300.0      # per second
        self.stamina_regen_rate = 50.0      # per second
        self.min_sprint_stamina = 1.0

    def can_sprint(self):
        return (
            not self.sprint_locked
            and self.stamina >= self.min_sprint_stamina
        )

    def update_stamina(self, dt):

        if self.sprinting and self.can_sprint():

            self.stamina -= (
                self.stamina_drain_rate
                * dt
            )

        else:

            self.stamina += (
                self.stamina_regen_rate
                * dt
            )

        self.stamina = np.clip(
            self.stamina,
            0.0,
            self.max_stamina
        )

        # Lock sprint when exhausted
        if self.stamina <= 10:
            self.sprinting = False
            self.sprint_locked = True

        # Unlock after recovering to 25%
        elif (
            self.sprint_locked
            and self.stamina >= 0.5 * self.max_stamina
        ):
            self.sprint_locked = False

    def get_speed_multiplier(self):

        if self.sprinting and self.can_sprint():
            return 3.0

        return 1.0