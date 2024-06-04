"""Operators related to the node generator settings."""

import bpy
from bpy.types import Operator
from beantextures.props_settings import Beantxs_LinkItem

def add_new_config(context, name: str):
    settings = context.scene.beantextures_settings
    config = settings.configs.add()
    config.name = name
    settings.active_config_idx = len(settings.configs) - 1

def remove_config(context, idx: int):
    settings = context.scene.beantextures_settings

    if settings.active_config_idx == len(settings.configs) - 1:
        settings.active_config_idx -= 1

    settings.configs.remove(idx)

def add_new_link(context) -> Beantxs_LinkItem:
    settings = context.scene.beantextures_settings
    config_idx = settings.active_config_idx
    config = settings.configs[config_idx]
    link = config.links.add()

    proper_idx = len(config.links) - 1
    try:
        if config.links[-2].name.isdigit():
            name = int(config.links[-2].name) + 1
        else:
            name = proper_idx + 1
    except IndexError:
        name = proper_idx + 1

    link.name = str(name)
    
    match config.linking_type:
        case 'INT_SIMPLE':
            link.int_simple_val = proper_idx + 1
        case 'INT':
            link.int_gt = proper_idx
            link.int_lt = proper_idx + 2
        case 'FLOAT':
            link.float_gt = proper_idx + 0.1
            link.float_lt = proper_idx + 1
        case 'ENUM':
            pass

    config.active_link_idx = proper_idx

    return link

def remove_link(context, idx: int):
    settings = context.scene.beantextures_settings
    config_idx = settings.active_config_idx
    config = settings.configs[config_idx]

    if config.active_link_idx == len(config.links) - 1:
        config.active_link_idx -= 1

    config.links.remove(idx)


# Operator Classes

class BeantxsOp_NewNodeTree(Operator):
    """Add a new shader node tree"""
    bl_label = "Add New Node Tree"
    bl_idname = "beantextures.new_node_tree"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # too short so no wrapper function.
        name = context.scene.beantextures_settings.node_tree_adder_name
        obj = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        # obj.name is used to get the real unique name (`name` may already exist)
        self.report({'INFO'}, f"Added node tree '{obj.name}'")
        return {'FINISHED'}

class BeantxsOp_NewConfig(Operator):
    bl_label = "Add New Configuration"
    bl_idname = "beantextures.new_config"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        add_new_config(context, "New Config")
        return {'FINISHED'}

class BeantxsOp_RemoveSelectedConfig(Operator):
    bl_label = "Remove Selected Configuration"
    bl_idname = "beantextures.remove_config"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        idx = context.scene.beantextures_settings.active_config_idx
        remove_config(context, idx)
        return {'FINISHED'}

class BeantxsOp_NewLink(Operator):
    bl_label = "Add New Link to Active Config"
    bl_idname = "beantextures.new_link"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        add_new_link(context)
        return {'FINISHED'}

class BeantxsOp_RemoveLink(Operator):
    bl_label = "Remove Selected Link"
    bl_idname = "beantextures.remove_link"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.beantextures_settings
        config_idx = settings.active_config_idx
        config = settings.configs[config_idx]

        remove_link(context, config.active_link_idx)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(BeantxsOp_NewNodeTree) 
    bpy.utils.register_class(BeantxsOp_NewConfig) 
    bpy.utils.register_class(BeantxsOp_NewLink) 
    bpy.utils.register_class(BeantxsOp_RemoveLink) 
    bpy.utils.register_class(BeantxsOp_RemoveSelectedConfig) 

def unregister():
    bpy.utils.unregister_class(BeantxsOp_NewNodeTree)
    bpy.utils.unregister_class(BeantxsOp_NewConfig) 
    bpy.utils.unregister_class(BeantxsOp_NewLink) 
    bpy.utils.unregister_class(BeantxsOp_RemoveLink) 
    bpy.utils.unregister_class(BeantxsOp_RemoveSelectedConfig) 
