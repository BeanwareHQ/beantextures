"""User interface for the node generator."""
import bpy
from bpy.types import Panel, UIList
from beantextures.ops_settings import BtxsOp_ClearLinks, BtxsOp_NewNodeGroup, BtxsOp_InitializeEnum, BtxsOp_OpenImage, BtxsOp_NewLink, BtxsOp_RemoveLink, BtxsOp_RemoveAllConfigs
from beantextures.props_settings import Btxs_LinkItem, Btxs_ConfigEntry

# Helper functions

def search_for_duplicate_int_simple_link_value(context, link) -> tuple[bool, str]:
    """Check if link value had been used by other link(s). Returns `(True, <name>)` if duplicate is found, where `name` is the name of the first matched link. Otherwise, returns `(False, 0)`."""
    settings = context.scene.beantextures_settings
    config = settings.configs[settings.active_config_idx]
    for check_link in config.links:
        if check_link == link:
            continue
        if check_link.int_simple_val == link.int_simple_val:
            return (True, check_link.name)
    return (False, "")

def search_for_duplicate_int_link_value(context, link) -> tuple[bool, str]:
    """Check if link range value overlaps other link(s). Returns `(True, <name>)` if duplicate is found, where `name` is the name of the first matched link. Otherwise, returns `(False, 0)`."""
    settings = context.scene.beantextures_settings
    config = settings.configs[settings.active_config_idx]
    for check_link in config.links:
        if check_link == link:
            continue
        if link.int_gt >= check_link.int_gt and link.int_lt <= check_link.int_lt:
            return (True, check_link.name)
    return (False, "")

def search_for_duplicate_float_link_value(context, link) -> tuple[bool, str]:
    """Check if link range value overlaps other link(s). Returns `(True, <name>)` if duplicate is found, where `name` is the name of the first matched link. Otherwise, returns `(False, 0)`."""
    settings = context.scene.beantextures_settings
    config = settings.configs[settings.active_config_idx]
    for check_link in config.links:
        if check_link == link:
            continue
        if link.float_gt >= check_link.float_gt and link.float_lt <= check_link.float_lt:
            return (True, check_link.name)
    return (False, "")

def search_for_duplicate_enum_name(context, link) -> bool:
    """Check if another link with the same name already exists."""
    settings = context.scene.beantextures_settings
    config = settings.configs[settings.active_config_idx]
    for check_link in config.links:
        if check_link == link:
            continue
        if link.name == check_link.name:
            return True
    return False

# Warning checkers

def check_warnings_int_simple(context, link: Btxs_LinkItem, config: Btxs_ConfigEntry) -> list[str]:
    warnings: list[str] = []
    if (search_result := search_for_duplicate_int_simple_link_value(context, link))[0]:
        warnings.append(f"Index has been used by link '{search_result[1]}'.")

    if link.int_simple_val > config.int_max or link.int_simple_val < config.int_min:
        warnings.append(f"Bound number is out of the set max/min range.")

    if search_for_duplicate_enum_name(context, link):
        warnings.append("Link with similar name already exists.")

    return warnings

def check_warnings_int(context, link: Btxs_LinkItem, config: Btxs_ConfigEntry) -> list[str]:
    warnings: list[str] = []
    if (search_result := search_for_duplicate_int_link_value(context, link))[0]:
        warnings.append(f"Range overlaps with link '{search_result[1]}'.")

    if link.int_lt < link.int_gt:
        warnings.append("The assigned greater than digit is bigger than its less than!")

    if link.int_lt > config.int_max + 1 or link.int_gt < config.int_min - 1:
        warnings.append("Range is out of the set max/min range!")

    if search_for_duplicate_enum_name(context, link):
        warnings.append("Link with similar name already exists.")

    return warnings

def check_warnings_float(context, link: Btxs_LinkItem, config: Btxs_ConfigEntry) -> list[str]:
    warnings: list[str] = []
    if (search_result := search_for_duplicate_float_link_value(context, link))[0]:
        warnings.append(f"Range overlaps with link '{search_result[1]}'.")

    if link.float_lt < link.float_gt:
        warnings.append("Range is invalid!")

    if link.float_lt > config.float_max or link.float_gt < config.float_min:
        warnings.append("Range is out of the set max/min range.")

    if search_for_duplicate_enum_name(context, link):
        warnings.append("Link with similar name already exists.")

    return warnings

def check_warnings_enum(context, link: Btxs_LinkItem, config: Btxs_ConfigEntry) -> list[str]:
    warnings: list[str] = []

    if search_for_duplicate_enum_name(context, link):
        warnings.append("Link with similar name already exists.")

    return warnings

# Panel definitions

