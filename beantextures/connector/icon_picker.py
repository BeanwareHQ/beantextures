"""Icon picker module."""
# Modified by Daringcuteseal for Beantextures
# Source of original code: https://projects.blender.org/blender/blender-addons/src/branch/main/development_icon_get.py
# by roaoao, maintained by the Blender Foundation and is licensed under the GPL.
# Add-on info: https://docs.blender.org/manual/en/4.1/addons/development/icon_viewer.html

import bpy
import math
from bpy.props import (
    BoolProperty,
    StringProperty,
)

DPI = 72
POPUP_PADDING = 10
WIN_PADDING = 32
ICON_SIZE = 20
HISTORY_SIZE = 100
HISTORY = []

# Set only once
ICONS: list[str] = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()

def ui_scale():
    prefs = bpy.context.preferences.system
    return prefs.dpi / DPI

def prefs() -> 'Btxs_IV_ScenePreferences':
    return bpy.context.scene.beantextures_icon_viewer_prefs

class Icons:
    def __init__(self, is_popup=False):
        self._filtered_icons = None
        self._filter = ""
        self.filter = ""
        self.selected_icon = ""
        self.is_popup = is_popup

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, value):
        if self._filter == value:
            return

        self._filter = value
        self.update()

    @property
    def filtered_icons(self):
        if self._filtered_icons is None:
            self._filtered_icons = []
            icon_filter = self._filter.upper()
            self.filtered_icons.clear()
            pr = prefs()

            for icon in ICONS:
                if icon == 'NONE' or \
                        icon_filter and icon_filter not in icon or \
                        not pr.show_brush_icons and "BRUSH_" in icon and \
                        icon != 'BRUSH_DATA' or \
                        not pr.show_matcap_icons and "MATCAP_" in icon or \
                        not pr.show_event_icons and (
                            "EVENT_" in icon or "MOUSE_" in icon
                        ) or \
                        not pr.show_colorset_icons and "COLORSET_" in icon:
                    continue
                self._filtered_icons.append(icon)

        return self._filtered_icons

    @property
    def num_icons(self):
        return len(self.filtered_icons)

    def update(self):
        if self._filtered_icons is not None:
            self._filtered_icons.clear()
            self._filtered_icons = None

    def draw(self, layout, num_cols=0, icons=None):
        if icons:
            filtered_icons = reversed(icons)
        else:
            filtered_icons = self.filtered_icons

        column = layout.column(align=True)
        row = column.row(align=True)
        row.alignment = 'CENTER'

        selected_icon = self.selected_icon if self.is_popup else \
            bpy.context.window_manager.clipboard
        col_idx = 0
        for i, icon in enumerate(filtered_icons):
            p = row.operator(
                BtxsOp_IV_OT_icon_select.bl_idname, text="",
                icon=icon, emboss=icon == selected_icon)
            p.icon = icon
            p.force_copy_on_select = not self.is_popup

            col_idx += 1
            if col_idx > num_cols - 1:
                if icons:
                    break
                col_idx = 0
                if i < len(filtered_icons) - 1:
                    row = column.row(align=True)
                    row.alignment = 'CENTER'

        if col_idx != 0 and not icons and i >= num_cols:
            for _ in range(num_cols - col_idx):
                row.label(text="", icon='BLANK1')

        if not filtered_icons:
            row.label(text="No icons were found")

class Btxs_IV_IconsMgr:
    def __init__(self):
        self.popup_icons = Icons(is_popup=True)

    def update_icons(self, context):
        self.popup_icons.update()

icons_mgr = Btxs_IV_IconsMgr()

class Btxs_IV_ScenePreferences(bpy.types.PropertyGroup):
    show_history: BoolProperty(
        name="Show History",
        description="Show history", default=True)
    show_brush_icons: BoolProperty(
        name="Show Brush Icons",
        description="Show brush icons", default=True,
        update=lambda s, c: icons_mgr.update_icons(c))
    show_matcap_icons: BoolProperty(
        name="Show Matcap Icons",
        description="Show matcap icons", default=True,
        update=lambda s, c: icons_mgr.update_icons(c))
    show_event_icons: BoolProperty(
        name="Show Event Icons",
        description="Show event icons", default=True,
        update=lambda s, c: icons_mgr.update_icons(c))
    show_colorset_icons: BoolProperty(
        name="Show Colorset Icons",
        description="Show colorset icons", default=True,
        update=lambda s, c: icons_mgr.update_icons(c))

