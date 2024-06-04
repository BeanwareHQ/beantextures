"""UI Interface for the node generator."""
import bpy
from bpy.types import Panel, UIList

class BeantexturesNodePanel(Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Beantextures"

    @classmethod
    def poll(cls, context):
        return True

class NodeTreePanel(BeantexturesNodePanel):
    bl_idname = "BEANTEXTURES_PT_node_tree_adder"
    bl_label = "Node Tree"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.row().prop(bpy.context.scene.beantextures_settings, "node_tree_adder_name")
        layout.row().operator("beantextures.new_node_tree", text="Add", icon='PLUS')

class BEANTEXTURES_UL_ConfigsListRenderer(UIList):
    """
    Renderer for a Beantextures config for the template_list widget.
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon='TOOL_SETTINGS')
            else:
                layout.label(text="", translate=False, icon_value=icon, icon='TOOL_SETTINGS')

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class ConfigsPanel(BeantexturesNodePanel):
    bl_idname = "BEANTEXTURES_PT_configs"
    bl_label = "Configurations"

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        settings = bpy.context.scene.beantextures_settings
        row.template_list("BEANTEXTURES_UL_ConfigsListRenderer", "compact", settings, "configs", settings, "active_config_idx")
        
        layout.use_property_split = True

        col = row.column(align=True)
        col.operator("beantextures.new_config", icon='ADD', text="")
        col.operator("beantextures.remove_config", icon='REMOVE', text="")

        try:
            idx = settings.active_config_idx
            item = settings.configs[idx]

            col = layout.column()
            col.prop(item, "linking_type", text="Linking Type")
            col.prop(item, "target_node_tree", text="Target Node")
            col.prop(item, "output_alpha", text="Output alpha")

        except IndexError:
            layout.column().label(text="No configuration available.")

class BEANTEXTURES_UL_LinksListRenderer(UIList):
    """
    Renderer for a Beantextures link entry for the template_list widget.
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon='LINKED')
            else:
                layout.label(text="", translate=False, icon_value=icon, icon='LINKED')

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class LinksPanel(BeantexturesNodePanel):
    bl_idname = "BEANTEXTURES_PT_LINKS"
    bl_label = "Links"
    bl_parent_id = "BEANTEXTURES_PT_configs"

    def draw(self, context):
        try:
            layout = self.layout
            row = layout.row()

            settings = bpy.context.scene.beantextures_settings
            idx = settings.active_config_idx
            active_config = settings.configs[idx]

            row.template_list("BEANTEXTURES_UL_LinksListRenderer", "compact", active_config, "links", active_config, "active_link_idx")

            layout.use_property_split = True

            col = row.column(align=True)
            col.operator("beantextures.new_link", icon='ADD', text="")
            col.operator("beantextures.remove_link", icon='REMOVE', text="")

        except IndexError:
            return


def register():
    bpy.utils.register_class(BEANTEXTURES_UL_ConfigsListRenderer)
    bpy.utils.register_class(BEANTEXTURES_UL_LinksListRenderer)
    bpy.utils.register_class(NodeTreePanel)
    bpy.utils.register_class(ConfigsPanel)
    bpy.utils.register_class(LinksPanel)

def unregister():
    bpy.utils.unregister_class(BEANTEXTURES_UL_ConfigsListRenderer)
    bpy.utils.unregister_class(BEANTEXTURES_UL_LinksListRenderer)
    bpy.utils.unregister_class(NodeTreePanel)
    bpy.utils.unregister_class(ConfigsPanel)
    bpy.utils.unregister_class(LinksPanel)