class BeantexturesNodePanel(Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Beantextures"

    @classmethod
    def poll(cls, context):
        return True

class NodeTreePanel(BeantexturesNodePanel):
    bl_idname = "BEANTEXTURES_PT_node_tree_adder"
    bl_label = "Node Group"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.row().prop(bpy.context.scene.beantextures_settings, "node_group_adder_name")
        layout.row().operator(BtxsOp_NewNodeGroup.bl_idname, text="Add", icon='PLUS')

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
        col.separator()
        col.operator("beantextures.remove_all_configs", icon='X', text="")

        try:
            idx = settings.active_config_idx
            item = settings.configs[idx]

            col = layout.column()
            col.prop(item, "linking_type", text="Linking Type")
            col.prop(item, "target_node_tree", text="Target Node Group")
            col.prop(item, "fallback_img", text="Fallback Image")
            col.prop(item, "output_alpha", text="Output Alpha")

            match item.linking_type:
                case 'INT_SIMPLE':
                    range_col = col.row()
                    range_col.prop(item, "int_min", text="Min")
                    range_col.prop(item, "int_max", text="Max")
                case 'INT':
                    range_col = col.row()
                    range_col.prop(item, "int_min", text="Min")
                    range_col.prop(item, "int_max", text="Max")
                case 'FLOAT': 
                    range_col = col.row()
                    range_col.prop(item, "float_min", text="Min")
                    range_col.prop(item, "float_max", text="Max")
                case 'ENUM':
                    pass

            col.separator()
            if item.target_node_tree is not None and item.target_node_tree.is_beantextures:
                col.operator("beantextures.generate_node_tree", text="Re-generate Node Tree", icon='FILE_REFRESH')
            else:
                col.operator("beantextures.generate_node_tree", text="Generate Node Tree", icon='NODETREE')

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
    bl_idname = "BEANTEXTURES_PT_links"
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
            col.operator(BtxsOp_NewLink.bl_idname, icon='ADD', text="")
            col.operator(BtxsOp_RemoveLink.bl_idname, icon='REMOVE', text="")
            col.separator()
            col.operator(BtxsOp_RemoveAllConfigs.bl_idname, icon='X', text="")
            col.operator(BtxsOp_ClearLinks.bl_idname, icon='FILE_FOLDER', text="")

            layout.use_property_split = True
            col = layout.column()
            link_idx = active_config.active_link_idx
            active_link = active_config.links[link_idx]

            match active_config.linking_type:
                case 'INT_SIMPLE':
                    if (warnings := check_warnings_int_simple(context, active_link, active_config)):
                        for msg in warnings:
                            col.label(text="Warning: " + msg, icon='ERROR')
                        col.separator()

                    col.prop(active_link, "int_simple_val", text="Bind to")

                case 'INT':
                    if (warnings := check_warnings_int(context, active_link, active_config)):
                        for msg in warnings:
                            col.label(text="Warning: " + msg, icon='ERROR')
                        col.separator()

                    col.prop(active_link, "int_gt", text="Greater Than")
                    col.prop(active_link, "int_lt", text="Less Than")

                case 'FLOAT':
                    if (warnings := check_warnings_float(context, active_link, active_config)):
                        for msg in warnings:
                            col.label(text="Warning: " + msg, icon='ERROR')
                        col.separator()

                    col.prop(active_link, "float_gt", text="Greater Than")
                    col.prop(active_link, "float_lt", text="Less Than")

                case 'ENUM':
                    if (warnings := check_warnings_enum(context, active_link, active_config)):
                        for msg in warnings:
                            col.label(text="Warning: " + msg, icon='ERROR')
                        col.separator()

                case _:
                    return
                    
            row = col.row()
            row.prop(active_link, "img", text="Image")
            row.operator(BtxsOp_OpenImage.bl_idname, text="", icon='FILE_FOLDER')

        except IndexError:
            return

class InspectorPanel(BeantexturesNodePanel):
    bl_idname = "BEANTEXTURES_PT_inspector"
    bl_label = "Inspector"

    @classmethod
    def poll(cls, context):
        return ((context.area.type == 'NODE_EDITOR') and isinstance(context.active_node, bpy.types.ShaderNode))

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        col = layout.column()

        node = context.active_node
        col.prop(node, "name", text=f"Active node", icon='NODE')

        if not (isinstance(node, bpy.types.ShaderNodeGroup) and hasattr(node.node_tree, "beantextures_props") and hasattr(node.node_tree.beantextures_props, "link_type")):
            layout.label(text="Not a Beantextures node.", icon='INFO')
            return

        # TODO: maybe use a more descriptive name
        col.label(text=f"Linking type: {node.node_tree.beantextures_props.link_type}")

        if node.node_tree.beantextures_props.link_type == 'ENUM':
            col.prop(node, "beantxs_enum_prop", text="Enum selection")
            col.separator()
            col.operator(BtxsOp_InitializeEnum.bl_idname, text="Add Driver", icon='DRIVER')

def register():
    bpy.utils.register_class(BEANTEXTURES_UL_ConfigsListRenderer)
    bpy.utils.register_class(BEANTEXTURES_UL_LinksListRenderer)
    bpy.utils.register_class(NodeTreePanel)
    bpy.utils.register_class(ConfigsPanel)
    bpy.utils.register_class(LinksPanel)
    bpy.utils.register_class(InspectorPanel)

def unregister():
    bpy.utils.unregister_class(BEANTEXTURES_UL_ConfigsListRenderer)
    bpy.utils.unregister_class(BEANTEXTURES_UL_LinksListRenderer)
    bpy.utils.unregister_class(NodeTreePanel)
    bpy.utils.unregister_class(ConfigsPanel)
    bpy.utils.unregister_class(LinksPanel)
    bpy.utils.unregister_class(InspectorPanel)
