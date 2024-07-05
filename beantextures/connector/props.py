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

class Btxs_ConnectorValidNode(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class Btxs_ConnectorTmpProps(bpy.types.PropertyGroup):
    valid_nodes: bpy.props.CollectionProperty(type=Btxs_ConnectorValidNode)

class Btx_ConnectorInstance(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty(name="Node Name", description="A Beantextures node group instance to control")
    menu_index: bpy.props.IntProperty(name="Menu Index", description="Index of the connector item; will influence the order of the item when displayed")
    icon: bpy.props.EnumProperty(items=icons_enum, name="Icon", description="Icon used to identify the connector item", default='NODETREE')
    show: bpy.props.BoolProperty(name="Show on Menu", default=True)

class Btxs_Connector(bpy.types.PropertyGroup):
    connectors: bpy.props.CollectionProperty(type=Btx_ConnectorInstance, name="Connector Items")
    active_connector_idx: bpy.props.IntProperty(name="Index of Active Connector Item")

def register():
    bpy.utils.register_class(Btxs_ConnectorValidNode)
    bpy.utils.register_class(Btxs_ConnectorTmpProps)
    bpy.utils.register_class(Btx_ConnectorInstance)
    bpy.utils.register_class(Btxs_Connector)

    bpy.types.Scene.beantextures_connector_tmp = bpy.props.PointerProperty(type=Btxs_ConnectorTmpProps)
    bpy.types.Bone.beantextures_connector = bpy.props.PointerProperty(type=Btxs_Connector)

def unregister():
    bpy.utils.unregister_class(Btxs_ConnectorValidNode)
    bpy.utils.unregister_class(Btxs_ConnectorTmpProps)
    bpy.utils.unregister_class(Btx_ConnectorInstance)
    bpy.utils.unregister_class(Btxs_Connector)
