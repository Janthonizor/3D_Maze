from asset_holder import AssetHolder
from node_builder import NodeBuilder
from nav_mesh import NavMesh
import numpy as np
import pyvista as pv




assets = AssetHolder(
    "assets"
)


builder = NodeBuilder(
    assets
)

i = 9

vertices, triangles = builder.build_node(
    i
)
print(i)
mesh = NavMesh(
    i,
    vertices,
    triangles
)

import pyvista as pv
import numpy as np


def triangles_to_polydata(mesh, triangles):

    vertices = []
    faces = []
    vertex_map = {}

    for tri in triangles:

        face = []

        for vertex_id in tri.vertex_indices:

            if vertex_id not in vertex_map:
                vertex_map[vertex_id] = len(vertices)
                vertices.append(
                    mesh.vertices[vertex_id]
                )

            face.append(
                vertex_map[vertex_id]
            )

        faces.append(
            [3] + face
        )

    if len(vertices) == 0:
        return None

    return pv.PolyData(
        np.array(vertices),
        np.array(faces)
    )


boundary = []
interior = []

for tri in mesh.triangles:

    if len(tri.neighbor_ids) == 2:
        boundary.append(tri)

    else:
        interior.append(tri)


boundary_mesh = triangles_to_polydata(
    mesh,
    boundary
)

interior_mesh = triangles_to_polydata(
    mesh,
    interior
)


plotter = pv.Plotter(
    shape=(1,2)
)


# left plot
plotter.subplot(0,0)

if boundary_mesh is not None:
    plotter.add_mesh(
        boundary_mesh,
        color="red",
        show_edges=True
    )

plotter.add_title(
    f"2 neighbors ({len(boundary)})"
)


# right plot
plotter.subplot(0,1)

if interior_mesh is not None:
    plotter.add_mesh(
        interior_mesh,
        color="white",
        show_edges=True
    )

plotter.add_title(
    f"Other ({len(interior)})"
)

plotter.link_views()

plotter.show()