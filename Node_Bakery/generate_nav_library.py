from asset_holder import AssetHolder
from node_builder import NodeBuilder
from nav_mesh import NavMesh
import pickle




assets = AssetHolder(
    "assets"
)


builder = NodeBuilder(
    assets
)

data_mesh_list = [None] * 64

for i in range(64):
    vertices, triangles = builder.build_node(
        i
    )
    print(i)
    mesh = NavMesh(
        i,
        vertices,
        triangles
    )
    data_mesh_list[i] = mesh.export()

with open("nav_library.pkl", "wb") as f:
    pickle.dump(data_mesh_list, f)



