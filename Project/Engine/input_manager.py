class InputManager:

    def __init__(self):

        self.keys = set()

        self.mouse_delta = [0, 0]

        self.mouse_position = None

        self.input_enabled = False


    def enable(self):

        self.input_enabled = True

        # discard anything accumulated before game start
        self.mouse_delta = [0, 0]


    def disable(self):

        self.input_enabled = False

        self.mouse_delta = [0, 0]


    def press(self, key):

        if not self.input_enabled:
            return

        self.keys.add(key)


    def release(self, key):

        if not self.input_enabled:
            return

        self.keys.discard(key)


    def down(self, key):

        if not self.input_enabled:
            return False

        return key in self.keys


    def move_mouse(self, dx, dy):

        if not self.input_enabled:
            return

        self.mouse_delta[0] += dx
        self.mouse_delta[1] += dy


    def get_mouse_delta(self):

        if not self.input_enabled:
            return [0, 0]

        delta = self.mouse_delta.copy()

        self.mouse_delta = [0, 0]

        return delta
    