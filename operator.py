
import bpy
from mathutils import Vector
import gpu
import blf
from gpu_extras.batch import batch_for_shader

# ==================================================================================
# Utility helpers
# ==================================================================================

def group_objects_with_empty(context, location, empty_name="Group"):
    selected = context.selected_objects
    if not selected:
        return None

    empty = bpy.data.objects.new(empty_name, None)
    empty.location = location
    context.collection.objects.link(empty)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected:
        obj.select_set(True)
    empty.select_set(True)
    context.view_layer.objects.active = empty

    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    # keep the empty selected so the interactive operator can run
    bpy.ops.object.select_all(action='DESELECT')
    empty.select_set(True)
    context.view_layer.objects.active = empty

    bpy.ops.object.empty_properties_interactive('INVOKE_DEFAULT')
    return empty


def clear_parents_and_delete_empties(context, keep_transform=True):
    selected = context.selected_objects
    parents_with_children = [o for o in selected if o.type == 'EMPTY' and o.children]

    if not parents_with_children:
        return -1

    bpy.ops.object.select_all(action='DESELECT')
    for p in parents_with_children:
        for child in p.children:
            child.select_set(True)

    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM' if keep_transform else 'CLEAR')

    for p in parents_with_children:
        bpy.data.objects.remove(p, do_unlink=True)

    return len(parents_with_children)


def clear_parents_from_objects(context, keep_transform=True):
    selected = context.selected_objects
    parents = [o for o in selected if o.children]

    if not parents:
        return -1

    bpy.ops.object.select_all(action='DESELECT')
    for p in parents:
        for child in p.children:
            child.select_set(True)

    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM' if keep_transform else 'CLEAR')
    return sum(len(p.children) for p in parents)


def unparent_selected_objects(context, keep_transform=True):
    selected = [o for o in context.selected_objects if o.parent]
    if not selected:
        return -1
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM' if keep_transform else 'CLEAR')
    return len(selected)


# ==================================================================================
#  View‑port overlay drawing
# ==================================================================================
draw_handler = None

def draw_empty_properties_overlay():
    context = bpy.context
    if not context.active_object or context.active_object.type != 'EMPTY' or context.mode != 'OBJECT':
        return

    obj = context.active_object
    x_off, y_off = 10, 10
    w, h = 180, 100

    bg = (0.2, 0.2, 0.2, 0.8)
    border = (0.5, 0.5, 0.5, 1)
    txt = (0.9, 0.9, 0.9, 1)
    accent = (0.3, 0.6, 1.0, 1)

    # background
    verts = [(x_off, y_off),
             (x_off + w, y_off),
             (x_off + w, y_off + h),
             (x_off, y_off + h)]
    indices = [(0, 1, 2), (2, 3, 0)]
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=indices)
    shader.bind()
    shader.uniform_float("color", bg)
    batch.draw(shader)

    # border
    line_batch = batch_for_shader(shader, 'LINE_STRIP', {"pos": verts + [verts[0]]})
    shader.uniform_float("color", border)
    line_batch.draw(shader)

    # text
    font = 0
    blf.color(font, *txt)
    blf.size(font, 12)
    blf.position(font, x_off + 10, y_off + h - 25, 0)
    blf.draw(font, f"Empty: {obj.name}")

    tname = obj.empty_display_type.replace('_', ' ').title()
    blf.position(font, x_off + 10, y_off + h - 45, 0)
    blf.draw(font, f"Type: {tname}")

    blf.position(font, x_off + 10, y_off + h - 65, 0)
    blf.draw(font, f"Size: {obj.empty_display_size:.3f}")

    blf.size(font, 10)
    blf.color(font, *accent)
    blf.position(font, x_off + 10, y_off + h - 85, 0)
    blf.draw(font, "E: Interactive Adjust")