class BtxsOp_IV_OT_icon_select(bpy.types.Operator):
    bl_idname = "beantextures.icon_select"
    bl_label = ""
    bl_description = "Select the icon"
    bl_options = {'INTERNAL'}

    icon: StringProperty()
    force_copy_on_select: BoolProperty()

    @classmethod
    def poll(cls, context) -> bool:
        connector = context.active_bone.beantextures_connector
        # FIXME: wonky
        try:
            connector.connectors[connector.active_connector_idx]
        except IndexError:
            return False
        return (context.active_bone is not None)

    def execute(self, context):
        icons_mgr.popup_icons.selected_icon = self.icon
        pr = prefs()

        if pr.show_history:
            if self.icon in HISTORY:
                HISTORY.remove(self.icon)
            if len(HISTORY) >= HISTORY_SIZE:
                HISTORY.pop(0)
            HISTORY.append(self.icon)
        return {'FINISHED'}


class BtxsOp_IV_OT_icons_set(bpy.types.Operator):
    bl_idname = "beantextures.icon_set"
    bl_label = "Icon Selector"
    bl_description = "Select an icon for a connector item"
    bl_property = "filter_auto_focus"

    instance = None

    @classmethod
    def poll(cls, context) -> bool:
        connector = context.active_bone.beantextures_connector
        # FIXME: wonky
        try:
            connector.connectors[connector.active_connector_idx]
        except IndexError:
            return False
        return (context.active_bone is not None)


    def set_filter(self, value):
        icons_mgr.popup_icons.filter = value

    def set_selected_icon(self, value):
        if BtxsOp_IV_OT_icons_set.instance:
            BtxsOp_IV_OT_icons_set.instance.auto_focusable = False

    filter: StringProperty(
        description="Filter",
        get=lambda s: icons_mgr.popup_icons.filter,
        set=set_filter,
        options={'TEXTEDIT_UPDATE'})
    selected_icon: StringProperty(
        description="Selected Icon",
        get=lambda s: icons_mgr.popup_icons.selected_icon,
        set=set_selected_icon)

    def get_num_cols(self, num_icons):
        return round(1.3 * math.sqrt(num_icons))

    def draw_header(self, layout):
        pr = prefs()
        header = layout.box()
        header = header.split(factor=0.75) if self.selected_icon else \
            header.row()
        row = header.row(align=True)
        row.prop(pr, "show_matcap_icons", text="", icon='SHADING_RENDERED')
        row.prop(pr, "show_brush_icons", text="", icon='BRUSH_DATA')
        row.prop(pr, "show_colorset_icons", text="", icon='COLOR')
        row.prop(pr, "show_event_icons", text="", icon='HAND')
        row.separator()

        row.prop(self, "filter", text="", icon='VIEWZOOM')

        if self.selected_icon:
            row = header.row()
            row.prop(self, "selected_icon", text="", icon=self.selected_icon)

    def draw(self, context):
        pr = prefs()
        col = self.layout
        self.draw_header(col)

        history_num_cols = int(
            (self.width - POPUP_PADDING) / (ui_scale() * ICON_SIZE))
        num_cols = min(
            self.get_num_cols(len(icons_mgr.popup_icons.filtered_icons)),
            history_num_cols)

        subcol = col.column(align=True)

        if HISTORY and pr.show_history:
            icons_mgr.popup_icons.draw(subcol.box(), history_num_cols, HISTORY)

        icons_mgr.popup_icons.draw(subcol.box(), num_cols)

    def close(self):
        bpy.context.window.screen = bpy.context.window.screen

    def check(self, context):
        return True

    def cancel(self, context):
        BtxsOp_IV_OT_icons_set.instance = None

    def execute(self, context):
        connector = context.active_bone.beantextures_connector
        item = connector.connectors[connector.active_connector_idx]
        
        if not BtxsOp_IV_OT_icons_set.instance:
            return {'CANCELLED'}
        BtxsOp_IV_OT_icons_set.instance = None

        if len(self.selected_icon) > 0:
            item.icon = self.selected_icon

        return {'FINISHED'}

    def invoke(self, context, event):
        icons_mgr.popup_icons.selected_icon = ""
        icons_mgr.popup_icons.filter = ""
        BtxsOp_IV_OT_icons_set.instance = self
        self.auto_focusable = True

        num_cols = self.get_num_cols(len(icons_mgr.popup_icons.filtered_icons))
        self.width = int(min(
            ui_scale() * (num_cols * ICON_SIZE + POPUP_PADDING),
            context.window.width - WIN_PADDING))

        return context.window_manager.invoke_props_dialog(
            self, width=self.width)

classes = (
    BtxsOp_IV_OT_icon_select,
    Btxs_IV_ScenePreferences,
    BtxsOp_IV_OT_icons_set,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.beantextures_icon_viewer_prefs = bpy.props.PointerProperty(type=Btxs_IV_ScenePreferences)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
