"""Custom attributes for node generation settings under the node editor sidebar."""

import bpy

beantextures_link_type: list[tuple[str, str, str, int]] = [
        ('INT_SIMPLE', "Int (Simple)", "Simple integer linking", 0),
        ('INT', "Int (Ranged)", "Integer linking (advanced)", 1),
        ('FLOAT', "Float", "Float linking", 2),
        ('ENUM', "Enum", "Enum linking", 3),
]

def get_builtin_image_texture_prop_enum_items(property_name: str) -> list[tuple[str, str, str, int]]:
    """Get the official image texture node's enum for given property name."""
    items = bpy.types.ShaderNodeTexImage.bl_rna.properties[property_name].enum_items #type: ignore
    return [(i.identifier, i.name, i.description, n) for n, i in enumerate(items)]

def get_builtin_image_texture_prop_name(property_name: str) -> str:
    """Get the official image texture node's (human readable) property name."""
    return bpy.types.ShaderNodeTexImage.bl_rna.properties[property_name].name

def get_builtin_image_texture_prop_description(property_name: str) -> str:
    """Get the official image texture node's (human readable) property description."""
    return bpy.types.ShaderNodeTexImage.bl_rna.properties[property_name].description

class Btxs_LinkItem_ImageProps(bpy.types.PropertyGroup):
    interpolation: bpy.props.EnumProperty(items=get_builtin_image_texture_prop_enum_items("interpolation"), name=get_builtin_image_texture_prop_name("interpolation"), description=get_builtin_image_texture_prop_description("interpolation"))
    projection: bpy.props.EnumProperty(items=get_builtin_image_texture_prop_enum_items("projection"), name=get_builtin_image_texture_prop_name("projection"), description=get_builtin_image_texture_prop_description("projection"))
    extension: bpy.props.EnumProperty(items=get_builtin_image_texture_prop_enum_items("extension"), name=get_builtin_image_texture_prop_name("extension"), description=get_builtin_image_texture_prop_description("extension"))

class Btxs_LinkItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Link Name", description="Name of a Beantextures image link")
    img: bpy.props.PointerProperty(type=bpy.types.Image, name="Linked Image")

    int_simple_val: bpy.props.IntProperty(name="Int Value")
    int_lt: bpy.props.IntProperty(name="When Int is Less than")
    int_gt: bpy.props.IntProperty(name="When Int is Greater than")

    float_lt: bpy.props.FloatProperty(name="When Float is Less Than")
    float_gt: bpy.props.FloatProperty(name="When Float is Greater Than")

    image_node_properties: bpy.props.PointerProperty(type=Btxs_LinkItem_ImageProps, name="Image Node Properties", description="Properties to assign to image nodes")

class Btxs_ConfigEntry(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Config Name", description="Name of Beantextures configuration entry")
    fallback_img: bpy.props.PointerProperty(type=bpy.types.Image, name="Fallback Image", description="Image to use when user-defined value does not match any link and therefore image (will output black if this is not set)")
    linking_type: bpy.props.EnumProperty(items=beantextures_link_type, name="Linking Type", description="Approach to link values to images")
    target_node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree, name="Target Node Tree", description="Node tree to be configured")
    output_alpha: bpy.props.BoolProperty(default=False, name="Output Alpha", description="Whether or not the generated node should output alpha of the active image")
    active_link_idx: bpy.props.IntProperty(name="Index of Active Link")
    links: bpy.props.CollectionProperty(type=Btxs_LinkItem, name="Configured Links", description="Collection of defined value-image links")

    int_max: bpy.props.IntProperty(name="Maximum Int Value", default=2)
    int_min: bpy.props.IntProperty(name="Maximum Int Value", default=1)

    float_max: bpy.props.FloatProperty(name="Maximum Float Value", default=2.0)
    float_min: bpy.props.FloatProperty(name="Minimum Float Value", default=0.9)

class Btxs_GlobalSettings(bpy.types.PropertyGroup):
    node_group_adder_name: bpy.props.StringProperty(name="Node Group Name", description="Name to assign for the new group", default="Beantextures")
    configs: bpy.props.CollectionProperty(type=Btxs_ConfigEntry, name="Beantextures Configurations", description="List of stored configurations for active scene")
    active_config_idx: bpy.props.IntProperty(name="Index of Active Configuration")
    #link_err_msg: bpy.props.Str

def register():
    bpy.utils.register_class(Btxs_LinkItem_ImageProps)
    bpy.utils.register_class(Btxs_LinkItem)
    bpy.utils.register_class(Btxs_ConfigEntry)
    bpy.utils.register_class(Btxs_GlobalSettings)
    bpy.types.Scene.beantextures_settings = bpy.props.PointerProperty(type=Btxs_GlobalSettings, name="Per-Scene Beantextures Settings", description="Beantextures properties for node generation settings")

def unregister():
    bpy.utils.unregister_class(Btxs_LinkItem_ImageProps)
    bpy.utils.unregister_class(Btxs_LinkItem)
    bpy.utils.unregister_class(Btxs_ConfigEntry)
    bpy.utils.unregister_class(Btxs_GlobalSettings)
    del(bpy.types.Scene.beantextures_settings)
