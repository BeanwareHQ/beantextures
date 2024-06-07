"""Operators used to generate node groups."""
import bpy
from bpy.types import NodeTree
from beantextures.props_settings import Beantxs_ConfigEntry, Beantxs_LinkItem

def generate_int_simple_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()
    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
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

def generate_int_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()
    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
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

def generate_float_node_group(context, config: Beantxs_ConfigEntry):
    links: list[Beantxs_LinkItem] = config.links # wrong type but it works and I need autocompletion

    node: bpy.types.NodeTree = config.target_node_tree
    node.nodes.clear()
    node.interface.clear()
    node.is_beantextures = True # type: ignore

    node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketFloat')
    node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
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

# Testing
generate_int_simple_node_group(bpy.context, bpy.context.scene.beantextures_settings.configs[0])
