"""Operators related to the node generator settings."""

import bpy
from bpy.types import Operator
from bpy_extras import image_utils
from beantextures.props_settings import Btxs_LinkItem, Btxs_ConfigEntry

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

def add_new_link(context) -> Btxs_LinkItem:
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
    
    link.int_simple_val = proper_idx + 1
    link.int_gt = proper_idx
    link.int_lt = proper_idx + 2
    link.float_gt = proper_idx + 1
    link.float_lt = proper_idx + 2.1

    config.active_link_idx = proper_idx

    return link

def remove_link(context, idx: int):
    settings = context.scene.beantextures_settings
    config_idx = settings.active_config_idx
    config = settings.configs[config_idx]

    if config.active_link_idx == len(config.links) - 1:
        config.active_link_idx -= 1

    config.links.remove(idx)

def auto_import_images(context, directory: bpy.types.StringProperty, files: bpy.types.CollectionProperty, prefix: bpy.types.StringProperty, suffix: bpy.types.StringProperty):
    for file_name in sorted(files.keys()):
        if len(file_name) > 0:
            link = add_new_link(context)
            link.img = image_utils.load_image(directory + file_name)
            link.name = str(prefix) + bpy.path.display_name_from_filepath(file_name) + str(suffix)

def import_image(link: Btxs_LinkItem, directory: bpy.types.StringProperty, file: bpy.types.OperatorFileListElement):
    link.img = image_utils.load_image(directory + file.name) # type: ignore

def purge_image(context, img: bpy.types.Image):
    """Purge image if image has no user"""

    if img and img.users == 0:
        context.blend_data.images.remove(img)

def delete_all_links(context, config: Btxs_ConfigEntry, purge_images: bool):
    for _ in range(0, len(config.links)):
        img = config.links[0].img
        config.links.remove(0)
        if purge_images:
            purge_image(context, img) 

# Operator Classes

class BtxsOp_NewNodeGroup(Operator):
    """Add a new shader node group"""
    bl_label = "Add New Node Group"
    bl_idname = "beantextures.new_node_group"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # too short so no wrapper function.
        name = context.scene.beantextures_settings.node_group_adder_name
        obj = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        # obj.name is used to get the real unique name (`name` may already exist)
        self.report({'INFO'}, f"Added node group '{obj.name}'")
        return {'FINISHED'}

class BtxsOp_NewConfig(Operator):
    """Add a new configuration entry"""
    bl_label = "Add Configuration"
    bl_idname = "beantextures.new_config"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        add_new_config(context, "New Config")
        return {'FINISHED'}

class BtxsOp_RemoveSelectedConfig(Operator):
    """Remove selected configuration"""
    bl_label = "Remove Configuration"
    bl_idname = "beantextures.remove_config"

    @classmethod
    def poll(cls, context):
        return (len(context.scene.beantextures_settings.configs) > 0)

    def execute(self, context):
        idx = context.scene.beantextures_settings.active_config_idx
        remove_config(context, idx)
        return {'FINISHED'}

class BtxsOp_RemoveAllConfigs(Operator):
    """Remove all configurations"""
    bl_label = "Clear Configurations"
    bl_idname = "beantextures.remove_all_configs"

    @classmethod
    def poll(cls, context):
        return (len(context.scene.beantextures_settings.configs) > 0)

    def execute(self, context):
        settings = context.scene.beantextures_settings
        settings.configs.clear()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.column().label(text="Delete all configurations?")

    def invoke(self, context, event):
        wm = context.window_manager
        bpy.context.area.tag_redraw()
        return wm.invoke_props_dialog(self)

class BtxsOp_NewLink(Operator):
    """Add a new link to the active configuration"""
    bl_label = "New Link"
    bl_idname = "beantextures.new_link"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        add_new_link(context)
        return {'FINISHED'}

class BtxsOp_RemoveLink(Operator):
    """Remove selected link from the active configuration"""
    bl_label = "Remove Link"
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

