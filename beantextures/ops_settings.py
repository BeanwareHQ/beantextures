import bpy
from bpy.types import Operator

class BeantxsOp_NewNodeTree(Operator):
    """Add a new shader node tree"""
    bl_label = "Add new node tree"
    bl_idname = "beantextures.new_node_tree"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # too short so no wrapper function.
        name = bpy.context.scene.beantextures_settings.node_tree_adder_name
        obj = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        # obj.name is used to get the real unique name (`name` may already exist)
        self.report({'INFO'}, f"Added node tree '{obj.name}'")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BeantxsOp_NewNodeTree) 

def unregister():
    bpy.utils.unregister_class(BeantxsOp_NewNodeTree)
