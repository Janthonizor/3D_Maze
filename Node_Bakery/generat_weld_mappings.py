from asset_holder import AssetHolder
from mapping_creator import MappingCreator
import pickle


assets = AssetHolder("assets")


creator = MappingCreator(
    assets
)


mappings = creator.generate_all()


with open(
    "weld_mappings.pkl",
    "wb"
) as f:

    pickle.dump(
        mappings,
        f
    )


print("Saved weld_mappings.pkl")