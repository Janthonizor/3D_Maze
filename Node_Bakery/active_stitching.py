import pickle
import pyvista as pv
import numpy as np
from collections import deque
from active_nav_mesh import ActiveNavMesh
import time


# -----------------------------------
# Load baked library
# -----------------------------------

t0 = time.perf_counter()

with open("nav_library.pkl", "rb") as f:
    nav_library = pickle.load(f)

print(
    "Load pickle:",
    time.perf_counter() - t0,
    "seconds"
)


# -----------------------------------
# Load two copies of same node
# -----------------------------------

mesh_id = 62

t0 = time.perf_counter()

mesh0 = ActiveNavMesh(
    nav_library[62],
    0,
    np.array([0,0,0], dtype=float)
)

mesh1 = ActiveNavMesh(
    nav_library[62],
    1,
    np.array([0,0,-8], dtype=float)
)

print(
    "ActiveNavMesh creation:",
    time.perf_counter() - t0,
    "seconds"
)


# -----------------------------------
# Stitch
# -----------------------------------

def stitch_boundary_loops(meshA, meshB, axisAB):

    axis_dict = {
        "x":(1,0),
        "-x":(0,1),
        "y":(3,2),
        "-y":(2,3),
        "z":(5,4),
        "-z":(4,5)
    }

    loopA, loopB = axis_dict[axisAB]

    A = meshA.boundary_triangles[loopA]
    B = meshB.boundary_triangles[loopB]

    assert len(A) == len(B)


    for triA, triB in zip(A,B):

        triA.neighbors.append(triB)
        triB.neighbors.append(triA)


# -----------------------------------
# BFS
# -----------------------------------

def bfs_triangles(start_triangle, depth=None):

    visited = set()
    result = []

    queue = deque([
        (start_triangle,0)
    ])

    visited.add(
        start_triangle.global_id
    )


    while queue:

        tri,d = queue.popleft()

        result.append(tri)


        if depth is not None and d >= depth:
            continue


        for nbr in tri.neighbors:

            key = nbr.global_id

            if key in visited:
                continue

            visited.add(key)

            queue.append(
                (nbr,d+1)
            )


    return result


# -----------------------------------
# Plot helper
# -----------------------------------

def triangles_to_polydata(mesh, triangles):

    t0 = time.perf_counter()

    points = []
    faces = []

    vertex_map = {}


    for tri in triangles:

        ids=[]

        for vid in tri.vertex_indices:

            if vid not in vertex_map:

                vertex_map[vid] = len(points)
                points.append(
                    mesh.vertices[vid]
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


    poly = pv.PolyData(
        np.asarray(points),
        np.asarray(faces,dtype=np.int64)
    )

    print(
        "triangles_to_polydata:",
        len(triangles),
        "triangles ->",
        time.perf_counter() - t0,
        "seconds"
    )

    return poly


# -----------------------------------
# Test stitch + BFS
# -----------------------------------

t0 = time.perf_counter()

stitch_boundary_loops(
    mesh0,
    mesh1,
    "-z"
)

print(
    "Stitch:",
    time.perf_counter() - t0,
    "seconds"
)


t0 = time.perf_counter()

offset = np.array([0,0,-8])

bfs = bfs_triangles(
    mesh0.boundary_triangles[4][1],
    depth=6
)

print(
    "BFS:",
    time.perf_counter() - t0,
    "seconds",
    "visited:",
    len(bfs)
)


t0 = time.perf_counter()

bfs0 = [
    tri for tri in bfs
    if tri.mesh_id == 0
]

bfs1 = [
    tri for tri in bfs
    if tri.mesh_id == 1
]

print(
    "BFS split:",
    time.perf_counter() - t0,
    "seconds",
    "mesh0:",
    len(bfs0),
    "mesh1:",
    len(bfs1)
)


# -----------------------------------
# Plot
# -----------------------------------

t0 = time.perf_counter()

plotter = pv.Plotter()

mesh0_poly = triangles_to_polydata(
    mesh0,
    mesh0.triangles
)

plotter.add_mesh(
    mesh0_poly,
    color="grey",
    opacity=0.2,
    show_edges=True
)


mesh1_poly = triangles_to_polydata(
    mesh1,
    mesh1.triangles
)

actor = plotter.add_mesh(
    mesh1_poly,
    color="blue",
    opacity=0.2,
    show_edges=True
)


if len(bfs0):

    bfs0_poly = triangles_to_polydata(
        mesh0,
        bfs0
    )

    plotter.add_mesh(
        bfs0_poly,
        color="red",
        show_edges=True
    )


if len(bfs1):

    bfs1_poly = triangles_to_polydata(
        mesh1,
        bfs1
    )

    bfs_actor = plotter.add_mesh(
        bfs1_poly,
        color="red",
        show_edges=True
    )


plotter.add_axes()

print(
    "Plot construction:",
    time.perf_counter() - t0,
    "seconds"
)

plotter.show()