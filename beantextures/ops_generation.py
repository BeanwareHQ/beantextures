"""Operators used to generate node groups."""
import bpy
from bpy.types import Image, Operator, NodeTree, NodeGroupInput, NodeGroupOutput, NodeReroute, ShaderNodeMath, ShaderNodeTexImage, ShaderNodeMix
from .props_settings import Btxs_ConfigEntry, Btxs_LinkItem
from .ui_node_generator import check_warnings_int, check_warnings_enum, check_warnings_float, check_warnings_int_simple

class BtxsNodeTreeBuilder:
    """Base class for node tree builder. Link type-specific builders should derive this class and override some of the methods here as needed."""
    prev_mix_inputs_loc = (530, 470)
    prev_mix_nodes_loc = (1000, 0)

    def __init__(self, config: Btxs_ConfigEntry):
        self.generate(config)

    def generate(self, config: Btxs_ConfigEntry):
        """Steps of building the node tree (abstracted)."""
        prev_mix_color_node: ShaderNodeMix | None = None # FIXME: python momen
        prev_mix_alpha_node: ShaderNodeMix | None = None # FIXME: python momen
        curr_mix_color_node = None
        curr_mix_alpha_node = None

        node = self.init_node_tree(config)
        self.add_io_sockets(config, node)
        self.delete_redundant_sockets(node)
        group_in, group_out = self.add_io_nodes(node)
        rerouter = self.add_maths_rerouter(node, group_in)

        # Loop through all links
        for link in config.links:
            gt_node, lt_node, mult_node, self.prev_mix_inputs_loc = self.LINKLOOP_add_math_nodes(link, node, rerouter, self.prev_mix_inputs_loc)

            curr_mix_color_node, self.prev_mix_nodes_loc = self.LINKLOOP_add_mix_color_node(link, node, mult_node, self.prev_mix_nodes_loc)
            self.LINKLOOP_connect_previous_mix_color_node(node, curr_mix_color_node, prev_mix_color_node)

            if config.output_alpha:
                curr_mix_alpha_node = self.LINKLOOP_add_mix_alpha_node(link, node, curr_mix_color_node, mult_node)
                self.LINKLOOP_connect_previous_mix_alpha_node(node, curr_mix_alpha_node, prev_mix_alpha_node)

            img_node: None | ShaderNodeTexImage = None

            if link.img is None:
                self.LINKLOOP_add_color_input_socket(link, node) 
                self.LINKLOOP_connect_color_input_socket(link, node, group_in, curr_mix_color_node)

                if config.output_alpha:
                    # HACK: ↓ possibly unbound, but is guaranteed to be set if config.output_alpha is set to True
                    self.LINKLOOP_add_alpha_input_socket(node, link)
                    self.LINKLOOP_connect_alpha_input_socket(link, node, group_in, curr_mix_alpha_node)
            else:
                img_node, self.prev_mix_inputs_loc = self.LINKLOOP_add_img(link, node, self.prev_mix_inputs_loc)
                self.LINKLOOP_connect_image_to_mix_node(node, img_node, curr_mix_color_node)

                if config.output_alpha:
                    # HACK: ↓ possibly unbound, but is guaranteed to be set if config.output_alpha is set to True
                    self.LINKLOOP_connect_image_alpha_to_mix_node(node, img_node, curr_mix_alpha_node) 

            if link == config.links[0]:
                if config.fallback_img is None:
                    self.LINKLOOP_set_falback_color(curr_mix_color_node)
                    if config.output_alpha:
                        # HACK: ↓ possibly unbound, but is guaranteed to be set if config.output_alpha is set to True
                        self.LINKLOOP_set_fallback_alpha(curr_mix_alpha_node)
                else:
                    fallback_img_node = self.LINKLOOP_set_fallback_image(node, config.fallback_img, curr_mix_color_node)

                    if config.output_alpha:
                        # HACK: ↓ possibly unbound, but is guaranteed to be set if config.output_alpha is set to True
                        self.LINKLOOP_set_fallback_image_alpha(node, fallback_img_node, curr_mix_alpha_node)

            prev_mix_color_node = curr_mix_color_node
            if config.output_alpha:
                prev_mix_alpha_node = curr_mix_alpha_node

        self.connect_last_mix_color_nodes(node, group_out, curr_mix_color_node, self.prev_mix_nodes_loc)
        if config.output_alpha:
            self.connect_last_alpha_mix_node(node, group_out, curr_mix_alpha_node)

        self.adjust_final_node_locations(group_in, rerouter)
        self.setup_node_tree_attributes(config, node)

    def adjust_final_node_locations(self, group_in, rerouter):
        rerouter.location = (rerouter.location[0], (self.prev_mix_inputs_loc[1] - 360) // 2)
        group_in.location = (group_in.location[0], (self.prev_mix_inputs_loc[1] - 290) // 2)

    def init_node_tree(self, config) -> NodeTree:
        """Clear node tree and mark it as a Beantextures-generated node tree."""
        node: NodeTree = config.target_node_tree
        node.nodes.clear()
        node.is_beantextures = True # type: ignore
        node.beantextures_props.link_type = config.linking_type
        return node

    def add_io_sockets(self, config, node: NodeTree):
        """Add the base input and output sockets for the node tree. Only adds the sockets when they don't exist already, so that the user doesn't have to reconnect nodes themselves."""
        if not 'Value' in node.interface.items_tree:
            node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
        elif not isinstance(node.interface.items_tree['Value'], bpy.types.NodeSocketInt):
            node.interface.remove(node.interface.items_tree['Value'])
            node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')

        if not 'Image' in node.interface.items_tree:
            node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')

        node.interface.items_tree['Value'].min_value = config.int_min # type: ignore
        node.interface.items_tree['Value'].max_value = config.int_max # type: ignore

        if config.output_alpha:
            if not 'Alpha' in node.interface.items_tree: 
                node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        elif 'Alpha' in node.interface.items_tree:
            node.interface.remove(node.interface.items_tree['Alpha'])

    def delete_redundant_sockets(self, node: NodeTree):
        """Delete input sockets other than the important ones, as this can be problematic with node re-generation."""
        for i in node.interface.items_tree:
            if not(i.name == 'Value' or i.name == 'Image' or i.name == 'Alpha'): # type: ignore
                node.interface.remove(i)

    def add_io_nodes(self, node: NodeTree) -> tuple[NodeGroupInput, NodeGroupOutput]:
        """Add the Group Input and Group Output nodes to the node tree."""

        # Note: using NodeGroupInput and NodeGroupOutput confuses my pyright, but
        # bpy.types.NodeGroupInput is actually derived from bpy.types.Node.
        group_in: NodeGroupInput = node.nodes.new('NodeGroupInput') # type: ignore
        group_in.location = (0, 0)
        group_in.name = "group_in"

        group_out: NodeGroupOutput = node.nodes.new('NodeGroupOutput') # type: ignore
        group_out.location = (1000, 0)
        group_out.name = "group_out"

        return (group_in, group_out)

    def add_maths_rerouter(self, node: NodeTree, group_in_node: NodeGroupInput) -> NodeReroute:
        """Add the reroute node to clear up our node tree network."""

        # Again, NodeReroute is a subclass of bpy.types.Node. node.nodes.new() returns bpy.types.Node.
        maths_reroute_node: NodeReroute = node.nodes.new('NodeReroute') # type: ignore
        maths_reroute_node.location = (group_in_node.location[0] + 200, group_in_node.location[1] - 35)

        node.links.new(group_in_node.outputs['Value'], maths_reroute_node.inputs[0])
        return maths_reroute_node

    ##### Methods used for the link loop (for link in config.links) #####
    def LINKLOOP_add_math_nodes(self, link: Btxs_LinkItem, node: NodeTree, maths_reroute_node: NodeReroute, prev_mix_inputs_loc: tuple[int, int]) -> tuple[ShaderNodeMath, ShaderNodeMath, ShaderNodeMath, tuple[int, int]]:
        """Add greater than node, less than node, and multiply node for the link. Also connect them together properly.
        To be exact, the logic is: if `input` > `gt threshold` `and` `input` < `lt threshold` then `true`.
        The `and` here is replaced with the `Multiply` math node which is similar to a boolean `AND` with two boolean (0.00/1.00) inputs.
        Of course, everything is a float in Blender's shader node system.
        """
        # ShaderNodeMath is a subclass of Node
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = link.int_simple_val - 1 # type: ignore
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        # ShaderNodeMath is a subclass of Node
        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = link.int_simple_val + 1 # type: ignore
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        # ShaderNodeMath is a subclass of Node
        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore

        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        return (gt_node, lt_node, mult_node, prev_mix_inputs_loc)

    def LINKLOOP_add_img(self, link: Btxs_LinkItem, node: NodeTree, prev_mix_inputs_loc: tuple[int, int]) -> tuple[ShaderNodeTexImage, tuple[int, int]]:
        """(Only if an image is supplied for the link) add and configure an image texture node."""
        # ShaderNodeTexImage is a subclass of Node
        img_node: ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage') # type: ignore

        img_node.image = link.img
        img_node.name = "img_" + link.name
        img_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 360)
        img_node.hide = True
        return (img_node, prev_mix_inputs_loc)

    def LINKLOOP_add_color_input_socket(self, link: Btxs_LinkItem, node: NodeTree) -> None:
        """(Only if no image is supplied for the link) add a color input socket for the node tree."""
        node.interface.new_socket(link.name, in_out='INPUT', socket_type='NodeSocketColor')

    def LINKLOOP_connect_color_input_socket(self, link: Btxs_LinkItem, node: NodeTree, group_in: NodeGroupInput, mix_node: ShaderNodeMix):
        """(Only if no image is supplied for the link) Link the color input socket to a mix color node."""
        node.links.new(group_in.outputs[link.name], mix_node.inputs['B'])

    def LINKLOOP_add_mix_color_node(self, link: Btxs_LinkItem, node: NodeTree, multiply_node: ShaderNodeMath, prev_mix_nodes_loc: tuple[int, int]) -> tuple[ShaderNodeMix, tuple[int, int]]:
        """Add a mix color node."""
        # ShaderNodeMix is a subclass of Node
        mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix') # type: ignore

        mix_node.name = "mix_" + link.name
        mix_node.data_type = 'RGBA'
        mix_node.location = (prev_mix_nodes_loc[0] + 210, prev_mix_nodes_loc[1])
        mix_node.hide = True
        node.links.new(multiply_node.outputs[0], mix_node.inputs[0])
        return (mix_node, mix_node.location)

    def LINKLOOP_connect_previous_mix_color_node(self, node: NodeTree, current_node: ShaderNodeMix, previous_node: ShaderNodeMix | None):
        """Connect the previous mix color node with the current one (if `previous_node` is not `None`)"""
        if previous_node is not None:
            node.links.new(previous_node.outputs['Result'], current_node.inputs['A'])

    def LINKLOOP_add_mix_alpha_node(self, link: Btxs_LinkItem, node: NodeTree, mix_color_node: ShaderNodeMix, multiply_node: ShaderNodeMath) -> ShaderNodeMix:
        """Add a mix node (for the alpha channel)."""
        # ShaderNodeMix is a subclass of Node
        alpha_mix_node: bpy.types.ShaderNodeMix = node.nodes.new('ShaderNodeMix') # type: ignore
        alpha_mix_node.name = "mix_alpha_" + link.name
        alpha_mix_node.hide = True
        alpha_mix_node.data_type = 'FLOAT'
        alpha_mix_node.location = (mix_color_node.location[0], mix_color_node.location[1] - 45)
        node.links.new(multiply_node.outputs[0], alpha_mix_node.inputs[0])

        return alpha_mix_node

    def LINKLOOP_connect_previous_mix_alpha_node(self, node: NodeTree, current_node: ShaderNodeMix, previous_node: ShaderNodeMix | None):
        """Connect the previous mix node (for the alpha channel) with the current one (if `previous_node` is not `None`)"""
        if previous_node is not None:
            node.links.new(previous_node.outputs['Result'], current_node.inputs['A'])

    def LINKLOOP_connect_image_to_mix_node(self, node: NodeTree, img_node: ShaderNodeTexImage, mix_node: ShaderNodeMix):
        """Connect the image texture node to its mix color node."""
        node.links.new(img_node.outputs['Color'], mix_node.inputs['B'])

    def LINKLOOP_connect_image_alpha_to_mix_node(self, node: NodeTree, img_node: ShaderNodeTexImage, mix_node: ShaderNodeMix):
        """(Only if `output_alpha` is set to True under `config`) Connect the alpha channel of an image node to its mix node."""
        try:
            node.links.new(img_node.outputs['Alpha'], mix_node.inputs['B'])
        except AttributeError:
            return

    def LINKLOOP_add_alpha_input_socket(self, node: NodeTree, link: Btxs_LinkItem):
        """(Only if no image is supplied for the link) add an alpha channel input socket for the node tree."""
        node.interface.new_socket(link.name + "_alpha", in_out='INPUT', socket_type='NodeSocketFloat')
        node.interface.items_tree[link.name + "_alpha"].max_value = 1.0
        node.interface.items_tree[link.name + "_alpha"].min_value = 0.0

    def LINKLOOP_connect_alpha_input_socket(self, link: Btxs_LinkItem, node: NodeTree, group_in: NodeGroupInput, mix_node: ShaderNodeMix):
        """(Only if no image is supplied for the link) Link the alpha channel input socket to a mix node."""
        try:
            node.links.new(group_in.outputs[link.name + "_alpha"], mix_node.inputs['B'])
        except AttributeError:
            return

    def LINKLOOP_set_fallback_image(self, node: NodeTree, fallback_img: Image, color_mix_node: ShaderNodeMix) -> ShaderNodeTexImage:
        """(Only for index 0 of links) set fallback image"""
        # ShaderNodeTexImage is a subclass of Node
        fallback_img_node: bpy.types.ShaderNodeTexImage = node.nodes.new('ShaderNodeTexImage') # type: ignore
        fallback_img_node.name = "fallback_img"
        fallback_img_node.location = (color_mix_node.location[0] - 350, color_mix_node.location[1])
        fallback_img_node.image = fallback_img
        fallback_img_node.hide = True
        node.links.new(fallback_img_node.outputs['Color'], color_mix_node.inputs['A'])
        return fallback_img_node

    def LINKLOOP_set_fallback_image_alpha(self, node: NodeTree, fallback_img_node: ShaderNodeTexImage, alpha_mix_node: ShaderNodeMix):
        """Set a fallback image (alpha channel)."""
        try:
            node.links.new(fallback_img_node.outputs['Alpha'], alpha_mix_node.inputs['A'])
        except AttributeError:
            return

    def LINKLOOP_set_falback_color(self, color_mix_node: ShaderNodeMix):
        """(Only if no fallback image is supplied under `config` Set a fallback color."""
        color_mix_node.inputs['A'].default_value = (0, 0, 0, 1) # type: ignore

    def connect_last_mix_color_nodes(self, node: NodeTree, group_out: NodeGroupOutput, curr_mix_color_node: ShaderNodeMix, prev_mix_nodes_loc: tuple[int, int]):
        try:
            group_out.location = (prev_mix_nodes_loc[0] + 200, prev_mix_nodes_loc[1])
            node.links.new(curr_mix_color_node.outputs['Result'], group_out.inputs['Image'])
        except AttributeError:
            return

    def connect_last_alpha_mix_node(self, node: NodeTree, group_out: NodeGroupOutput, curr_alpha_mix_node: ShaderNodeMix):
        try:
            node.links.new(curr_alpha_mix_node.outputs['Result'], group_out.inputs['Alpha'])
        except AttributeError:
            return

    def LINKLOOP_set_fallback_alpha(self, alpha_mix_node: ShaderNodeMix):
        """(Only if no fallback image is supplied under `config` Set a fallback alpha color."""
        try:
            alpha_mix_node.inputs['A'].default_value = 0.0 # type: ignore
        except AttributeError:
            return

    def setup_node_tree_attributes(self, config, node):
        node.interface.items_tree['Value'].default_value = config.int_min # type: ignore
        node.interface.items_tree['Value'].subtype = 'FACTOR'

class IntSimpleNodeTreeBuilder(BtxsNodeTreeBuilder):
    def __init__(self, config: Btxs_ConfigEntry):
        super().__init__(config)

class IntNodeTreeBuilder(BtxsNodeTreeBuilder):
    def __init__(self, config: Btxs_ConfigEntry):
        super().__init__(config)

    def LINKLOOP_add_math_nodes(self, link: Btxs_LinkItem, node: NodeTree, maths_reroute_node: NodeReroute, prev_mix_inputs_loc: tuple[int, int]) -> tuple[ShaderNodeMath, ShaderNodeMath, ShaderNodeMath, tuple[int, int]]:
        # ShaderNodeMath is a subclass of Node
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = link.int_gt # type: ignore
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        # ShaderNodeMath is a subclass of Node
        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = link.int_lt # type: ignore
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        # ShaderNodeMath is a subclass of Node
        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore

        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        return (gt_node, lt_node, mult_node, prev_mix_inputs_loc)

    def setup_node_tree_attributes(self, config, node):
        node.interface.items_tree['Value'].default_value = config.int_min # type: ignore
        node.interface.items_tree['Value'].subtype = 'NONE'

class FloatNodeTreeBuilder(BtxsNodeTreeBuilder):
    def __init__(self, config: Btxs_ConfigEntry):
        super().__init__(config)

    def add_io_sockets(self, config, node: NodeTree):
        """Add the base input and output sockets for the node tree. Only adds the sockets when they don't exist already, so that the user doesn't have to reconnect nodes themselves."""
        if not 'Value' in node.interface.items_tree:
            node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketFloat')
        elif not isinstance(node.interface.items_tree['Value'], bpy.types.NodeSocketFloat):
            node.interface.remove(node.interface.items_tree['Value'])
            node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketFloat')

        if not 'Image' in node.interface.items_tree:
            node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')

        node.interface.items_tree['Value'].min_value = config.float_min # type: ignore
        node.interface.items_tree['Value'].max_value = config.float_max # type: ignore

        if config.output_alpha:
            if not 'Alpha' in node.interface.items_tree: 
                node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        elif 'Alpha' in node.interface.items_tree:
            node.interface.remove(node.interface.items_tree['Alpha'])

    def LINKLOOP_add_math_nodes(self, link: Btxs_LinkItem, node: NodeTree, maths_reroute_node: NodeReroute, prev_mix_inputs_loc: tuple[int, int]) -> tuple[ShaderNodeMath, ShaderNodeMath, ShaderNodeMath, tuple[int, int]]:
        # ShaderNodeMath is a subclass of Node
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = link.float_gt # type: ignore
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        # ShaderNodeMath is a subclass of Node
        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = link.float_lt # type: ignore
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        # ShaderNodeMath is a subclass of Node
        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore

        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        return (gt_node, lt_node, mult_node, prev_mix_inputs_loc)

    def setup_node_tree_attributes(self, config, node):
        node.interface.items_tree['Value'].default_value = config.float_min 
        node.interface.items_tree['Value'].subtype = 'FACTOR'

class EnumNodeTreeBuilder(BtxsNodeTreeBuilder):
    def __init__(self, config) -> None:
        self.enum_idx = 0
        super().__init__(config)

    def init_node_tree(self, config) -> NodeTree:
        """Clear node tree and mark it as a Beantextures-generated node tree."""
        super().init_node_tree(config)
        node: NodeTree = config.target_node_tree
        node.beantextures_props.enum_items.clear()
        return node

    def add_io_sockets(self, config, node: NodeTree):
        """Add the base input and output sockets for the node tree. Only adds the sockets when they don't exist already, so that the user doesn't have to reconnect nodes themselves."""
        if not 'Value' in node.interface.items_tree:
            node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')
        elif not isinstance(node.interface.items_tree['Value'], bpy.types.NodeSocketInt):
            node.interface.remove(node.interface.items_tree['Value'])
            node.interface.new_socket("Value", in_out='INPUT', socket_type='NodeSocketInt')

        if not 'Image' in node.interface.items_tree:
            node.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')

        node.interface.items_tree['Value'].min_value = 0 # type: ignore
        node.interface.items_tree['Value'].max_value = len(config.links) - 1 # type: ignore

        if config.output_alpha:
            if not 'Alpha' in node.interface.items_tree: 
                node.interface.new_socket("Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        elif 'Alpha' in node.interface.items_tree:
            node.interface.remove(node.interface.items_tree['Alpha'])

    def LINKLOOP_add_math_nodes(self, link: Btxs_LinkItem, node: NodeTree, maths_reroute_node: NodeReroute, prev_mix_inputs_loc: tuple[int, int]) -> tuple[ShaderNodeMath, ShaderNodeMath, ShaderNodeMath, tuple[int, int]]:
        enum_item = node.beantextures_props.enum_items.add()
        enum_item.name = link.name
        enum_item.idx = self.enum_idx

        # ShaderNodeMath is a subclass of Node
        gt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        gt_node.name = "gt_" + link.name
        gt_node.operation = 'GREATER_THAN'
        gt_node.inputs[1].default_value = self.enum_idx - 1 # type: ignore
        gt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 470)
        node.links.new(maths_reroute_node.outputs[0], gt_node.inputs[0])
        prev_mix_inputs_loc = gt_node.location

        # ShaderNodeMath is a subclass of Node
        lt_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore
        lt_node.name = "lt_" + link.name
        lt_node.operation = 'LESS_THAN'
        lt_node.inputs[1].default_value = self.enum_idx + 1 # type: ignore
        lt_node.location = (prev_mix_inputs_loc[0], prev_mix_inputs_loc[1] - 170)
        node.links.new(maths_reroute_node.outputs[0], lt_node.inputs[0])

        # ShaderNodeMath is a subclass of Node
        mult_node: bpy.types.ShaderNodeMath = node.nodes.new('ShaderNodeMath') # type: ignore

        mult_node.name = "mult_" + link.name
        mult_node.operation = 'MULTIPLY'
        mult_node.location = (prev_mix_inputs_loc[0] + 180, prev_mix_inputs_loc[1] - 100)
        node.links.new(gt_node.outputs[0], mult_node.inputs[0])
        node.links.new(lt_node.outputs[0], mult_node.inputs[1])

        self.enum_idx += 1
        return (gt_node, lt_node, mult_node, prev_mix_inputs_loc)

    def setup_node_tree_attributes(self, config, node):
        node.interface.items_tree['Value'].default_value = 0 # type: ignore
        node.interface.items_tree['Value'].subtype = 'FACTOR'

class BtxsOp_GenerateNode(Operator):
    """Generate node tree using active configuration"""
    bl_label = "Generate Node Tree"
    bl_idname = "beantextures.generate_node_tree"

    @classmethod
    def poll(cls, context):
        settings = context.scene.beantextures_settings
        if len(settings.configs) > 0 and settings.active_config_idx < len(settings.configs):
            config = settings.configs[settings.active_config_idx]

            if not isinstance(config.target_node_tree, bpy.types.ShaderNodeTree):
                cls.poll_message_set("Specify a shader node group as the target!")
            if not bool(config.target_node_tree):
                cls.poll_message_set("Set a valid shader node group as a target first!")
            return bool(config.target_node_tree) and isinstance(config.target_node_tree, bpy.types.ShaderNodeTree)
        return False

    def draw(self, context):
        layout = self.layout
        column = layout.column()

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
            errors.update({'configuration': ["There is no link available."]})
        for link in config.links:
            errors.update({f"link '{link.name}'": warning_checker(context, link, config)})

        err_detected = False
        for err_key in errors.keys():
            if len(errors[err_key]) == 0:
                continue
            err_detected = True
            box = layout.box()
            box.label(text=f"On {err_key}:")
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
                IntSimpleNodeTreeBuilder(config)
            case 'INT':
                IntNodeTreeBuilder(config)
            case 'FLOAT':
                FloatNodeTreeBuilder(config)
            case 'ENUM':
                EnumNodeTreeBuilder(config)

        self.report({'INFO'}, f"Generated tree with config '{config.name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    

def register():
    bpy.utils.register_class(BtxsOp_GenerateNode)

def unregister():
    bpy.utils.unregister_class(BtxsOp_GenerateNode)
