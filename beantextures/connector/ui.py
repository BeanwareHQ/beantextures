"""User interface for the connector."""
import bpy
from bpy.types import UIList
from beantextures.connector.icon_picker import ICONS

def check_icon_validity(icon_name: str) -> bool:
    return (icon_name in ICONS)

class BEANTEXTURES_UL_ConnectorItemsListRenderer(UIList):
    """
    Renderer for a Beantextures config for the template_list widget.
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon=item.icon)
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

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        connector = context.active_bone.beantextures_connector

        row.template_list("BEANTEXTURES_UL_ConnectorItemsListRenderer", "compact", connector, "connectors", connector, "active_connector_idx")

        layout.use_property_split = True

        col = row.column(align=True)
        col.operator("beantextures.connector_add", icon='ADD', text="")
        col.operator("beantextures.connector_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("beantextures.connector_remove_all", icon='X', text="")

def register():
    bpy.utils.register_class(BEANTEXTURES_UL_ConnectorItemsListRenderer)
    bpy.utils.register_class(Btxs_ConnectorPanel)

def unregister():
    bpy.utils.unregister_class(BEANTEXTURES_UL_ConnectorItemsListRenderer)
    bpy.utils.unregister_class(Btxs_ConnectorPanel)
