import numpy as np
import pickle

from mesh_instance import MeshInstance


DIRECTIONS = [

    ( 1, 0, 0),
    (-1, 0, 0),

    ( 0, 1, 0),
    ( 0,-1, 0),

    ( 0, 0, 1),
    ( 0, 0,-1)

]


class NodeBuilder:


    def __init__(
        self,
        assets,
        weld_file="weld_mappings.pkl"
    ):

        self.assets = assets

        with open(
            weld_file,
            "rb"
        ) as f:

            self.welds = pickle.load(f)



    def decode_key(
        self,
        key
    ):

        return [

            bool(
                key & (1 << i)
            )

            for i in range(6)

        ]



    def build_instances(
        self,
        key
    ):

        open_dirs = self.decode_key(key)

        instances = []


        node = MeshInstance(
            self.assets.node_asset,
            asset_type="node"
        )

        instances.append(
            node
        )


        for i, direction in enumerate(DIRECTIONS):

            if open_dirs[i]:

                instances.append(

                    MeshInstance(

                        self.assets.hallway_asset,

                        position=np.array(direction)*1.5,

                        rotation=self.assets.hallway_rotations[direction],

                        asset_type="hallway",

                    )

                )

            else:

                instances.append(

                    MeshInstance(

                        self.assets.cap_asset,

                        position=np.array(direction)*1.5,

                        rotation=self.assets.cap_rotations[direction],

                        asset_type="cap",

                    )

                )


        return instances



    def weld_instances(
        self,
        instances,
        key
    ):

        node = instances[0]


        vertices = list(
            node.vertices
        )


        triangles = []


        # node triangles already valid

        for tri in node.triangles:

            triangles.append(
                tri.vertex_indices.copy()
            )



        open_dirs = self.decode_key(key)


        instance_index = 1


        for i, direction in enumerate(DIRECTIONS):


            attachment = instances[
                instance_index
            ]

            instance_index += 1



            if attachment.asset_type == "hallway":

                weld_data = self.welds["hallways"][direction]

            else:

                weld_data = self.welds["caps"][direction]



            # offset before adding attachment vertices

            vertex_offset = len(vertices)


            vertices.extend(
                attachment.vertices
            )



            # map attachment vertex ids back to node ids

            vertex_map = {

                attach_id + vertex_offset:
                node_id

                for node_id, attach_id
                in weld_data.items()

            }



            for tri in attachment.triangles:

                new_tri = []


                for index in tri.vertex_indices:


                    world_index = (
                        index + vertex_offset
                    )


                    if world_index in vertex_map:

                        new_tri.append(
                            vertex_map[world_index]
                        )

                    else:

                        new_tri.append(
                            world_index
                        )


                triangles.append(
                    new_tri
                )


        return (

            np.array(
                vertices,
                dtype=float
            ),

            triangles

        )



    def build_node(
        self,
        key
    ):

        instances = self.build_instances(
            key
        )


        return self.weld_instances(
            instances,
            key
        )