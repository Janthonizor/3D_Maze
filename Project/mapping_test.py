import time
import numpy as np
import pyvista as pv
import vtk

from vtkmodules.util import numpy_support

from Assets.asset_library import AssetLibrary
from Maze_Generation.level import Level



def convert_colors_to_vtk(colors):

    colors = np.asarray(
        colors,
        dtype=float
    )

    colors = (
        colors * 255
    ).clip(
        0,
        255
    ).astype(
        np.uint8
    )

    vtk_colors = numpy_support.numpy_to_vtk(
        colors,
        deep=True,
        array_type=vtk.VTK_UNSIGNED_CHAR
    )

    vtk_colors.SetNumberOfComponents(
        3
    )

    vtk_colors.SetName(
        "Scalars"
    )

    return vtk_colors



# -------------------------
# Load assets
# -------------------------

assets = AssetLibrary()

assets.load_all()


level = Level(
    5,
    8,
    100,
    12345
)


build_node_color_maps(
    level.maze_map,
    assets
)


node = level.maze_map.nodes[0]


mesh = assets.render_meshes[
    node.type_id
]


texture = assets.texture
print(texture.GetClassName())




colors = node.colors


vtk_colors = convert_colors_to_vtk(
    colors
)



# -------------------------
# PyVista add_mesh
# -------------------------

def benchmark_add_mesh(
    plotter,
    mesh,
    texture,
    colors
):

    start = time.perf_counter()


    actor = plotter.add_mesh(
        mesh,
        texture=texture,
        scalars=colors,
        rgb=True,
        lighting=False
    )


    elapsed = (
        time.perf_counter()
        -
        start
    )


    return actor, elapsed



# -------------------------
# Manual VTK
# -------------------------

def benchmark_prepare_actor(
    mesh,
    vtk_colors,
    vtk_texture
):

    times = {}

    start = time.perf_counter()


    # -----------------
    # polydata
    # -----------------

    t = time.perf_counter()

    polydata = mesh.copy()

    polydata.GetPointData().SetScalars(
        vtk_colors
    )

    times["polydata + colors"] = (
        time.perf_counter() - t
    )


    # -----------------
    # mapper
    # -----------------

    t = time.perf_counter()

    mapper = vtk.vtkPolyDataMapper()

    mapper.SetInputData(
        polydata
    )

    mapper.ScalarVisibilityOn()

    mapper.SetScalarModeToUsePointData()

    mapper.SetColorModeToDirectScalars()

    mapper.InterpolateScalarsBeforeMappingOff()


    times["mapper"] = (
        time.perf_counter() - t
    )


    # -----------------
    # actor
    # -----------------

    t = time.perf_counter()

    actor = vtk.vtkActor()

    actor.SetMapper(
        mapper
    )

    actor.SetTexture(
        vtk_texture
    )

    actor.GetProperty().SetLighting(
        False
    )


    times["actor"] = (
        time.perf_counter() - t
    )


    times["CPU TOTAL"] = (
        time.perf_counter()
        -
        start
    )


    return actor, times


def benchmark_add_actor(
    plotter,
    actor
):

    start = time.perf_counter()

    plotter.add_actor(
        actor
    )

    elapsed = (
        time.perf_counter()
        -
        start
    )

    return elapsed
# -------------------------
# Run test
# -------------------------

plotter = pv.Plotter(
    shape=(1,2)
)


# -------------------------
# LEFT
# -------------------------

plotter.subplot(
    0,
    0
)


plotter.add_text(
    "PyVista add_mesh"
)


print("\n--- ADD MESH ---")


actor1, add_time = benchmark_add_mesh(
    plotter,
    mesh,
    texture,
    colors
)


print(
    f"add_mesh total: {add_time*1000:.3f} ms"
)


plotter.camera_position = "iso"



# -------------------------
# RIGHT
# -------------------------

plotter.subplot(
    0,
    1
)


plotter.add_text(
    "Manual VTK Actor"
)


print("\n--- MANUAL ACTOR CPU PREP ---")


actor2, times = benchmark_prepare_actor(
    mesh,
    vtk_colors,
    texture
)


for name, value in times.items():

    print(
        f"{name:25s}: {value*1000:.3f} ms"
    )



print("\n--- ADD ACTOR TO RENDERER ---")


add_time = benchmark_add_actor(
    plotter,
    actor2
)


print(
    f"add_actor: {add_time*1000:.3f} ms"
)


plotter.camera_position = "iso"



# -------------------------
# Show
# -------------------------

plotter.link_views()

plotter.show()