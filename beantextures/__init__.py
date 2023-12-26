import bpy
from . import children, operators, panel, ui_ops, classes

bl_info = {
    "name": "Beantextures",
    "author": "Cikitta (daringcuteseal)",
    "version": (1, 0, 0, 231204),  # X.Y.Z.yymmdd
    "blender": (3, 0, 0),
    "location": "View3D > Properties > Beantextures",
    "description": "Enhance texture-based animation workflow.",
    "doc_url": "https://github.com/BeanwareHQ/beantextures/docs",
    "tracker_url": "https://github.com/BeanwareHQ/beantextures/issues",
    "category": "Animation",
}

def register():
    panel.register()
    children.register()
    operators.register()
    ui_ops.register()
    classes.register()
    # for module in modules:
        # module.register() 


def unregister():
    panel.unregister()
    children.unregister()
    operators.unregister()
    ui_ops.unregister()
    classes.unregister()


if __name__ == "__main__":
    register()
