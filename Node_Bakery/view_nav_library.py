import pickle
import numpy as np
import pyvista as pv


# -----------------------------
# Load nav library
# -----------------------------

with open("nav_library.pkl", "rb") as f:
    nav_library = pickle.load(f)



# -----------------------------
# Convert NavData -> PolyData
# -----------------------------

def navdata_to_polydata(nav_data):

    points = []
    faces = []

    vertex_map = {}

    for tri in nav_data.triangles:

        ids = []

        for vid in tri.vertex_indices:

            if vid not in vertex_map:
                vertex_map[vid] = len(points)
                points.append(
                    nav_data.vertices[vid]
                )

            ids.append(vertex_map[vid])


        faces.extend([
            3,
            ids[0],
            ids[1],
            ids[2]
        ])

    return pv.PolyData(
        np.asarray(points),
        np.asarray(faces, dtype=np.int64)
    )



# -----------------------------
# Boundary loop -> PolyData
# boundary lists contain triangle objects
# -----------------------------

def boundary_loop_to_polydata(triangles, nav_data):

    if len(triangles) == 0:
        return None


    points = []
    faces = []

    vertex_map = {}


    for tri in triangles:

        ids = []

        for vid in tri.vertex_indices:

            if vid not in vertex_map:

                vertex_map[vid] = len(points)

                points.append(
                    nav_data.vertices[vid]
                )

            ids.append(
                vertex_map[vid]
            )


        faces.extend([
            3,
            ids[0],
            ids[1],
            ids[2]
        ])


    return pv.PolyData(
        np.asarray(points),
        np.asarray(faces, dtype=np.int64)
    )


# -----------------------------
# Boundary colors
# -----------------------------

BOUNDARY_COLORS = {
    0: "red",
    1: "blue",
    2: "green",
    3: "purple",
    4: "yellow",
    5: "black"
}



# -----------------------------
# Create grid
# -----------------------------

plotter = pv.Plotter(
    shape=(8,8),
    window_size=(1600,1600)
)



for i in range(64):

    row = i // 8
    col = i % 8

    plotter.subplot(
        row,
        col
    )


    if i >= len(nav_library):

        plotter.add_text(
            "EMPTY",
            font_size=10
        )

        continue


    nav_data = nav_library[i]


    # -------------------------
    # Main mesh
    # -------------------------

    mesh = navdata_to_polydata(
        nav_data
    )


    plotter.add_mesh(
        mesh,
        color="lightgrey",
        opacity=0.25,
        show_edges=False
    )


    # -------------------------
    # Boundary loops
    # -------------------------

    for boundary_key, triangles in nav_data.boundary_triangles.items():

        if len(triangles) == 0:
            continue


        boundary_mesh = boundary_loop_to_polydata(
            triangles,
            nav_data
        )


        if boundary_mesh is None:
            continue


        plotter.add_mesh(
            boundary_mesh,
            color=BOUNDARY_COLORS[boundary_key],
            opacity=1.0,
            show_edges=True
        )


    plotter.add_text(
        f"Node {i}",
        font_size=10
    )

    plotter.view_isometric()
    plotter.camera.zoom(0.8)



plotter.show()