# ==================================================================================
#  Modal Interactive Operator
# ==================================================================================
class OBJECT_OT_empty_properties_interactive(bpy.types.Operator):
    bl_idname = "object.empty_properties_interactive"
    bl_label = "Interactive Empty Properties"
    bl_options = {'REGISTER', 'UNDO'}

    empty_types = ['PLAIN_AXES', 'ARROWS', 'SINGLE_ARROW', 'CIRCLE',
                   'CUBE', 'SPHERE', 'CONE', 'IMAGE']

    def __init__(self):
        self.mouse_init_x = 0
        self.size_init = 1.0
        self.size_cur = 1.0
        self.type_idx = 0
        self.type_init_idx = 0
        self.target = None

    def invoke(self, context, event):
        obj = context.active_object
        if not obj or obj.type != 'EMPTY':
            self.report({'WARNING'}, "Select an empty")
            return {'CANCELLED'}

        self.target = obj
        self.mouse_init_x = event.mouse_x
        self.size_init = obj.empty_display_size
        self.size_cur = self.size_init

        try:
            self.type_idx = self.empty_types.index(obj.empty_display_type)
            self.type_init_idx = self.type_idx
        except ValueError:
            self.type_idx = self.type_init_idx = 0

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            dx = event.mouse_x - self.mouse_init_x
            self.size_cur = max(0.001, self.size_init + dx * 0.01)
            self.target.empty_display_size = self.size_cur

        elif event.type == 'WHEELUPMOUSE':
            self.type_idx = (self.type_idx + 1) % len(self.empty_types)
            self.target.empty_display_type = self.empty_types[self.type_idx]

        elif event.type == 'WHEELDOWNMOUSE':
            self.type_idx = (self.type_idx - 1) % len(self.empty_types)
            self.target.empty_display_type = self.empty_types[self.type_idx]

        elif event.type in {'LEFTMOUSE', 'RET', 'SPACE'}:
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.target.empty_display_size = self.size_init
            self.target.empty_display_type = self.empty_types[self.type_init_idx]
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


# ==================================================================================
#  Core Operators used in the Pie Menu
# ==================================================================================
class OBJECT_OT_group_world_origin(bpy.types.Operator):
    bl_idname = "object.group_world_origin"
    bl_label = "Group at World Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        group_objects_with_empty(context, Vector((0, 0, 0)), "WorldGroup")
        return {'FINISHED'}


class OBJECT_OT_group_object_origin(bpy.types.Operator):
    bl_idname = "object.group_object_origin"
    bl_label = "Group at Object Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        center = sum((o.matrix_world.translation for o in sel), Vector()) / len(sel)
        group_objects_with_empty(context, center, f"Group_{len(sel)}Objects")
        return {'FINISHED'}


class OBJECT_OT_group_active_origin(bpy.types.Operator):
    bl_idname = "object.group_active_origin"
    bl_label = "Group to Active Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = context.active_object
        sel = context.selected_objects
        if not active or not sel:
            self.report({'WARNING'}, "Need active + selection")
            return {'CANCELLED'}
        group_objects_with_empty(context, active.matrix_world.translation, f"Group_{active.name}")
        return {'FINISHED'}


class OBJECT_OT_group_cursor_origin(bpy.types.Operator):
    bl_idname = "object.group_cursor_origin"
    bl_label = "Group at Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel = context.selected_objects
        if not sel:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        group_objects_with_empty(context, context.scene.cursor.location, "CursorGroup")
        return {'FINISHED'}


class OBJECT_OT_parent_default(bpy.types.Operator):
    bl_idname = "object.parent_default"
    bl_label = "Parent to Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = context.active_object
        sel = context.selected_objects
        if not active or len(sel) < 2:
            self.report({'WARNING'}, "Select active + children")
            return {'CANCELLED'}
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        return {'FINISHED'}


class OBJECT_OT_ungroup_keep_transform(bpy.types.Operator):
    bl_idname = "object.ungroup_keep_transform"
    bl_label = "Ungroup (Keep Transform)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.selected_objects:
            return {'CANCELLED'}
        res = clear_parents_and_delete_empties(context, True)
        return {'FINISHED'} if res > 0 else {'CANCELLED'}


