import bpy

bpy.context.object['beantextures_children'] = [
    {
        "name": "child1",
        "texture": bpy.types.Image,
        "variants": [
            {
            "name": "variant1",
            "uv_map": bpy.types.Mesh.uv_layers,
            }
        ],
            
    }
]
