import bpy

class BeantexturesChildrenVariant(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="children_variant_name") # type:ignore
    uv_map: bpy.props.StringProperty(name="uv_map_name") # type:ignore

class BeantexturesChildren(bpy.types.PropertyGroup):
    children_modes = [
        ("INDEX", "Index", "Display an index slider"),
        ("DROPDOWN", "Dropdown", "Display a dropdown")
    ]
    mode: bpy.props.EnumProperty( # type:ignore
        name="children_modes",
        items=children_modes, # type:ignore
        default="INDEX",
        description="Mode used to display variant selection" 
        )

    name: bpy.props.StringProperty(name="children_name") # type:ignore
    texture: bpy.props.PointerProperty(type=bpy.types.Image, name="children_texture") # type:ignore
    variants: bpy.props.CollectionProperty(type=BeantexturesChildrenVariant) # type:ignore

class BeantexturesTmpSelection(bpy.types.PropertyGroup):
    object_selection: bpy.props.PointerProperty(type=bpy.types.Object, name="tmp_object_selection") # type:ignore
    img: bpy.props.PointerProperty(type=bpy.types.Image, name="tmp_img") # type:ignore
    uv_map: bpy.props.StringProperty(name="tmp_uv_map") # type:ignore

class BeantexturesData(bpy.types.PropertyGroup):
    children: bpy.props.CollectionProperty(type=BeantexturesChildren) # type:ignore
    tmp_picker: bpy.props.PointerProperty(type=BeantexturesTmpSelection) #type: ignore

    def __init__(self):
        self.children = bpy.props.CollectionProperty(type=BeantexturesChildren)
        self.tmp_picker = None

def register():
    bpy.utils.register_class(BeantexturesChildrenVariant)
    bpy.utils.register_class(BeantexturesChildren)
    bpy.utils.register_class(BeantexturesTmpSelection)
    bpy.utils.register_class(BeantexturesData)
    bpy.types.Object.beantextures_data = bpy.props.PointerProperty(type=BeantexturesData) # type:ignore

def unregister():
    bpy.utils.unregister_class(BeantexturesChildrenVariant)
    bpy.utils.unregister_class(BeantexturesChildren)
    bpy.utils.unregister_class(BeantexturesTmpSelection)
    bpy.utils.unregister_class(BeantexturesData)
