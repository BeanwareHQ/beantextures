"""Custom attributes for node generation settings under the node editor sidebar."""

import bpy

# TODO: link to the same array at props_nodes.py?
beantextures_link_type = [
        ('INT_SIMPLE', "Int", "Simple integer linking", 0),
        ('INT', "Int", "Integer linking (advanced)", 1),
        ('FLOAT', "Float", "Float linking", 2),
        ('ENUM', "Enum", "Enum linking", 3),
]

class Beantxs_ConfigEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Config Name", description="Name of Beantextures configuration entry")
    link_type: bpy.props.EnumProperty(items=beantextures_link_type, name="Linking Type", description="Approach to link values to images")
    target_node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree, name="Target Node Tree", description="The node tree configured to be a Beantextures node")
    output_alpha: bpy.props.BoolProperty(default=False, name="Output Alpha", description="Whether or not the generated node should output alpha of the active image")

class Beantxs_LinkItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Link Name", description="Name of a Beantextures image link")
    img: bpy.props.PointerProperty(type=bpy.types.Image, name="Linked Image")

    int_simple_val: bpy.props.IntProperty(name="Int Value")
    int_lt: bpy.props.IntProperty(name="When Int is Less than")
    int_gt: bpy.props.IntProperty(name="When Int is Greater than")

    float_lt: bpy.props.FloatProperty(name="When Float is Less Than")
    float_gt: bpy.props.FloatProperty(name="When Float is Greater Than")

class Beantxs_GlobalSettings(bpy.types.PropertyGroup):
    node_tree_adder_name: bpy.props.StringProperty(name="New Node Tree Name", description="Name to assign for a new node tree", default="Beantextures")
    configs: bpy.props.CollectionProperty(type=Beantxs_ConfigEntry, name="Beantextures Configurations", description="List of stored configurations for active scene")
    active_config_idx: bpy.props.IntProperty(name="Index of Active Configuration")

def register():
    bpy.utils.register_class(Beantxs_ConfigEntry)
    bpy.utils.register_class(Beantxs_GlobalSettings)
    bpy.types.Scene.beantextures_settings = bpy.props.PointerProperty(type=Beantxs_GlobalSettings, name="Per-Scene Beantextures Settings", description="Beantextures properties for node generation settings")

def unregister():
    bpy.utils.unregister_class(Beantxs_ConfigEntry)
    bpy.utils.unregister_class(Beantxs_GlobalSettings)
