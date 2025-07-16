
bl_info = {
    "name": "Nestify",
    "author": "Model verse",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "P Pie Menu",
    "description": "Parent/unparent selected objects with active object and also with empties at various positions with enhanced features",
    "category": "Object",
}

import bpy
from . import operator
from . import menu

classes = operator.classes + menu.classes

addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    operator.register_keymaps(addon_keymaps)

def unregister():
    from .operator import draw_handler

    if draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')
        operator.draw_handler = None

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
