"""Custom properties for Beantexture's connector."""
import bpy
from beantextures.connector.icon_picker import ICONS

icons_enum: list[tuple[str, str, str, int]] = [
        (icon, icon.title(), icon.title(), i) for i, icon in enumerate(ICONS)
]

beantextures_connector_menu_types: list[tuple[str, str, str, int]] = [
        ('LIST', "List", "Pop-up panel listing all available connectors", 0),
        ('PIE', "Pie", "Pie menu listing all available connectors", 1)
]

def generate_valid_nodes(material: bpy.types.Material) -> list[str]:
    nodes = material.node_tree.nodes
    return [node.name for node in nodes if (isinstance(node, bpy.types.ShaderNodeGroup) and node.node_tree.is_beantextures)]

# FIXME: this is not executed periodically; only when the user changes the target material.
# For now the solution is to have a dedicated operator used to refresh the list manually whenever
# needed.
def update_valid_nodes_list(self, context):
    valid_nodes_list = self.valid_nodes
    valid_nodes_list.clear()
    if self.material is not None and self.material.use_nodes:
        valid_nodes = generate_valid_nodes(self.material)

        for node_name in valid_nodes:
            item = valid_nodes_list.add()
            item.name = node_name

class Btxs_ConnectorValidNode(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class Btxs_ConnectorInstance(bpy.types.PropertyGroup):
    valid_nodes: bpy.props.CollectionProperty(type=Btxs_ConnectorValidNode)
    material: bpy.props.PointerProperty(type=bpy.types.Material, name="Material Selection", description="Location of target node group instance", update=update_valid_nodes_list)
    name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty(name="Node Name", description="A Beantextures node group instance to control")
    menu_index: bpy.props.IntProperty(name="Menu Index", description="Index of the connector item; will influence the order of the item when displayed")
    icon: bpy.props.EnumProperty(items=icons_enum, name="Icon", description="Icon used to identify the connector item", default='NODETREE')
    show: bpy.props.BoolProperty(name="Show on View3D Sidebar and Pop-up", default=True)

class Btxs_Connector(bpy.types.PropertyGroup):
    connectors: bpy.props.CollectionProperty(type=Btxs_ConnectorInstance, name="Connector Items")
    active_connector_idx: bpy.props.IntProperty(name="Index of Active Connector Item")
    menu_type: bpy.props.EnumProperty(items=beantextures_connector_menu_types, name="Menu Type", default='LIST')

    # used by the pie popup menu 
    tmp_connector_idx: bpy.props.IntProperty()

def register():
    bpy.utils.register_class(Btxs_ConnectorValidNode)
    bpy.utils.register_class(Btxs_ConnectorInstance)
    bpy.utils.register_class(Btxs_Connector)

    bpy.types.Bone.beantextures_connector = bpy.props.PointerProperty(type=Btxs_Connector)

def unregister():
    bpy.utils.unregister_class(Btxs_ConnectorValidNode)
    bpy.utils.unregister_class(Btxs_ConnectorInstance)
    bpy.utils.unregister_class(Btxs_Connector)
