"""Operators used to configure connector items."""
import bpy
from bpy.types import Operator
from beantextures.connector.props import Btx_ConnectorInstance

def add_new_connector_item(context, name: str) -> Btx_ConnectorInstance:
    connector = context.active_bone.beantextures_connector
    item = connector.connectors.add()
    item.name = name
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
        try:
            return bool(context.active_bone and context.mode == 'POSE' and context.active_bone.beantextures_connector)
        except AttributeError:
            return False

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
        connectors = context.active_bone.beantextures_connector.connectors
        return (super().poll(context)) and (len(connectors) > 0)

    def execute(self, context):
        connector = context.active_bone.beantextures_connector
        remove_connector_item(context, connector.active_connector_idx)
        return {'FINISHED'}

class BtxsOp__RemoveAllConnector(BtxsOp_ConnectorOperator):
    """Remove all connector items"""
    bl_label = "Clear connector items"
    bl_idname = "beantextures.connector_remove_all"

    @classmethod
    def poll(cls, context):
        connectors = context.active_bone.beantextures_connector.connectors
        return (super().poll(context)) and (len(connectors) > 0)

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

def register():
    bpy.utils.register_class(BtxsOp_NewConnectorItem)
    bpy.utils.register_class(BtxsOp_RemoveSelectedConnectorItem)
    bpy.utils.register_class(BtxsOp__RemoveAllConnector)

def unregister():
    bpy.utils.unregister_class(BtxsOp_NewConnectorItem)
    bpy.utils.unregister_class(BtxsOp_RemoveSelectedConnectorItem)
    bpy.utils.unregister_class(BtxsOp__RemoveAllConnector)
