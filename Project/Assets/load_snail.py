import pyvista as pv
import numpy as np
import os


SNAIL_SCALE = 0.04

SNAIL_MATERIALS = {

    "Material": {

        "color": (
            0.615131,
            0.005634,
            0.800000
        ),

        "specular": 0.5,

        # Blender Ns is 0-1000
        # PyVista specular_power is 0-128
        "specular_power": 128
    },


    "Material.001": {

        "color": (
            0.800000,
            0.251892,
            0.123644
        ),

        "specular": 0.5,

        "specular_power": 128
    },


    "Material.002": {

        "color": (
            0.008076,
            0.008076,
            0.008076
        ),

        "specular": 0.5,

        "specular_power": 128
    },


    "Material.003": {

        "color": (
            0.787985,
            0.776077,
            0.800000
        ),

        "specular": 0.5,

        "specular_power": 128
    }

}

def load_obj_materials(path):

    vertices = []

    faces = {}

    current_material = None


    with open(path, "r") as file:

        for line in file:

            parts = line.strip().split()

            if not parts:
                continue



            if parts[0] == "v":

                vertices.append(
                    [
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3])
                    ]
                )



            elif parts[0] == "usemtl":

                current_material = parts[1]

                if current_material not in faces:

                    faces[current_material] = []



            elif parts[0] == "f":

                face = []

                for item in parts[1:]:

                    index = int(
                        item.split("/")[0]
                    )

                    face.append(
                        index - 1
                    )


                faces[current_material].append(
                    face
                )



    vertices = np.array(
        vertices,
        dtype=float
    )



    meshes = {}



    for material, face_list in faces.items():

        cells = []


        for face in face_list:

            # triangulate polygons

            for i in range(
                1,
                len(face)-1
            ):

                cells.append(
                    [
                        3,
                        face[0],
                        face[i],
                        face[i+1]
                    ]
                )



        if not cells:
            continue



        cells = np.array(
            cells,
            dtype=np.int64
        )



        meshes[material] = pv.PolyData(
            vertices,
            cells
        )


    return meshes

def load_snail_asset(
    asset_directory
):


    obj_path = os.path.join(
        asset_directory,
        "snail_test.obj"
    )


    meshes = load_obj_materials(
        obj_path
    )


    snail = []


    for material_name, mesh in meshes.items():


        if material_name not in SNAIL_MATERIALS:

            print(
                "Missing snail material:",
                material_name
            )

            continue


        # -------------------------
        # Normalize imported asset
        # -------------------------

        mesh.scale(
            [
                SNAIL_SCALE,
                SNAIL_SCALE,
                SNAIL_SCALE
            ],
            inplace=True
        )


        material = SNAIL_MATERIALS[
            material_name
        ]


        snail.append(
            {
                "mesh": mesh,
                "material": material,
                "name": material_name
            }
        )
        mesh.translate(
            -np.array(mesh.center),
            inplace=True
        )


    return snail
