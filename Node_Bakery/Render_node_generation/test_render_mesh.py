import numpy as np
import pyvista as pv

from Rendering.render_mesh import RenderMesh
from Assets.mesh_asset import MeshAsset


DIRECTIONS = [
    ( 1, 0, 0),
    (-1, 0, 0),
    ( 0, 1, 0),
    ( 0,-1, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]


CAP_ROTATIONS = {
    ( 1,0,0): (0,90,0),
    (-1,0,0): (0,-90,0),
    ( 0,1,0): (-90,0,0),
    ( 0,-1,0): (90,0,0),
    ( 0,0,1): (0,0,0),
    ( 0,0,-1): (0,180,0),
}


HALL_ROTATIONS = {
    ( 1,0,0): (0,0,0),
    (-1,0,0): (0,0,180),
    ( 0,1,0): (0,0,90),
    ( 0,-1,0): (0,0,-90),
    ( 0,0,1): (0,-90,0),
    ( 0,0,-1): (0,90,0),
}



# ----------------------------
# Load assets through your pipeline
# ----------------------------

texture = pv.read_texture(
    "Data/texture_2.png"
)


cap = RenderMesh(
    MeshAsset("Data/cap.obj"),
    texture
).polydata


hall = RenderMesh(
    MeshAsset("Data/hallway.obj"),
    texture
).polydata


node = RenderMesh(
    MeshAsset("Data/node.obj"),
    texture
).polydata



# ----------------------------
# Transform helper
# ----------------------------

def transform_mesh(
    mesh,
    rotation,
    offset
):

    mesh = mesh.copy(deep = True)

    mesh.rotate_x(
        rotation[0],
        inplace=True
    )

    mesh.rotate_y(
        rotation[1],
        inplace=True
    )

    mesh.rotate_z(
        rotation[2],
        inplace=True
    )

    mesh.translate(
        offset,
        inplace=True
    )

    return mesh



# ----------------------------
# Build one node combination
# ----------------------------

def build_node_key(key):

    meshes = []


    # center node

    meshes.append(
        node.copy(deep = True)
    )


    # six directions

    for i, direction in enumerate(DIRECTIONS):

        offset = np.array(direction) * 1.5


        if key & (1 << i):

            mesh = transform_mesh(
                hall,
                HALL_ROTATIONS[direction],
                offset
            )

        else:

            mesh = transform_mesh(
                cap,
                CAP_ROTATIONS[direction],
                offset
            )


        meshes.append(mesh)



    # merge without welding vertices
    merged = meshes[0]

    for mesh in meshes[1:]:

        merged = merged.merge(
            mesh,
            merge_points=False
        )


    merged.active_texture_coordinates = (
        merged.point_data["Texture Coordinates"]
    )


    return merged

def build_render_library():

    node_meshes = {}
    node_edge_meshes = {}

    for key in range(64):

        print(
            f"Building key {key}"
        )

        mesh = build_node_key(key)

        node_meshes[key] = mesh


        # Build edge mesh once
        edges = mesh.extract_all_edges()

        node_edge_meshes[key] = edges


    print("==============================")
    print("Render library build complete")
    print("Meshes:", len(node_meshes))
    print("Edges:", len(node_edge_meshes))
    print("==============================")


    return node_meshes, node_edge_meshes

node_meshes, node_edge_meshes = build_render_library()

# ----------------------------
# Select node key
# ----------------------------

key = 42   # change this


mesh = node_meshes[key]
edges = node_edge_meshes[key]


# ----------------------------
# Create synchronized plot
# ----------------------------

plotter = pv.Plotter(
    shape=(1,2),
    window_size=(1600,800)
)


# ----------------------------
# Mesh view
# ----------------------------

plotter.subplot(0,0)

plotter.add_mesh(
    mesh,
    texture=texture,
    lighting=False
)

plotter.add_text(
    f"Node {key} Surface",
    font_size=14
)


plotter.view_isometric()


# store camera
camera_position = plotter.camera_position


# ----------------------------
# Edge view
# ----------------------------

plotter.subplot(0,1)

plotter.add_mesh(
    edges,
    color="white",
    line_width=2
)

plotter.add_text(
    f"Node {key} Edges",
    font_size=14
)


# apply identical camera
plotter.camera_position = camera_position


# ----------------------------
# Sync cameras
# ----------------------------

plotter.link_views()


# optional nicer background
plotter.set_background(
    "black"
)


plotter.show()