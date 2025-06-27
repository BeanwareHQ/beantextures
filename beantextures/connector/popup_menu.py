"""Definition of popup menus used to display the `Value` input of a Beantextures node."""
import bpy
from bpy.types import UILayout
from .props import Btxs_ConnectorInstance, update_valid_nodes_list

def list_draw(self, context, layout: UILayout, label: bool = False):
    layout = layout
    layout.use_property_split = True
    col = layout.column()
    connector: list[Btxs_ConnectorInstance] = context.active_bone.beantextures_connector
    connectors_sorted: list[Btxs_ConnectorInstance] = sorted(connector.connectors, key=lambda x: x.menu_index)
    available = False

    if label:
        col.label(text="Beantextures Nodes Control")
        col.separator()

    for item in connectors_sorted:
        if (item.material is not None) and item.material.use_nodes and item.show:
            if (item.node_name in item.material.node_tree.nodes) and ("Value" in item.material.node_tree.nodes[item.node_name].inputs):
                available = True
                row = col.row()
                row.alignment = 'EXPAND'
                row.label(text="", icon=item.icon)

                if item.material.node_tree.nodes[item.node_name].node_tree.beantextures_props.link_type == 'ENUM':
                    row.prop(item.material.node_tree.nodes[item.node_name], "beantxs_enum_prop", text=item.name)
                else:
                    row.prop(item.material.node_tree.nodes[item.node_name].inputs["Value"], "default_value", icon=item.icon, text=item.name)

    if not available:
        col.label(text="No connector item available.", icon='INFO')


class BtxsOp_ListMenu(bpy.types.Operator):
    """Show properties of Beantexture nodes on active bone as a list"""
    bl_label = "Display Beantextures Props List"
    # WARNING: does bl_idname *force* you to have a predefined Blender ID (`pose` here) so it can be assigned a keybind?
    bl_idname = "pose.connector_popup_list_show"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        try:
            return (hasattr(context, "active_bone") and context.mode == 'POSE')
        except AttributeError:
            return False

    def draw(self, context):
        list_draw(self, context, self.layout, label=True)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        connector: list[Btxs_ConnectorInstance] = context.active_bone.beantextures_connector
        try:
            item = connector.connectors[connector.active_connector_idx]
            update_valid_nodes_list(item, context)
        except IndexError:
            pass

        wm = context.window_manager
        bpy.context.area.tag_redraw()

        # HACK: this doesn't seem right..
        return wm.invoke_popup(self)

class BtxsOp_PieMenuItem(bpy.types.Operator):
    """Show selected property"""
    bl_label = "Display Beantextures Props List"
    bl_idname = "beantextures.show_pie_menu_item"
    bl_options = {'INTERNAL'}

    idx: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        try:
            return (hasattr(context, "active_bone") and context.mode == 'POSE')
        except AttributeError:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        row = layout.row()
        row.alignment = 'EXPAND'
        connector = context.active_bone.beantextures_connector

        item = connector.connectors[self.idx]

        row.label(text="", icon=item.icon)
        if item.material.node_tree.nodes[item.node_name].node_tree.beantextures_props.link_type == 'ENUM':
            row.prop(item.material.node_tree.nodes[item.node_name], "beantxs_enum_prop", text=item.name)
        else:
            row.prop(item.material.node_tree.nodes[item.node_name].inputs["Value"], "default_value", icon=item.icon, text=item.name)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        bpy.context.area.tag_redraw()

        # HACK: this doesn't seem right..
        return wm.invoke_popup(self)

class BtxsOp_PieMenu(bpy.types.Menu):
    """Show properties of Beantexture nodes on active bone as a pie menu"""
    bl_label = "Beantextures Props List"
    bl_idname = "BEANTEXTURES_MT_pie_menu"

    @classmethod
    def poll(cls, context):
        try:
            return (hasattr(context, "active_bone") and context.mode == 'POSE')
        except AttributeError:
            return False

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        layout = layout
        layout.use_property_split = True
        connector = context.active_bone.beantextures_connector
        connectors_sorted: list[Btxs_ConnectorInstance] = sorted(connector.connectors, key=lambda x: x.menu_index)
        available = False

        for item in connectors_sorted:
            available = True

            if (item.material is not None) and item.material.use_nodes and item.show and (item.node_name in item.material.node_tree.nodes) and ("Value" in item.material.node_tree.nodes[item.node_name].inputs):
                pie.operator(BtxsOp_PieMenuItem.bl_idname, text=item.name, icon=item.icon).idx = connector.connectors.keys().index(item.name)

        if not available:
            col.label(text="No connector item available.", icon='INFO')


class BtxsOp_ShowMenu(bpy.types.Operator):
    """Show properties of Beantexture nodes on active bone"""
    bl_label = "Display Beantextures Props"
    bl_idname = "beantextures.connector_popup_show"

    @classmethod
    def poll(cls, context):
        try:
            return (hasattr(context, "active_bone") and context.mode == 'POSE')
        except AttributeError:
            return False
    
    def execute(self, context):
        connector: list[Btxs_ConnectorInstance] = context.active_bone.beantextures_connector
        
        match connector.menu_type:
            case 'LIST':
                # FIXME: don't hardcode?
                bpy.ops.pose.connector_popup_list_show('INVOKE_DEFAULT')
            case 'PIE':
                bpy.ops.wm.call_menu_pie(name=BtxsOp_PieMenu.bl_idname)

        return {'FINISHED'}

addon_keymaps = [] 

def register():
    bpy.utils.register_class(BtxsOp_ListMenu)
    bpy.utils.register_class(BtxsOp_PieMenuItem)
    bpy.utils.register_class(BtxsOp_PieMenu)
    bpy.utils.register_class(BtxsOp_ShowMenu)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new(BtxsOp_ShowMenu.bl_idname, 'G', 'PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(BtxsOp_ListMenu)
    bpy.utils.unregister_class(BtxsOp_PieMenuItem)
    bpy.utils.unregister_class(BtxsOp_PieMenu)
    bpy.utils.unregister_class(BtxsOp_ShowMenu)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
