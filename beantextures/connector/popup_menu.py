"""Definition of popup menus used to display the `Value` input of a Beantextures node."""
import bpy
from beantextures.connector.props import Btxs_ConnectorInstance, update_valid_nodes_list

class BtxsOp_ListMenu(bpy.types.Operator):
    """Show properties of Beantexture nodes on active bone as a list"""
    bl_label = "Display Beantextures Props List"
    # WARNING: does bl_idname *force* you to have a predefined Blender ID (`pose` here) so it can be keymappable?
    bl_idname = "pose.connector_popup_list_show"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.active_bone and context.mode == 'POSE')
        except AttributeError:
            return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        connector: list[Btxs_ConnectorInstance] = context.active_bone.beantextures_connector
        connectors_sorted = sorted(connector.connectors, key=lambda x: x.menu_index)
        available = False

        col.label(text="Beantextures Nodes Control")
        col.separator()

        for item in connectors_sorted:
            if (item.material is not None) and item.material.use_nodes and item.show:
                if "Value" in item.material.node_tree.nodes[item.node_name].inputs:
                    available = True
                    row = col.row()
                    row.alignment = 'EXPAND'
                    row.label(text="", icon=item.icon)
                    row.prop(item.material.node_tree.nodes[item.node_name].inputs["Value"], "default_value", icon=item.icon, text=item.name)

        if not available:
            col.label(text="No connector item available.", icon='INFO')

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
        return wm.invoke_popup(self, width=350)

class BtxsOp_ShowMenu(bpy.types.Operator):
    """Show properties of Beantexture nodes on active bone"""
    bl_label = "Display Beantextures Props"
    bl_idname = "beantextures.connector_popup_show"

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.active_bone and context.mode == 'POSE')
        except AttributeError:
            return False
    
    def execute(self, context):
        connector: list[Btxs_ConnectorInstance] = context.active_bone.beantextures_connector
        
        match connector.menu_type:
            case 'LIST':
                # FIXME: don't hardcode?
                bpy.ops.pose.connector_popup_list_show('INVOKE_DEFAULT')
            case 'PIE':
                print("unimplemented")
            
        return {'FINISHED'}

addon_keymaps = [] 

def register():
    bpy.utils.register_class(BtxsOp_ListMenu)
    bpy.utils.register_class(BtxsOp_ShowMenu)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new(BtxsOp_ShowMenu.bl_idname, 'G', 'PRESS', ctrl=True)
        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(BtxsOp_ListMenu)
    bpy.utils.unregister_class(BtxsOp_ShowMenu)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
