"""Operators used to generate node groups."""
import bpy
from bpy.types import Operator
from beantextures.props_settings import Beantxs_ConfigEntry, Beantxs_LinkItem
from beantextures.ui_node_generator import check_warnings_int, check_warnings_enum, check_warnings_float, check_warnings_int_simple

# TODO: Organize all into common methods and for each of the linking types, override the behavior by some parameter
# because this is barely extensible right now.

def generate_int_simple_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()
    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')

    node.interface.items_tree['Value'].min_value = config.int_min
    node.interface.items_tree['Value'].max_value = config.int_max
    if config.output_alpha: 
        node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')

    group_in: bpy.types.NodeGroupInput = node.nodes.new('NodeGroupInput')
    group_in.location = (0, 0)
    group_in.name = "group_in"

    group_out: bpy.types.NodeGroupOutput = node.nodes.new('NodeGroupOutput')
    group_out.location = (1000, 0)
    group_out.name = "group_out"

    maths_reroute_node: bpy.types.NodeReroute = node.nodes.new('NodeReroute')
    maths_reroute_node.location = (group_in.location[0] + 200, group_in.location[1] - 35)

    node.links.new(group_in.outputs['Value'], maths_reroute_node.inputs[0])
    prev_mix_inputs_loc = (530, 470)
    prev_mix_nodes_loc = (1000, 0)

    for link in links:
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = link.int_simple_val - 1
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = link.int_simple_val + 1
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        if bool(link.img):
            img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
            img_node.image = link.img
            img_node.name = "img_" + link.name
            img_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 360)
            img_node.hide = True
        else:
            # FIXME: python momen
            img_node = None
            node.interface.new_socket(link.name, in_out='INPUT', socket_type='NodeSocketColor')

        mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
        mix_node.name = "mix_" + link.name
        mix_node.data_type = 'RGBA'
        mix_node.location = (prev_mix_nodes_loc[0] + 210, prev_mix_nodes_loc[1])
        mix_node.hide = True
        node.links.new(mult_node.outputs[0], mix_node.inputs[0])

        try:
            node.links.new(prev_mix_node.outputs['Result'], mix_node.inputs['A'])
        except NameError:
            pass

        prev_mix_node = mix_node


        if config.output_alpha:
            alpha_mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
            alpha_mix_node.name = "mix_alpha_" + link.name
            alpha_mix_node.hide = True
            alpha_mix_node.data_type = 'FLOAT'
            alpha_mix_node.location = (mix_node.location[0], mix_node.location[1] - 45)
            node.links.new(mult_node.outputs[0], alpha_mix_node.inputs[0])

            try:
                node.links.new(prev_alpha_mix_node.outputs['Result'], alpha_mix_node.inputs['A'])
            except NameError:
                pass

            prev_alpha_mix_node = alpha_mix_node

        if img_node is None:
            node.links.new(group_in.outputs[link.name], mix_node.inputs['B'])

            if config.output_alpha:
                node.links.new(group_in.outputs[link.name + "_alpha"], alpha_mix_node.inputs['B'])

        else:
            node.links.new(img_node.outputs['Color'], mix_node.inputs['B'])
            if config.output_alpha:
                node.interface.new_socket(link.name + "_alpha", in_out='INPUT', socket_type='NodeSocketFloat')
                node.links.new(img_node.outputs['Alpha'], alpha_mix_node.inputs['B'])


        prev_mix_nodes_loc = mix_node.location

        try:
            if link == links[0]:
                if config.fallback_img:
                    fallback_img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
                    fallback_img_node.name = "fallback_img"
                    fallback_img_node.location = (mix_node.location[0] - 350, mix_node.location[1])
                    fallback_img_node.image = config.fallback_img
                    fallback_img_node.hide = True
                    node.links.new(fallback_img_node.outputs['Color'], mix_node.inputs['A'])

                    if config.output_alpha:
                        node.links.new(fallback_img_node.outputs['Alpha'], alpha_mix_node.inputs['A'])

                else:
                    mix_node.inputs['A'].default_value = (0, 0, 0, 1)
        except NameError:
            pass

    group_out.location = (prev_mix_nodes_loc[0] + 200, prev_mix_nodes_loc[1])
    try:
        node.links.new(mix_node.outputs['Result'], group_out.inputs['Image'])
        if config.output_alpha:
            node.links.new(alpha_mix_node.outputs['Result'], group_out.inputs['Alpha'])
    except NameError:
        return

    maths_reroute_node.location = (maths_reroute_node.location[0], (prev_mix_inputs_loc[1] - 360) // 2)
    group_in.location = (group_in.location[0], (prev_mix_inputs_loc[1] - 290) // 2)

    node.interface.items_tree['Value'].default_value = config.int_min

def generate_int_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()
    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    node.interface.items_tree['Value'].min_value = config.int_min
    node.interface.items_tree['Value'].max_value = config.int_max

    if config.output_alpha: 
        node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')

    group_in: bpy.types.NodeGroupInput = node.nodes.new('NodeGroupInput')
    group_in.location = (0, 0)
    group_in.name = "group_in"

    group_out: bpy.types.NodeGroupOutput = node.nodes.new('NodeGroupOutput')
    group_out.location = (1000, 0)
    group_out.name = "group_out"

    maths_reroute_node: bpy.types.NodeReroute = node.nodes.new('NodeReroute')
    maths_reroute_node.location = (group_in.location[0] + 200, group_in.location[1] - 35)

    node.links.new(group_in.outputs['Value'], maths_reroute_node.inputs[0])
    prev_mix_inputs_loc = (530, 470)
    prev_mix_nodes_loc = (1000, 0)

    for link in links:
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = link.int_gt
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = link.int_lt
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
        img_node.image = link.img
        img_node.name = "img_" + link.name
        img_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 360)
        img_node.hide = True

        mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
        mix_node.name = "mix_" + link.name
        mix_node.data_type = 'RGBA'
        mix_node.location = (prev_mix_nodes_loc[0] + 210, prev_mix_nodes_loc[1])
        mix_node.hide = True
        node.links.new(mult_node.outputs[0], mix_node.inputs[0])
        node.links.new(img_node.outputs['Color'], mix_node.inputs['B'])
        prev_mix_nodes_loc = mix_node.location

        try:
            node.links.new(prev_mix_node.outputs['Result'], mix_node.inputs['A'])
        except NameError:
            pass

        prev_mix_node = mix_node

        if config.output_alpha:
            alpha_mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
            alpha_mix_node.name = "mix_alpha_" + link.name
            alpha_mix_node.hide = True
            alpha_mix_node.data_type = 'FLOAT'
            alpha_mix_node.location = (mix_node.location[0], mix_node.location[1] - 45)
            node.links.new(mult_node.outputs[0], alpha_mix_node.inputs[0])
            node.links.new(img_node.outputs['Alpha'], alpha_mix_node.inputs['B'])

            try:
                node.links.new(prev_alpha_mix_node.outputs['Result'], alpha_mix_node.inputs['A'])
            except NameError:
                pass

            prev_alpha_mix_node = alpha_mix_node

        try:
            if link == links[0]:
                if config.fallback_img:
                    fallback_img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
                    fallback_img_node.name = "fallback_img"
                    fallback_img_node.location = (mix_node.location[0] - 350, mix_node.location[1])
                    fallback_img_node.image = config.fallback_img
                    fallback_img_node.hide = True
                    node.links.new(fallback_img_node.outputs['Color'], mix_node.inputs['A'])

                    if config.output_alpha:
                        node.links.new(fallback_img_node.outputs['Alpha'], alpha_mix_node.inputs['A'])

                else:
                    mix_node.inputs['A'].default_value = (0, 0, 0, 1)
        except NameError:
            pass

    group_out.location = (prev_mix_nodes_loc[0] + 200, prev_mix_nodes_loc[1])
    try:
        node.links.new(mix_node.outputs['Result'], group_out.inputs['Image'])
        if config.output_alpha:
            node.links.new(alpha_mix_node.outputs['Result'], group_out.inputs['Alpha'])
    except NameError:
        return

    maths_reroute_node.location = (maths_reroute_node.location[0], (prev_mix_inputs_loc[1] - 360) // 2)
    group_in.location = (group_in.location[0], (prev_mix_inputs_loc[1] - 290) // 2)

    node.interface.items_tree['Value'].default_value = config.int_min

def generate_float_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()
    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketFloat')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    node.interface.items_tree['Value'].min_value = config.float_min
    node.interface.items_tree['Value'].max_value = config.float_max

    if config.output_alpha: 
        node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')

    group_in: bpy.types.NodeGroupInput = node.nodes.new('NodeGroupInput')
    group_in.location = (0, 0)
    group_in.name = "group_in"

    group_out: bpy.types.NodeGroupOutput = node.nodes.new('NodeGroupOutput')
    group_out.location = (1000, 0)
    group_out.name = "group_out"

    maths_reroute_node: bpy.types.NodeReroute = node.nodes.new('NodeReroute')
    maths_reroute_node.location = (group_in.location[0] + 200, group_in.location[1] - 35)

    node.links.new(group_in.outputs['Value'], maths_reroute_node.inputs[0])
    prev_mix_inputs_loc = (530, 470)
    prev_mix_nodes_loc = (1000, 0)

    for link in links:
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = link.float_gt
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = link.float_lt
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
        img_node.image = link.img
        img_node.name = "img_" + link.name
        img_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 360)
        img_node.hide = True

        mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
        mix_node.name = "mix_" + link.name
        mix_node.data_type = 'RGBA'
        mix_node.location = (prev_mix_nodes_loc[0] + 210, prev_mix_nodes_loc[1])
        mix_node.hide = True
        node.links.new(mult_node.outputs[0], mix_node.inputs[0])
        node.links.new(img_node.outputs['Color'], mix_node.inputs['B'])
        prev_mix_nodes_loc = mix_node.location

        try:
            node.links.new(prev_mix_node.outputs['Result'], mix_node.inputs['A'])
        except NameError:
            pass

        prev_mix_node = mix_node

        if config.output_alpha:
            alpha_mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
            alpha_mix_node.name = "mix_alpha_" + link.name
            alpha_mix_node.hide = True
            alpha_mix_node.data_type = 'FLOAT'
            alpha_mix_node.location = (mix_node.location[0], mix_node.location[1] - 45)
            node.links.new(mult_node.outputs[0], alpha_mix_node.inputs[0])
            node.links.new(img_node.outputs['Alpha'], alpha_mix_node.inputs['B'])

            try:
                node.links.new(prev_alpha_mix_node.outputs['Result'], alpha_mix_node.inputs['A'])
            except NameError:
                pass

            prev_alpha_mix_node = alpha_mix_node

        try:
            if link == links[0]:
                if config.fallback_img:
                    fallback_img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
                    fallback_img_node.name = "fallback_img"
                    fallback_img_node.location = (mix_node.location[0] - 350, mix_node.location[1])
                    fallback_img_node.image = config.fallback_img
                    fallback_img_node.hide = True
                    node.links.new(fallback_img_node.outputs['Color'], mix_node.inputs['A'])

                    if config.output_alpha:
                        node.links.new(fallback_img_node.outputs['Alpha'], alpha_mix_node.inputs['A'])

                else:
                    mix_node.inputs['A'].default_value = (0, 0, 0, 1)
        except NameError:
            pass

    group_out.location = (prev_mix_nodes_loc[0] + 200, prev_mix_nodes_loc[1])
    try:
        node.links.new(mix_node.outputs['Result'], group_out.inputs['Image'])
        if config.output_alpha:
            node.links.new(alpha_mix_node.outputs['Result'], group_out.inputs['Alpha'])
    except NameError:
        return

    maths_reroute_node.location = (maths_reroute_node.location[0], (prev_mix_inputs_loc[1] - 360) // 2)
    group_in.location = (group_in.location[0], (prev_mix_inputs_loc[1] - 290) // 2)
    node.interface.items_tree['Value'].default_value = config.float_min

def generate_enum_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()

    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    node.interface.items_tree['Value'].min_value = 0
    node.interface.items_tree['Value'].max_value = len(links)

    if config.output_alpha: 
        node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')

    group_in: bpy.types.NodeGroupInput = node.nodes.new('NodeGroupInput')
    group_in.location = (0, 0)
    group_in.name = "group_in"

    group_out: bpy.types.NodeGroupOutput = node.nodes.new('NodeGroupOutput')
    group_out.location = (1000, 0)
    group_out.name = "group_out"

    maths_reroute_node: bpy.types.NodeReroute = node.nodes.new('NodeReroute')
    maths_reroute_node.location = (group_in.location[0] + 200, group_in.location[1] - 35)

    node.links.new(group_in.outputs['Value'], maths_reroute_node.inputs[0])
    prev_mix_inputs_loc = (530, 470)
    prev_mix_nodes_loc = (1000, 0)

    enum_idx = 0
    for link in links:
        enum_item = node.beantextures_props.enum_items.add()
        enum_item.name = link.name
        enum_item.idx = enum_idx

        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = enum_idx - 1
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = enum_idx + 1
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath')
        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
        img_node.image = link.img
        img_node.name = "img_" + link.name
        img_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 360)
        img_node.hide = True

        mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
        mix_node.name = "mix_" + link.name
        mix_node.data_type = 'RGBA'
        mix_node.location = (prev_mix_nodes_loc[0] + 210, prev_mix_nodes_loc[1])
        mix_node.hide = True
        node.links.new(mult_node.outputs[0], mix_node.inputs[0])
        node.links.new(img_node.outputs['Color'], mix_node.inputs['B'])
        prev_mix_nodes_loc = mix_node.location

        enum_idx += 1

        try:
            node.links.new(prev_mix_node.outputs['Result'], mix_node.inputs['A'])
        except NameError:
            pass

        prev_mix_node = mix_node

        if config.output_alpha:
            alpha_mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix')
            alpha_mix_node.name = "mix_alpha_" + link.name
            alpha_mix_node.hide = True
            alpha_mix_node.data_type = 'FLOAT'
            alpha_mix_node.location = (mix_node.location[0], mix_node.location[1] - 45)
            node.links.new(mult_node.outputs[0], alpha_mix_node.inputs[0])
            node.links.new(img_node.outputs['Alpha'], alpha_mix_node.inputs['B'])

            try:
                node.links.new(prev_alpha_mix_node.outputs['Result'], alpha_mix_node.inputs['A'])
            except NameError:
                pass

            prev_alpha_mix_node = alpha_mix_node

        try:
            if link == links[0]:
                if config.fallback_img:
                    fallback_img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage')
                    fallback_img_node.name = "fallback_img"
                    fallback_img_node.location = (mix_node.location[0] - 350, mix_node.location[1])
                    fallback_img_node.image = config.fallback_img
                    fallback_img_node.hide = True
                    node.links.new(fallback_img_node.outputs['Color'], mix_node.inputs['A'])

                    if config.output_alpha:
                        node.links.new(fallback_img_node.outputs['Alpha'], alpha_mix_node.inputs['A'])

                else:
                    mix_node.inputs['A'].default_value = (0, 0, 0, 1)
        except NameError:
            pass

    group_out.location = (prev_mix_nodes_loc[0] + 200, prev_mix_nodes_loc[1])
    try:
        node.links.new(mix_node.outputs['Result'], group_out.inputs['Image'])
        if config.output_alpha:
            node.links.new(alpha_mix_node.outputs['Result'], group_out.inputs['Alpha'])
    except NameError:
        return

    maths_reroute_node.location = (maths_reroute_node.location[0], (prev_mix_inputs_loc[1] - 360) // 2)
    group_in.location = (group_in.location[0], (prev_mix_inputs_loc[1] - 290) // 2)

    node.interface.items_tree['Value'].default_value = 0

# Testing
#generate_int_simple_node_group(bpy.context, bpy.context.scene.beantextures_settings.configs[0])

class BeantxsOp_GenerateNode(Operator):
    """Generate node tree using active configuration"""
    bl_label = "Generate Node Tree"
    bl_idname = "beantextures.generate_node_tree"

    @classmethod
    def poll(cls, context):
        settings = context.scene.beantextures_settings
        config = settings.configs[settings.active_config_idx]

        if not isinstance(config.target_node_tree, bpy.types.ShaderNodeTree):
            cls.poll_message_set("Specify a shader node group as the target!")
        if not bool(config.target_node_tree):
            cls.poll_message_set("Set a valid shader node group as a target first!")
        return bool(config.target_node_tree) and isinstance(config.target_node_tree, bpy.types.ShaderNodeTree)

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.label(icon='INFO', text="Checking validity of links..")

        settings = context.scene.beantextures_settings
        config = settings.configs[settings.active_config_idx]
        errors: dict[str, list[str]] = {} # {location: ["error1", "error2"], ...}

        match config.linking_type:
            # FIXME: python momen
            case 'INT_SIMPLE':
                warning_checker = check_warnings_int_simple
            case 'INT':
                warning_checker = check_warnings_int
            case 'FLOAT':
                warning_checker = check_warnings_float
            case 'ENUM':
                warning_checker = check_warnings_enum
            case _:
                warning_checker = check_warnings_int_simple

        if len(config.links) == 0:
            # TODO: if more config checking is needed, consider making a separate function that
            # does something similar to check_warnings_<type>
            errors.update({'Config': ["There is no link available."]})
        for link in config.links:
            errors.update({link.name: warning_checker(context, link, config)})

        err_detected = False
        for err_key in errors.keys():
            if len(errors[err_key]) == 0:
                continue
            err_detected = True
            box = layout.box()
            box.label(text=f"On link '{err_key}':")
            for err_msg in errors[err_key]:
                box.label(icon='DOT', text=err_msg)

        if err_detected:
            column.label(icon='ERROR', text="Some warnings found; hit OK to proceed anyways.")
        else:
            column.label(icon='CHECKMARK', text="No warnings found; hit OK to proceed.")

        
    def execute(self, context):
        settings = context.scene.beantextures_settings
        config = settings.configs[settings.active_config_idx]
        match config.linking_type:
            case 'INT_SIMPLE':
                generate_int_simple_node_group(context, config)
            case 'INT':
                generate_int_node_group(context, config)
            case 'FLOAT':
                generate_float_node_group(context, config)
            case 'ENUM':
                generate_enum_node_group(context, config)

        self.report({'INFO'}, f"Generated tree for node group '{config.name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    

def register():
    bpy.utils.register_class(BeantxsOp_GenerateNode)

def unregister():
    bpy.utils.unregister_class(BeantxsOp_GenerateNode)
