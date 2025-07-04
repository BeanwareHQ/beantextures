bl_info = {
    "name": "Beantextures",
    "author": "Cikitta Tjok (daringcuteseal)",
    "version": (1, 0, 2, 250628),
    "blender": (4, 0, 0),
    "location": "Node editor sidebar and bone properties",
    "description": "Enhance image texture-based animation workflow.",
    "doc_url": "https://github.com/BeanwareHQ/beantextures/wiki",
    "tracker_url": "https://github.com/BeanwareHQ/beantextures/issues",
    "category": "Animation",
    "support": "COMMUNITY",
    "extension": {
        "id": "beantextures",
        "type": "add-on",
        "version": "1.0.2",
        "schema_version": 1,
    }
}

from importlib import reload

if "bpy" in locals():
    reload(ops_settings)
    reload(props_nodes)
    reload(props_settings)
    reload(ui_node_generator)
    reload(ops_generation)

else:
    from . import ops_settings, props_nodes, props_settings, ui_node_generator, ops_generation
    from .connector import props, ui, ops, icon_picker, popup_menu, panel

def register():
    ops_settings.register()
    props_nodes.register()
    props_settings.register()
    ui_node_generator.register()
    ops_generation.register()

    props.register()
    ui.register()
    ops.register()
    icon_picker.register()
    popup_menu.register()
    panel.register()

def unregister():
    ops_settings.unregister()
    props_nodes.unregister()
    props_settings.unregister()
    ui_node_generator.unregister()
    ops_generation.unregister()

    props.unregister()
    ui.unregister()
    ops.unregister()
    icon_picker.unregister()
    popup_menu.unregister()
    panel.unregister()


if __name__ == "__main__":
    register()
