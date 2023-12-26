import bpy

class VIEW3D_PT_beantextures_controller_panel(bpy.types.Panel):
    bl_label = "Controller Settings"
    # bl_idname = "bean_textures.main_handler"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Beantextures"

    # bpy.types.Scene.create_controller_btn = self.layout.button
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        if bpy.ops.beantextures.make_controller.poll(): # type: ignore
            layout.operator("beantextures.ui_make_controller", text="Make Controller", icon="ADD")
        if bpy.ops.beantextures.add_child.poll(): # type:ignore
            layout.operator("beantextures.ui_add_child", text="Add Child", icon="MESH_CUBE")

class VIEW3D_PT_beantextures_children_panel(bpy.types.Panel):
    bl_label = ""
def register():
    bpy.utils.register_class(VIEW3D_PT_beantextures_controller_panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_beantextures_controller_panel)