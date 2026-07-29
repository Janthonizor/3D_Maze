import numpy as np
import pyvista as pv


def load_obj_with_uv_triangles(filename):

    vertices = []
    uvs = []
    normals = []

    faces = []


    # -------------------------
    # Parse OBJ
    # -------------------------

    with open(filename, "r") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue


            parts = line.split()

            if parts[0] == "v":

                vertices.append(
                    [
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3])
                    ]
                )


            elif parts[0] == "vt":

                uvs.append(
                    [
                        float(parts[1]),
                        float(parts[2])
                    ]
                )


            elif parts[0] == "vn":

                normals.append(
                    [
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3])
                    ]
                )


            elif parts[0] == "f":

                face = []

                for vert in parts[1:]:

                    indices = vert.split("/")


                    v_id = int(indices[0]) - 1


                    uv_id = None
                    normal_id = None


                    if len(indices) > 1 and indices[1]:

                        uv_id = int(indices[1]) - 1


                    if len(indices) > 2 and indices[2]:

                        normal_id = int(indices[2]) - 1


                    face.append(
                        (
                            v_id,
                            uv_id,
                            normal_id
                        )
                    )


                faces.append(face)



    # -------------------------
    # Explode vertices
    # -------------------------

    new_points = []
    new_uvs = []
    new_normals = []

    new_faces = []

    vertex_map = {}


    def get_vertex_index(key):

        if key in vertex_map:

            return vertex_map[key]


        v_id, uv_id, n_id = key


        index = len(new_points)


        vertex_map[key] = index


        new_points.append(
            vertices[v_id]
        )


        if uv_id is not None:

            new_uvs.append(
                uvs[uv_id]
            )

        else:

            new_uvs.append(
                [0.0,0.0]
            )


        if n_id is not None:

            new_normals.append(
                normals[n_id]
            )

        else:

            new_normals.append(
                [0.0,0.0,1.0]
            )


        return index



    # -------------------------
    # Triangulate faces
    # -------------------------

    for face in faces:


        # fan triangulation
        for i in range(1, len(face)-1):

            tri = [
                face[0],
                face[i],
                face[i+1]
            ]


            ids = []

            for key in tri:

                ids.append(
                    get_vertex_index(key)
                )


            new_faces.append(
                [
                    3,
                    ids[0],
                    ids[1],
                    ids[2]
                ]
            )



    # -------------------------
    # Create PolyData
    # -------------------------

    points = np.array(
        new_points
    )


    faces = np.array(
        new_faces,
        dtype=np.int64
    ).flatten()


    mesh = pv.PolyData(
        points,
        faces
    )


    mesh.point_data["Texture Coordinates"] = np.array(
        new_uvs
    )


    mesh.point_data["Normals"] = np.array(
        new_normals
    )


    return mesh