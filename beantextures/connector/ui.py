"""User interface for the connector."""
import bpy
from bpy.types import UIList
from beantextures.connector.icon_picker import ICONS, BtxsOp_IV_OT_icons_set

def check_icon_validity(icon_name: str) -> bool:
    return (icon_name in ICONS)

class BEANTEXTURES_UL_ConnectorItemsListRenderer(UIList):
    """
    Renderer for a Beantextures config for the template_list widget.
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                layout.operator(BtxsOp_IV_OT_icons_set.bl_idname, text="", icon=item.icon, emboss=True)
                layout.prop(item, "name", text="", emboss=False)
                if item.show:
                    layout.prop(item, "show", text="", emboss=False, icon='HIDE_OFF')
                else:
                    layout.prop(item, "show", text="", emboss=False, icon='HIDE_ON')
            else:
                layout.label(text="", translate=False, icon_value=icon, icon=item.icon)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class Btxs_ConnectorPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    bl_idname = "BEANTEXTURES_PT_connector"
    bl_label = "Beantextures Connector"

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.active_bone and context.mode == 'POSE' and context.active_bone.beantextures_connector)
        except AttributeError:
            return False

    def draw(self, context):
        connector = context.active_bone.beantextures_connector
        layout = self.layout

        layout.column().label(text="Display as:")
        row = layout.row()
        row.prop(connector, "menu_type", expand=True)


class Btxs_ConnectorItemsList(bpy.types.Panel):
    bl_parent_id="BEANTEXTURES_PT_connector"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    bl_idname = "BEANTEXTURES_PT_connector_items_list"
    bl_label = "Connector Items"

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.active_bone and context.mode == 'POSE' and context.active_bone.beantextures_connector)
        except AttributeError:
            return False

    def draw(self, context):
        connector = context.active_bone.beantextures_connector
        layout = self.layout
        row = layout.row()
        row.template_list("BEANTEXTURES_UL_ConnectorItemsListRenderer", "compact", connector, "connectors", connector, "active_connector_idx")

        col = row.column(align=True)
        col.operator("beantextures.connector_add", icon='ADD', text="")
        col.operator("beantextures.connector_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("beantextures.connector_remove_all", icon='X', text="")

        try:
            layout.use_property_split = True
            
            idx = connector.active_connector_idx
            item = connector.connectors[idx]

            col = layout.column()
            col.prop(item, "menu_index", text="Menu Index")

            row = col.row()


        except IndexError:
            layout.column().label(text="No connector item available.")


def register():
    bpy.utils.register_class(BEANTEXTURES_UL_ConnectorItemsListRenderer)
    bpy.utils.register_class(Btxs_ConnectorPanel)
    bpy.utils.register_class(Btxs_ConnectorItemsList)

def unregister():
    bpy.utils.unregister_class(BEANTEXTURES_UL_ConnectorItemsListRenderer)
    bpy.utils.unregister_class(Btxs_ConnectorPanel)
    bpy.utils.unregister_class(Btxs_ConnectorItemsList)
