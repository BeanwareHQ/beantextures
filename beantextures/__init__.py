bl_info = {
    "name": "Beantextures",
    "author": "Cikitta Tjok (daringcuteseal)",
    "version": (1, 0, 0, 240604),
    "blender": (4, 1, 1),
    "location": "Node editor sidebar",
    "description": "Enhance texture-based animation workflow.",
    "doc_url": "https://github.com/BeanwareHQ/beantextures/docs",
    "tracker_url": "https://github.com/BeanwareHQ/beantextures/issues",
    "category": "Animation",
}

from importlib import reload

if "bpy" in locals():
    reload(ops_settings)
    reload(props_nodes)
    reload(props_settings)
    reload(ui_node_generator)

else:
    from . import ops_settings, props_nodes, props_settings, ui_node_generator


def register():
    ops_settings.register()
    props_nodes.register()
    props_settings.register()
    ui_node_generator.register()

def unregister():
    ops_settings.unregister()
    props_nodes.unregister()
    props_settings.unregister()
    ui_node_generator.unregister()

if __name__ == "__main__":
    register()
