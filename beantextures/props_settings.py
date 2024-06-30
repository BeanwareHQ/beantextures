"""Custom attributes for node generation settings under the node editor sidebar."""

import bpy

beantextures_link_type: list[tuple[str, str, str, int]] = [
        ('INT_SIMPLE', "Int (Simple)", "Simple integer linking", 0),
        ('INT', "Int (Ranged)", "Integer linking (advanced)", 1),
        ('FLOAT', "Float", "Float linking", 2),
        ('ENUM', "Enum", "Enum linking", 3),
]

class Beantxs_LinkItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Link Name", description="Name of a Beantextures image link")
    img: bpy.props.PointerProperty(type=bpy.types.Image, name="Linked Image")

    int_simple_val: bpy.props.IntProperty(name="Int Value")
    int_lt: bpy.props.IntProperty(name="When Int is Less than")
    int_gt: bpy.props.IntProperty(name="When Int is Greater than")

    float_lt: bpy.props.FloatProperty(name="When Float is Less Than")
    float_gt: bpy.props.FloatProperty(name="When Float is Greater Than")

class Beantxs_ConfigEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Config Name", description="Name of Beantextures configuration entry")
    fallback_img: bpy.props.PointerProperty(type=bpy.types.Image, name="Fallback Image", description="Image to use when user-defined value does not match any link and therefore image (will output black if this is not set)")
    linking_type: bpy.props.EnumProperty(items=beantextures_link_type, name="Linking Type", description="Approach to link values to images")
    target_node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree, name="Target Node Tree", description="Node tree to be configured")
    output_alpha: bpy.props.BoolProperty(default=False, name="Output Alpha", description="Whether or not the generated node should output alpha of the active image")
    active_link_idx: bpy.props.IntProperty(name="Index of Active Link")
    links: bpy.props.CollectionProperty(type=Beantxs_LinkItem, name="Configured Links", description="Collection of defined value-image links")

    int_max: bpy.props.IntProperty(name="Maximum Int Value", default=2)
    int_min: bpy.props.IntProperty(name="Maximum Int Value", default=1)

    float_max: bpy.props.FloatProperty(name="Maximum Float Value", default=2.0)
    float_min: bpy.props.FloatProperty(name="Minimum Float Value", default=0.9)

class Beantxs_GlobalSettings(bpy.types.PropertyGroup):
    node_group_adder_name: bpy.props.StringProperty(name="Node Group Name", description="Name to assign for the new group", default="Beantextures")
    configs: bpy.props.CollectionProperty(type=Beantxs_ConfigEntry, name="Beantextures Configurations", description="List of stored configurations for active scene")
    active_config_idx: bpy.props.IntProperty(name="Index of Active Configuration")

def register():
    bpy.utils.register_class(Beantxs_LinkItem)
    bpy.utils.register_class(Beantxs_ConfigEntry)
    bpy.utils.register_class(Beantxs_GlobalSettings)
    bpy.types.Scene.beantextures_settings = bpy.props.PointerProperty(type=Beantxs_GlobalSettings, name="Per-Scene Beantextures Settings", description="Beantextures properties for node generation settings")

def unregister():
    bpy.utils.unregister_class(Beantxs_LinkItem)
    bpy.utils.unregister_class(Beantxs_ConfigEntry)
    bpy.utils.unregister_class(Beantxs_GlobalSettings)
