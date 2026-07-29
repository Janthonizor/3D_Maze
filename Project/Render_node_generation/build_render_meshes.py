import os
from test_render_mesh import build_render_library

def save_render_library():

    # Build meshes
    node_meshes, node_edge_meshes = build_render_library()


    # ----------------------------
    # Paths
    # ----------------------------

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    data_dir = os.path.join(
        current_dir,
        "Data"
    )

    render_dir = os.path.join(
        data_dir,
        "render_meshes"
    )

    edge_dir = os.path.join(
        data_dir,
        "edge_meshes"
    )


    # ----------------------------
    # Save render meshes
    # ----------------------------

    print("Saving render meshes...")

    for key, mesh in node_meshes.items():

        filename = os.path.join(
            render_dir,
            f"rmesh{key}.vtp"
        )

        mesh.save(
            filename,
            binary=True
        )

        print(
            f"Saved {filename}"
        )


    # ----------------------------
    # Save edge meshes
    # ----------------------------

    print("Saving edge meshes...")

    for key, mesh in node_edge_meshes.items():

        filename = os.path.join(
            edge_dir,
            f"emesh{key}.vtp"
        )

        mesh.save(
            filename,
            binary=True
        )

        print(
            f"Saved {filename}"
        )


    print("==============================")
    print("Render library saved")
    print(f"Render meshes: {len(node_meshes)}")
    print(f"Edge meshes:   {len(node_edge_meshes)}")
    print("==============================")

save_render_library()