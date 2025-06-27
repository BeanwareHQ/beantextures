"""Operators used to configure connector items."""
import bpy
from bpy.types import Operator
from .props import Btxs_ConnectorInstance, update_valid_nodes_list

def add_new_connector_item(context, name: str) -> Btxs_ConnectorInstance:
    connector = context.active_bone.beantextures_connector
    item = connector.connectors.add()
    item.name = name
    item.menu_index = len(connector.connectors) - 1
    connector.active_connector_idx = len(connector.connectors) - 1
    return item

def remove_connector_item(context, idx: int):
    connector = context.active_bone.beantextures_connector

    if connector.active_connector_idx == len(connector.connectors) - 1:
        connector.active_connector_idx -= 1

    connector.connectors.remove(idx)

class BtxsOp_ConnectorOperator(Operator):

    @classmethod
    def poll(cls, context):
        return (
            context.mode == "POSE"
            and hasattr(context, 'active_bone')
            and hasattr(context.active_bone, 'beantextures_connector')
        )

class BtxsOp_NewConnectorItem(BtxsOp_ConnectorOperator):
    """Add a new connector item"""
    bl_label = "Add Connector Item"
    bl_idname = "beantextures.connector_add"

    def execute(self, context):
        add_new_connector_item(context, "New Connector Item")
        return {'FINISHED'}

class BtxsOp_RemoveSelectedConnectorItem(BtxsOp_ConnectorOperator):
    """Remove selected connector item"""
    bl_label = "Remove Connector Item"
    bl_idname = "beantextures.connector_remove"

    @classmethod
    def poll(cls, context):
        return (super().poll(context)) and (len(context.active_bone.beantextures_connector.connectors) > 0)

    def execute(self, context):
        connector = context.active_bone.beantextures_connector
        remove_connector_item(context, connector.active_connector_idx)
        return {'FINISHED'}

class BtxsOp_RemoveAllConnector(BtxsOp_ConnectorOperator):
    """Remove all connector items"""
    bl_label = "Clear connector items"
    bl_idname = "beantextures.connector_remove_all"

    @classmethod
    def poll(cls, context):
        return (super().poll(context)) and (len(context.active_bone.beantextures_connector.connectors) > 0)

    def execute(self, context):
        connector = context.active_bone.beantextures_connector
        connector.connectors.clear()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.column().label(text="Delete all connector items?")

    def invoke(self, context, event):
        wm = context.window_manager
        bpy.context.area.tag_redraw()
        return wm.invoke_props_dialog(self)

class BtxsOp_ReloadNodeNames(BtxsOp_ConnectorOperator):
    """Reload available Beantextures node group instances"""
    bl_label = "Reload List"
    bl_idname = "beantextures.connector_reload_group_list"

    def execute(self, context):
        connector = context.active_bone.beantextures_connector
        item = connector.connectors[connector.active_connector_idx]
        update_valid_nodes_list(item, context)
        item.node_is_valid = True if item.node_name in item.valid_nodes else False
        return {'FINISHED'}

class BtxsOp_ReloadAllNodeNames(BtxsOp_ConnectorOperator):
    """Reload available Beantextures node group instances across all connector items"""
    bl_label = "Reload List"
    bl_idname = "beantextures.connector_reload_all_group_list"

    @classmethod
    def poll(cls, context):
        return (super().poll(context)) and (len(context.active_bone.beantextures_connector.connectors) > 0)

    def execute(self, context):
        connector = context.active_bone.beantextures_connector
        for item in connector.connectors:
            update_valid_nodes_list(item, context)
            item.node_is_valid = True if item.node_name in item.valid_nodes else False
        return {'FINISHED'}


class BtxsOp_ModifyNodeSelection(BtxsOp_ConnectorOperator):
    """Select a target material"""
    bl_label = "Set Target Material"
    bl_idname = "beantextures.connector_set_target_material"

    @classmethod
    def poll(cls, context):
        return (super().poll(context)) and (len(context.active_bone.beantextures_connector.connectors) > 0)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        connector = context.active_bone.beantextures_connector
        item = connector.connectors[connector.active_connector_idx]
        col.prop(item, "material", text="Material")
        if item.material is not None and not item.material.use_nodes:
            col.label(text="Warning: material doesn't use nodes", icon='ERROR')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        bpy.context.area.tag_redraw()

        # HACK: this doesn't seem right..
        return wm.invoke_popup(self)
        

def register():
    bpy.utils.register_class(BtxsOp_NewConnectorItem)
    bpy.utils.register_class(BtxsOp_RemoveSelectedConnectorItem)
    bpy.utils.register_class(BtxsOp_RemoveAllConnector)
    bpy.utils.register_class(BtxsOp_ModifyNodeSelection)
    bpy.utils.register_class(BtxsOp_ReloadNodeNames)
    bpy.utils.register_class(BtxsOp_ReloadAllNodeNames)

def unregister():
    bpy.utils.unregister_class(BtxsOp_NewConnectorItem)
    bpy.utils.unregister_class(BtxsOp_RemoveSelectedConnectorItem)
    bpy.utils.unregister_class(BtxsOp_RemoveAllConnector)
    bpy.utils.unregister_class(BtxsOp_ModifyNodeSelection)
    bpy.utils.unregister_class(BtxsOp_ReloadNodeNames)
    bpy.utils.unregister_class(BtxsOp_ReloadAllNodeNames)