class BtxsOp_AutoImportImages(Operator):
    """Automatically import image(s) as link(s)"""
    bl_label = "Import Image(s)"
    bl_idname = "beantextures.auto_import_images"

    filter_image: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_folder: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    name_prefix: bpy.props.StringProperty(name="Naming Prefix", description="Extra prefix which will be added to relation names")
    name_suffix: bpy.props.StringProperty(name="Naming Suffix", description="Extra suffix which will be added to relation names")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        auto_import_images(context, self.directory, self.files, self.name_prefix, self.name_suffix)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BtxsOp_OpenImage(Operator):
    """Import image to link"""
    bl_label = "Pick Image"
    bl_idname = "beantextures.import_image"

    filter_image: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_folder: bpy.props.BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.beantextures_settings
        config = settings.configs[settings.active_config_idx]
        link = config.links[config.active_link_idx]
        import_image(link, self.directory, self.files[0])
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BtxsOp_ClearLinks(Operator):
    """Clear all links from active configuration"""
    bl_label = "Clear Defined Links"
    bl_idname = "beantextures.clear_links"

    remove_data_blocks: bpy.props.BoolProperty(default=True, name="Remove Data-Blocks", description="Also purge image data-blocks (if they have no users left)")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        settings = context.scene.beantextures_settings
        config = settings.configs[settings.active_config_idx]

        delete_all_links(context, config, self.remove_data_blocks)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Delete all relations?")
        col.prop(self, "remove_data_blocks")

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class BtxsOp_InitializeEnum(Operator):
    """Initialize driver for an enum Beantextures node"""
    bl_label = "Add Driver"
    bl_idname = "beantextures.init_enum_driver"

    @classmethod
    def poll(cls, context) -> bool:
        return ((context.area.type == 'NODE_EDITOR') and hasattr(context, "active_node") and hasattr(context, "material"))

    def execute(self, context):
        node = context.active_node
        material = context.material
        driver = node.inputs['Value'].driver_remove("default_value")
        driver = node.inputs['Value'].driver_add("default_value")
        driver.driver.type = 'AVERAGE'

        var = driver.driver.variables.new()
        var.name = "enum_item"
        var.targets[0].id_type = 'MATERIAL'
        var.targets[0].id = material
        var.targets[0].data_path = f"node_tree.nodes[\"{node.name}\"].beantxs_enum_prop"

        return {'FINISHED'}

def register():
    bpy.utils.register_class(BtxsOp_NewNodeGroup) 
    bpy.utils.register_class(BtxsOp_NewConfig) 
    bpy.utils.register_class(BtxsOp_NewLink) 
    bpy.utils.register_class(BtxsOp_RemoveLink) 
    bpy.utils.register_class(BtxsOp_RemoveSelectedConfig) 
    bpy.utils.register_class(BtxsOp_RemoveAllConfigs) 
    bpy.utils.register_class(BtxsOp_AutoImportImages) 
    bpy.utils.register_class(BtxsOp_OpenImage) 
    bpy.utils.register_class(BtxsOp_ClearLinks) 
    bpy.utils.register_class(BtxsOp_InitializeEnum) 

def unregister():
    bpy.utils.unregister_class(BtxsOp_NewNodeGroup)
    bpy.utils.unregister_class(BtxsOp_NewConfig) 
    bpy.utils.unregister_class(BtxsOp_NewLink) 
    bpy.utils.unregister_class(BtxsOp_RemoveLink) 
    bpy.utils.unregister_class(BtxsOp_RemoveSelectedConfig) 
    bpy.utils.unregister_class(BtxsOp_RemoveAllConfigs) 
    bpy.utils.unregister_class(BtxsOp_AutoImportImages) 
    bpy.utils.unregister_class(BtxsOp_OpenImage) 
    bpy.utils.unregister_class(BtxsOp_ClearLinks) 
    bpy.utils.unregister_class(BtxsOp_InitializeEnum) 
