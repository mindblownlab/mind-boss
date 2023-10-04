import bpy
import os
from importlib import reload
from _blender.modules import main
from bpy.props import StringProperty
from PySide2 import QtWidgets, QtCore
from bpy.app.handlers import persistent
import json
from pathlib import Path

reload(main)

_project = None
_context = None

bl_info = {
    "name": "BossMind",
    "author": "Mindblownlab",
    "version": (0, 0, 1),
    "blender": (3, 6, 2),
    "location": "Development > MBLab",
    "description": "Gestao de pipeline integrada",
    "category": "Development",
}

if 'MB_CONTEXT' in os.environ.keys():
    if os.environ['MB_CONTEXT'] != "null":
        _context = dict(json.loads(os.environ['MB_CONTEXT'])) or None

if 'MB_PROJECT' in os.environ.keys():
    if os.environ['MB_PROJECT'] != "null":
        _project = dict(json.loads(os.environ['MB_PROJECT'])) or None

try:
    app = QtWidgets.QApplication.instance()
    if app == None:
        app = QtWidgets.QApplication(['blender'])
    else:
        app.beep()
        try:
            mb_main.close()
        except:
            pass
    mb_main = main.MBMain(app=app)
    mb_main.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

except:
    pass


def reset_menu():
    try:
        unregister()
    except:
        pass
    register()


# CONTEXT ------------------------------------------------------------------------------------------------------------

class MB_MT_context(bpy.types.Menu):
    if _context is None:
        bl_label = _project.get("name")
    else:
        if _context.get("type") == "asset":
            bl_label = "{}, {} {}".format(_context.get("step"), _context.get("type").capitalize(), _context.get("asset"))
        else:
            bl_label = "{}, {} {}".format(_context.get("step"), _context.get("type").capitalize(), _context.get("shot"))

    mblab = None

    def draw(self, context):
        layout = self.layout
        if _context is None:
            layout.operator('mb.mb_mt_open_project_folder', icon="FILE_FOLDER")
            layout.separator()
        else:
            layout.operator('mb.mb_mt_open_project_folder', icon="FILE_FOLDER")
            layout.separator()
            layout.operator('mb.mb_mt_open_context_folder', icon="FILE_FOLDER")
            layout.separator()
            layout.operator('mb.mb_mt_settings_scene', icon="TOOL_SETTINGS")


class MB_MT_context_open_project_folder(bpy.types.Operator):
    bl_label = "Open project folder"
    bl_idname = "mb.mb_mt_open_project_folder"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_project.open_project()
        return {'FINISHED'}


class MB_MT_context_create_structure(bpy.types.Operator):
    bl_label = "Create folder structure"
    bl_idname = "mb.mb_mt_create_structure"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_project.create_structure()
        return {'FINISHED'}


class MB_MT_context_open_context_folder(bpy.types.Operator):
    if _context is not None:
        bl_label = "Open {} {} folder".format(_context.get("type").capitalize(), _context.get("step"))
    else:
        bl_label = "Open folder"
    bl_idname = "mb.mb_mt_open_context_folder"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_project.open_context()
        return {'FINISHED'}


class MB_MT_context_settings_scene(bpy.types.Operator):
    bl_label = "Set and Check Scene settings"
    bl_idname = "mb.mb_mt_settings_scene"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_scene.set_scene()
        return {'FINISHED'}


# OPEN, SAVE, PUBLISH ------------------------------------------------------------------------------------------------------------

class MB_MT_open(bpy.types.Operator):
    bl_label = "Open File"
    bl_idname = "mb.mb_mt_open"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_open.opening()

        return {'FINISHED'}


class MB_MT_save(bpy.types.Operator):
    bl_label = "File Save"
    bl_idname = "mb.mb_mt_save"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_save.saving()
        return {'FINISHED'}


class MB_MT_publish(bpy.types.Operator):
    bl_label = "Publish"
    bl_idname = "mb.mb_mt_publish"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_scene.publish()
        return {'FINISHED'}