class OBJECT_OT_ungroup_reset_transform(bpy.types.Operator):
    bl_idname = "object.ungroup_reset_transform"
    bl_label = "Ungroup (Reset Transform)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.selected_objects:
            return {'CANCELLED'}
        res = clear_parents_and_delete_empties(context, False)
        return {'FINISHED'} if res > 0 else {'CANCELLED'}


class OBJECT_OT_unparent_clear(bpy.types.Operator):
    bl_idname = "object.unparent_clear"
    bl_label = "Clear Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        res = clear_parents_from_objects(context, False)
        return {'FINISHED'} if res > 0 else {'CANCELLED'}


class OBJECT_OT_unparent_keep_transform(bpy.types.Operator):
    bl_idname = "object.unparent_keep_transform"
    bl_label = "Clear Parent (Keep Transform)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        res = clear_parents_from_objects(context, True)
        return {'FINISHED'} if res > 0 else {'CANCELLED'}


class OBJECT_OT_unparent_selected_keep_transform(bpy.types.Operator):
    bl_idname = "object.unparent_selected_keep_transform"
    bl_label = "Unparent Selected (Keep Transform)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        res = unparent_selected_objects(context, True)
        return {'FINISHED'} if res > 0 else {'CANCELLED'}


class OBJECT_OT_unparent_selected_clear(bpy.types.Operator):
    bl_idname = "object.unparent_selected_clear"
    bl_label = "Unparent Selected (Reset Transform)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        res = unparent_selected_objects(context, False)
        return {'FINISHED'} if res > 0 else {'CANCELLED'}


# ==================================================================================
#  Miscellaneous simple operators
# ==================================================================================
class OBJECT_OT_set_empty_size(bpy.types.Operator):
    bl_idname = "object.set_empty_size"
    bl_label = "Set Empty Size"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.FloatProperty(name="Size", default=1.0, min=0.001, max=100)

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'EMPTY':
            obj.empty_display_size = self.size
            return {'FINISHED'}
        return {'CANCELLED'}


class OBJECT_OT_toggle_empty_overlay(bpy.types.Operator):
    bl_idname = "object.toggle_empty_overlay"
    bl_label = "Toggle Empty Overlay"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global draw_handler
        if draw_handler is None:
            draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_empty_properties_overlay, (), 'WINDOW', 'POST_PIXEL')
            self.report({'INFO'}, "Overlay On")
        else:
            bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')
            draw_handler = None
            self.report({'INFO'}, "Overlay Off")
        for a in context.screen.areas:
            if a.type == 'VIEW_3D':
                a.tag_redraw()
        return {'FINISHED'}


# ==================================================================================
#  Key‑map binding helper
# ==================================================================================
def register_keymaps(addon_keymaps):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY')

    # P pie menu
    kmi = km.keymap_items.new("wm.call_menu_pie", 'P', 'PRESS')
    kmi.properties.name = "VIEW3D_MT_group_object_pie"
    addon_keymaps.append((km, kmi))

    # E interactive empty properties
    kmi = km.keymap_items.new("object.empty_properties_interactive", 'E', 'PRESS')
    addon_keymaps.append((km, kmi))

    # ensure overlay starts
    global draw_handler
    if draw_handler is None:
        draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_empty_properties_overlay, (), 'WINDOW', 'POST_PIXEL')


# ==================================================================================
#  Class list for registration
# ==================================================================================
classes = (
    OBJECT_OT_group_world_origin,
    OBJECT_OT_group_object_origin,
    OBJECT_OT_group_active_origin,
    OBJECT_OT_group_cursor_origin,
    OBJECT_OT_parent_default,
    OBJECT_OT_ungroup_keep_transform,
    OBJECT_OT_ungroup_reset_transform,
    OBJECT_OT_unparent_clear,
    OBJECT_OT_unparent_keep_transform,
    OBJECT_OT_unparent_selected_keep_transform,
    OBJECT_OT_unparent_selected_clear,
    OBJECT_OT_empty_properties_interactive,
    OBJECT_OT_set_empty_size,
    OBJECT_OT_toggle_empty_overlay,
)
