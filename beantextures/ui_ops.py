"""
Operators directly shown on Beantextures panel.
"""

from typing import Set
import bpy
import beantextures.operators as operators
from bpy.types import Context, Event

class BT_UI_MakeController(bpy.types.Operator):
    """Turn selected object into a Beantextures controller."""

    bl_idname = "beantextures.ui_make_controller"
    bl_label = "Make Controller"

    @classmethod
    def poll(cls, context: Context):
        return context.active_object is not None

    def execute(self, context: Context) -> Set[str] | Set[str]:
        bpy.ops.beantextures.make_controller() #type:ignore
        return {'FINISHED'}

class BT_UI_AddChild(bpy.types.Operator):
    """Add a new child object to Beantextures controller."""

    bl_idname = "beantextures.ui_add_child"
    bl_label = "Add Child"

    @classmethod
    def poll(cls, context: Context):
        return context.active_object is not None
    
    def execute(self, context: Context) -> Set[str] | Set[int]:
        bpy.ops.beantextures.add_child() # type:ignore
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str] | Set[int]:
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


def register():
    bpy.utils.register_class(BT_UI_MakeController)
    bpy.utils.register_class(BT_UI_AddChild)

def unregister():
    bpy.utils.unregister_class(BT_UI_MakeController)
    bpy.utils.unregister_class(BT_UI_AddChild)