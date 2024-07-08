"""Custom attributes for Blender node and node tree classes."""

import bpy
from beantextures.props_settings import beantextures_link_type

def generate_linking_enum_items(self: bpy.types.ShaderNodeGroup, context):
    """Used by node group instances. This function returns a list of enum items based on the respecting node tree's (not the instance itself!) `enum_items` property."""
    items = self.node_tree.beantextures_props.enum_items
    # BUG: putting `item.name` as the description turns all the tooltips gibberish ...
    return [(str(item.idx), item.name, "Select item", item.idx) for item in items]

class Btxs_EnumItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Enum item name", description="Human-readable name assigned by user")
    idx: bpy.props.IntProperty(name="Enum item index", description="Integer linked to enum item")

class Btxs_NodeTree_props(bpy.types.PropertyGroup):
    link_type: bpy.props.EnumProperty(items=beantextures_link_type, name="Linking type", description="Defines how Beantextures Node links values to images")

    # Enum linking specific properties
    # Custom node groups don't support enum sockets.
    # Technically, our enum linking is just a fancy wrapper
    # to the int linking.
    enum_items: bpy.props.CollectionProperty(type=Btxs_EnumItem, name="Enum items", description="Available enum items; only used if linking type is set to enum")

def register():
    bpy.utils.register_class(Btxs_EnumItem)
    bpy.utils.register_class(Btxs_NodeTree_props)

    bpy.types.NodeTree.is_beantextures = bpy.props.BoolProperty(name="Whether or not node tree is a Beantextures node")
    bpy.types.NodeTree.beantextures_props = bpy.props.PointerProperty(type=Btxs_NodeTree_props)
    bpy.types.ShaderNodeGroup.beantxs_enum_prop = bpy.props.EnumProperty(items=generate_linking_enum_items, name="Beantextures enum driver property")


def unregister():
    bpy.utils.unregister_class(Btxs_EnumItem)
    bpy.utils.unregister_class(Btxs_NodeTree_props)
