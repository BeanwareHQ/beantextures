from typing import Set
import bpy
from bpy.types import Context, Event

class BTChild():
    bt_object: bpy.props.StringProperty() # type: ignore

    def __init__(self, bt_object):
        self.bt_object = bt_object

class BTMakeController(bpy.types.Operator):
    bl_idname = "beantextures.make_controller"
    bl_label = "Make Controller"

    @classmethod
    def poll(cls, context: Context):
        if "is_beantextures_controller" in context.object:
            return not context.object['is_beantextures_controller']
        else:
            return True

    def execute(self, context: Context):
        context.object['is_beantextures_controller'] = True
        return {'FINISHED'}

class BTAddChild(bpy.types.Operator):
    bl_idname = "beantextures.add_child"
    bl_label = "Add Child"

    child_name: bpy.props.StringProperty(name="Child name") # type: ignore
    children_modes = [
        ("INDEX", "Index", "Display an index slider"),
        ("DROPDOWN", "Dropdown", "Display a dropdown")
    ]
    children_mode: bpy.props.EnumProperty( # type:ignore
        name="children_modes",
        items=children_modes, # type:ignore
        default="INDEX",
        description="Mode used to display variant selection" 
        )

    @classmethod
    def poll(cls, context: Context):
        return context.object["is_beantextures_controller"] == True if "is_beantextures_controller" in context.object else False
    
    def execute(self, context: Context) -> Set[str] | Set[int]:
        children = context.object.beantextures_data.children.add() # type:ignore
        children.name = self.child_name
        children.mode = self.children_mode
        children.texture = context.object.beantextures_data.tmp_picker.img # type: ignore
        # if "beantexture_children" in context.object:
            # pass
        # else:
            # tmp_img = bpy.types.PointerProperty()
            # tmp_img = bpy.props.PointerProperty(type=bpy.types.Image, name="image")
        return {'FINISHED'}

    def draw(self, context: Context):
        layout = self.layout
        layout.label(text="WHAT")
        layout.prop(context.object, "beantextures_data.tmp_picker.object_selection") # type: ignore

    def invoke(self, context: Context, event: Event) -> Set[str] | Set[int]:
        wm = context.window_manager
        return wm.invoke_props_popup(self, event)


def register():
    bpy.utils.register_class(BTMakeController)
    bpy.utils.register_class(BTAddChild)

def unregister():
    bpy.utils.unregister_class(BTMakeController)
    bpy.utils.unregister_class(BTAddChild)