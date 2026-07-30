import numpy as np

from mesh_instance import MeshInstance


DIRECTIONS = [

    ( 1, 0, 0),
    (-1, 0, 0),

    ( 0, 1, 0),
    ( 0,-1, 0),

    ( 0, 0, 1),
    ( 0, 0,-1)

]


class MappingCreator:


    def __init__(
        self,
        assets,
        tolerance=1e-4
    ):

        self.assets = assets

        self.tolerance = tolerance

        self.cap_mappings = {}
        self.hallway_mappings = {}



    def create_node(
        self
    ):

        return MeshInstance(
            self.assets.node_asset
        )



    def create_cap(
        self,
        direction
    ):

        return MeshInstance(

            self.assets.cap_asset,

            position=np.array(direction)*1.5,

            rotation=self.assets.cap_rotations[direction],

            asset_type="cap"

        )



    def create_hallway(
        self,
        direction
    ):

        return MeshInstance(

            self.assets.hallway_asset,

            position=np.array(direction)*1.5,

            rotation=self.assets.hallway_rotations[direction],

            asset_type="hallway"

        )



    def find_matching_loop(
        self,
        base_instance,
        attachment_instance
    ):

        candidates = []


        for base_id, base_loop in enumerate(
            base_instance.boundary_loops
        ):


            for attach_id, attach_loop in enumerate(
                attachment_instance.boundary_loops
            ):


                normal_dot = np.dot(

                    base_loop["normal"],

                    attach_loop["normal"]

                )


                # must face each other

                if normal_dot > -0.95:

                    continue



                distance = np.linalg.norm(

                    base_loop["center"]

                    -

                    attach_loop["center"]

                )


                candidates.append(

                    (
                        distance,
                        base_id,
                        attach_id
                    )

                )


        if len(candidates) == 0:

            raise Exception(
                "No matching boundary loops found"
            )


        candidates.sort(
            key=lambda x:x[0]
        )


        distance, base_id, attach_id = candidates[0]


        if distance > 1.0:

            raise Exception(

                f"Closest loop too far away: {distance}"

            )


        return (
            base_id,
            attach_id
        )



    def create_mapping(
        self,
        base_instance,
        attachment_instance
    ):


        base_loop_id, attach_loop_id = (

            self.find_matching_loop(

                base_instance,

                attachment_instance

            )

        )


        base_loop = (

            base_instance.boundary_loops[base_loop_id]

        )


        attach_loop = (

            attachment_instance.boundary_loops[attach_loop_id]

        )



        mapping = {}



        for base_id, base_point in zip(

            base_loop["ids"],

            base_loop["vertices"]

        ):


            best = None

            best_distance = np.inf


            for attach_id, attach_point in zip(

                attach_loop["ids"],

                attach_loop["vertices"]

            ):


                distance = np.linalg.norm(

                    base_point

                    -

                    attach_point

                )


                if distance < best_distance:

                    best_distance = distance

                    best = attach_id



            if best_distance > self.tolerance:

                raise Exception(

                    f"Vertex mismatch distance {best_distance}"

                )


            mapping[base_id] = best



        return mapping



    def generate_caps(self):

        node = self.create_node()


        for direction in DIRECTIONS:


            cap = self.create_cap(
                direction
            )


            self.cap_mappings[direction] = (

                self.create_mapping(

                    node,

                    cap

                )

            )



    def generate_hallways(self):

        node = self.create_node()


        for direction in DIRECTIONS:


            hallway = self.create_hallway(
                direction
            )


            self.hallway_mappings[direction] = (

                self.create_mapping(

                    node,

                    hallway

                )

            )



    def generate_all(self):


        self.generate_caps()

        self.generate_hallways()
        print(self.cap_mappings)
        print(self.hallway_mappings)

        return {

            "caps":
                self.cap_mappings,

            "hallways":
                self.hallway_mappings

        }