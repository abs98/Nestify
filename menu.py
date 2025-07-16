
import bpy

class VIEW3D_MT_group_object_pie(bpy.types.Menu):
    bl_label = "Parent Object Pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Grouping Options
        pie.operator("object.group_object_origin", text="At Center", icon='EMPTY_AXIS')
        pie.operator("object.group_active_origin", text="At Active", icon='EMPTY_ARROWS')

        # Unparent Selected
        column = pie.split().column()
        column.label(text="Unparent Selected", icon='UNLINKED')
        column.operator("object.unparent_selected_keep_transform", text="Keep Transform")
        column.operator("object.unparent_selected_clear", text="Reset Transform")

        # Parent
        pie.operator("object.parent_default", text="Parent", icon='OBJECT_ORIGIN')

        # Additional Options
        pie.operator("object.group_cursor_origin", text="At Cursor", icon='CURSOR')
        pie.operator("object.group_world_origin", text="At World", icon='WORLD')

        # Unparent from Object
        column = pie.split().column()
        column.label(text="Unparent from Object", icon='X')
        column.operator("object.unparent_keep_transform", text="Keep Transform")
        column.operator("object.unparent_clear", text="Reset Transform")

        # Unparent from Empty
        column = pie.split().column()
        column.label(text="Unparent from Empty", icon='EMPTY_DATA')
        column.operator("object.ungroup_keep_transform", text="Keep Transform")
        column.operator("object.ungroup_reset_transform", text="Reset Transform")

classes = (VIEW3D_MT_group_object_pie,)
