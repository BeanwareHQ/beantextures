"""View3D panel definition."""
import bpy
from .popup_menu import list_draw

class BeantexturesView3DPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Beantextures"
    bl_label = "Nodes Controls"
    bl_idname = "BEANTEXTURES_PT_view3d_panel"

    @classmethod
    def poll(cls, context):
        return bool(context.active_bone and context.mode == 'POSE')

    def draw(self, context):
        list_draw(self, context, self.layout, label=False)


def register():
    bpy.utils.register_class(BeantexturesView3DPanel)

def unregister():
    bpy.utils.unregister_class(BeantexturesView3DPanel)