# MANAGER ------------------------------------------------------------------------------------------------------------

class MB_MT_manager(bpy.types.Menu):
    bl_label = "Manager"

    def draw(self, context):
        layout = self.layout
        layout.operator('mb.mb_mt_manager_reference', icon="LINK_BLEND")
        layout.operator('mb.mb_mt_manager_backup', icon="FILE_BACKUP")
        layout.operator('mb.mb_mt_manager_context', icon="ASSET_MANAGER")


class MB_MT_manager_reference(bpy.types.Operator):
    bl_label = "Reference"
    bl_idname = "mb.mb_mt_manager_reference"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}


class MB_MT_manager_backup(bpy.types.Operator):
    bl_label = "Backup"
    bl_idname = "mb.mb_mt_manager_backup"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}


class MB_MT_manager_context(bpy.types.Operator):
    if _context is None:
        bl_label = ""
    else:
        bl_label = _context.get("type").capitalize()
    bl_idname = "mb.mb_mt_manager_context"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        if _context.get("type") == "shot":
            mb_main.mb_manager.loader()
            pass
        else:
            pass
        return {'FINISHED'}


# LOAD FILE ------------------------------------------------------------------------------------------------------------

class MB_MT_load_file(bpy.types.Operator):
    bl_label = "Load File"
    bl_idname = "mb.mb_mt_load_file"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        mb_main.mb_load.loading()
        return {'FINISHED'}


# CONTEXT ------------------------------------------------------------------------------------------------------------

class MB_MT_modeling(bpy.types.Operator):
    bl_label = "Modeling"
    bl_idname = "mb.mb_mt_modeling"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}


class MB_MT_lookdev(bpy.types.Operator):
    bl_label = "Lookdev"
    bl_idname = "mb.mb_mt_lookdev"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}


class MB_MT_rigging(bpy.types.Operator):
    bl_label = "Rigging"
    bl_idname = "mb.mb_mt_rigging"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}


class MB_MT_animation(bpy.types.Menu):
    bl_label = "Animation"

    def draw(self, context):
        layout = self.layout
        layout.operator('mb.mb_mt_animation_blast', icon="PLAY")
        layout.operator('mb.mb_mt_animation_camera', icon="VIEW_CAMERA")

    def execute(self, context):
        return {'FINISHED'}


class MB_MT_animation_blast(bpy.types.Operator):
    bl_label = "Playblast"
    bl_idname = "mb.mb_mt_animation_blast"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        return {'FINISHED'}
class MB_MT_animation_camera(bpy.types.Operator):
    bl_label = "Set camera"
    bl_idname = "mb.mb_mt_animation_camera"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        try:
            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
        except:
            pass
        return {'FINISHED'}


# RELOAD  ------------------------------------------------------------------------------------------------------------

class MB_MT_reload(bpy.types.Operator):
    bl_label = "Reload"
    bl_idname = "mb.mb_mt_reload"

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        bpy.ops.script.reload()
        return {'FINISHED'}


# ROOT MENU ------------------------------------------------------------------------------------------------------------

