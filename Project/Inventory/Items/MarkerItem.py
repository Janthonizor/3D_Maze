from Inventory.item import Item
class MarkerItem(Item):

    def __init__(self):

        super().__init__(
            name="Marker",
            icon="Assets/Items/marker_icon.png",
            world_mesh="marker_sphere"
        )


    def use(self, player):

        node = player.current_node

        node.items.append(
            self
        )