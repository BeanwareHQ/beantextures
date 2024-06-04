import bpy
from bpy.types import Panel

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

def register():
    bpy.utils.register_class(NodeTreePanel)

def unregister():
    bpy.utils.unregister_class(NodeTreePanel)