class MB_MT_root_menu(bpy.types.Menu):
    bl_label = "MBLab"
    if _context is None:
        bl_icon = "COLLECTION_NEW"
    else:
        if _context.get("type") == "asset":
            bl_icon = "MESH_CUBE"
        else:
            bl_icon = "RENDER_ANIMATION"

    mblab = None
    targetWorkspace: StringProperty(name=None, default=None)

    def draw(self, context):
        layout = self.layout
        if _context is None:
            layout.menu('MB_MT_context', icon=MB_MT_root_menu.bl_icon)
            layout.separator()
            layout.operator('mb.mb_mt_open', icon="FILE_FOLDER")
            layout.separator()
            layout.operator('mb.mb_mt_create_structure')
        else:
            layout.menu('MB_MT_context', icon=MB_MT_root_menu.bl_icon)
            layout.separator()
            layout.operator('mb.mb_mt_open', icon="FILE_FOLDER")
            layout.operator('mb.mb_mt_save', icon="FILE_TICK")
            layout.operator('mb.mb_mt_publish', icon="EXPORT")
            layout.separator()
            layout.menu('MB_MT_manager', icon="ASSET_MANAGER")
            layout.separator()
            layout.operator('mb.mb_mt_load_file', icon="IMPORT")
            layout.separator()
            layout.operator('mb.mb_mt_modeling', icon="MESH_ICOSPHERE")
            layout.operator('mb.mb_mt_lookdev', icon="SHADERFX")
            layout.operator('mb.mb_mt_rigging', icon="CURVE_NCIRCLE")
            layout.menu('MB_MT_animation', icon="RENDER_ANIMATION")
        layout.separator()
        layout.operator('mb.mb_mt_reload')

    def menu_draw(self, context):
        self.layout.menu("MB_MT_root_menu")

    def execute(self, context):
        if self.targetWorkspace in bpy.data.workspaces:
            context.window.workspace = bpy.data.workspaces[self.targetWorkspace]
            return {'FINISHED'}

        success = bpy.ops.workspace.append_activate(idname=self.targetWorkspace, filepath=bpy.utils.user_resource('CONFIG', 'startup.blend'))
        if success == {'FINISHED'}:
            return success

        for p in Path(next(bpy.utils.app_template_paths())).rglob("startup.blend"):
            success = bpy.ops.workspace.append_activate(idname=self.targetWorkspace, filepath=str(p))
            if success == {'FINISHED'}:
                return success
        else:
            print('Workspace Swapper: Could not find the requested workspace "{}"'.format(self.targetWorkspace))
        return {'CANCELLED'}


CLASSES = [
    MB_MT_root_menu,

    MB_MT_context,
    MB_MT_context_open_project_folder,
    MB_MT_context_create_structure,
    MB_MT_context_open_context_folder,
    MB_MT_context_settings_scene,

    MB_MT_open,
    MB_MT_save,
    MB_MT_publish,

    MB_MT_manager,
    MB_MT_manager_reference,
    MB_MT_manager_backup,
    MB_MT_manager_context,

    MB_MT_load_file,

    MB_MT_modeling,
    MB_MT_lookdev,
    MB_MT_rigging,
    MB_MT_animation,
    MB_MT_animation_blast,
    MB_MT_animation_camera,

    MB_MT_reload,
]


@persistent
def load_handler(dummy, context):
    print(os.environ['MB_CONTEXT'])
    print(dummy)
    print(context)

    if 'MB_CONTEXT' in os.environ.keys():
        if os.environ['MB_CONTEXT'] != "null":
            _context = dict(json.loads(os.environ['MB_CONTEXT'])) or None

            if _context.get("step") == "Model":
                bpy.context.window.workspace = bpy.data.workspaces["Modeling"]

            if _context.get("step") == "LookDev":
                bpy.context.window.workspace = bpy.data.workspaces["Shading"]

            if _context.get("step") == "Animation":
                bpy.context.window.workspace = bpy.data.workspaces["Animation"]

            if _context.get("step") == "Assembly":
                bpy.context.window.workspace = bpy.data.workspaces["Layout"]

            if _context.get("step") == "Light":
                bpy.context.window.workspace = bpy.data.workspaces["Rendering"]


@persistent
def save_handler(path):
    if path:
        path = os.path.normpath(path)
        path = path.replace(".blend", ".png")
        path = path.replace("\\", "/")
        if os.path.exists(path):
            os.unlink(path)
    bpy.context.scene.render.filepath = path
    bpy.ops.render.opengl(animation=False, write_still=True, view_context=True)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(MB_MT_root_menu.menu_draw)
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.handlers.save_post.append(save_handler)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(MB_MT_root_menu.menu_draw)
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.save_post.remove(save_handler)
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
