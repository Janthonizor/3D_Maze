class InputManager:

    def __init__(self):

        self.keys = set()

        self.mouse_delta = [0, 0]

        self.mouse_position = None


    def press(self, key):
        self.keys.add(key)


    def release(self, key):
        self.keys.discard(key)


    def down(self, key):
        return key in self.keys


    def move_mouse(self, dx, dy):

        self.mouse_delta[0] += dx
        self.mouse_delta[1] += dy


    def get_mouse_delta(self):

        delta = self.mouse_delta.copy()

        self.mouse_delta = [0, 0]

        return delta