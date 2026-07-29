import numpy as np

class MazeMap:

    def __init__(
        self,
        N,
        grid_spacing
    ):

        self.N = N
        self.grid_spacing = grid_spacing

        self.nodes = {}

    def add_node(self, node):

        self.nodes[node.id] = node

    def get_node(self, node_id):

        return self.nodes[node_id]

    def get_stream_tree(
        self,
        start_id,
        depth
    ):

        layers = []

        node_layers = {}

        visited = set()

        frontier = [start_id]


        for current_depth in range(depth + 1):

            layer = []

            next_frontier = []


            for node_id in frontier:

                if node_id in visited:
                    continue


                visited.add(node_id)

                layer.append(node_id)

                node_layers[node_id] = current_depth


                node = self.get_node(node_id)


                for neighbor in node.neighbors:

                    if neighbor not in visited:
                        next_frontier.append(
                            neighbor
                        )


            layers.append(layer)

            frontier = next_frontier


        return layers, node_layers
    
    def get_node_direction(
            self,
            node_a_id,
            node_b_id
        ):

            node_a = self.get_node(
                node_a_id
            )

            node_b = self.get_node(
                node_b_id
            )

            direction = (
                node_a.position -
                node_b.position
            )

            return np.sign(
                direction
            ).astype(int)
    