import pyvista as pv
from .mesh_asset import MeshAsset
from Rendering.render_mesh import RenderMesh
from .load_snail import load_snail_asset

from pathlib import Path
import pickle


class AssetLibrary:

    def __init__(self):

        self.data_dir = (
            Path(__file__).resolve().parent.parent / "Data"
        )


        # -------------------------
        # Loaded assets
        # -------------------------

        self.node_mesh = None
        self.hallway_mesh = None
        self.cap_mesh = None

        self.texture = None

        # render assets
        self.node_render = None
        self.hallway_render = None
        self.cap_render = None


        # player assets

        self.snail = None


        # navigation

        self.nav_library = None


        # render library

        self.render_meshes = None
        self.edge_meshes = None



    def load_all(self):

        DATA_DIR = self.data_dir


        print("Loading mesh assets...")

        self.node_mesh = MeshAsset(
            DATA_DIR / "node.obj"
        )

        self.hallway_mesh = MeshAsset(
            DATA_DIR / "hallway.obj"
        )

        self.cap_mesh = MeshAsset(
            DATA_DIR / "cap.obj"
        )


        print("Loading texture...")

        self.texture = pv.read_texture(
            DATA_DIR / "texture_2.png"
        )

        self.texture.SetMipmap(True)
        self.texture.InterpolateOn()



        print("Building render meshes...")

        self.node_render = RenderMesh(
            self.node_mesh,
            self.texture
        )


        self.hallway_render = RenderMesh(
            self.hallway_mesh,
            self.texture
        )


        self.cap_render = RenderMesh(
            self.cap_mesh,
            self.texture
        )



        print("Loading snail...")

        self.snail = load_snail_asset(
            DATA_DIR
        )



        print("Loading navigation library...")

        self.load_nav_library(
            DATA_DIR
        )


        print("Loading render library...")

        self.load_render_library(
            DATA_DIR
        )


        print("Asset loading complete")



    def load_nav_library(
        self,
        directory
    ):

        with open(
            directory / "nav_library.pkl",
            "rb"
        ) as f:

            self.nav_library = (
                self.NavUnpickler(f).load()
            )



    def load_render_library(
        self,
        directory
    ):

        render_dir = (
            directory / "render_meshes"
        )

        edge_dir = (
            directory / "edge_meshes"
        )


        self.render_meshes = []
        self.edge_meshes = []


        for i in range(64):

            render_path = (
                render_dir / f"rmesh{i}.vtp"
            )

            edge_path = (
                edge_dir / f"emesh{i}.vtp"
            )


            self.render_meshes.append(
                pv.read(render_path)
            )


            self.edge_meshes.append(
                pv.read(edge_path)
            )


        print(
            "Loaded render library:",
            len(self.render_meshes),
            "meshes"
        )



    class NavUnpickler(pickle.Unpickler):

        def find_class(
            self,
            module,
            name
        ):

            if module == "nav_data":
                module = "Assets.nav_data"

            return super().find_class(
                module,
                name
            )