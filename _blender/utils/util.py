import os
import sys
from library import yaml
import math
import bpy
import os.path, time
from unicodedata import normalize
from glob import glob
from PySide2.QtUiTools import QUiLoader


def get_root_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def storage(data=None, path=None, replace=False):
    try:
        if data:
            if replace:
                with open(path, 'w') as outfile:
                    yaml.dump(data, outfile, default_flow_style=False)

            if not os.path.exists(path):
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with open(path, 'w') as outfile:
                    yaml.dump(data, outfile, default_flow_style=False)
            else:
                return None
        else:
            if os.path.exists(path):
                with open(path) as fl:
                    return yaml.safe_load(fl)
            else:
                return None
    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))
        return None


def get_size_file(path=None):
    file_stats = os.stat(path)
    return {
        "size": file_stats.st_size,
        "bytes": convert_size(file_stats.st_size)
    }


def get_data_file(path):
    return {
        "created": time.ctime(os.path.getctime(path)),
        "last_modified": time.ctime(os.path.getmtime(path)),
    }


def convert_size(size):
    if size == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return "%s %s" % (s, size_name[i])


def no_accents(value=""):
    return normalize('NFKD', value).encode('ASCII', 'ignore').decode('ASCII')


def get_settings(file):
    if os.path.exists(file):
        with open(file, 'r') as data:
            return yaml.safe_load(data)


def set_storage(data, file):
    file = file.replace('\\', '/')
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, 'w') as seq_file:
        yaml.dump(data, seq_file, default_flow_style=False)


def get_style(name='style'):
    path = os.path.join(get_root_path(), 'ui', '{}.qss'.format(name))
    with open(path, 'r') as fh:
        return fh.read()


def get_ui(name='main'):
    return os.path.join(get_root_path(), 'ui', '{}.ui'.format(name))


def load_ui(name='main', target=None):
    loader = QUiLoader()
    return loader.load(get_ui(name), target)


def get_ffmpeg():
    try:
        return os.path.normpath(os.path.join(get_root_path(), "lib", "ffmpeg", "bin", "ffmpeg.exe"))
    except:
        return "ffmpeg path error"


def get_database(name="templates"):
    path = os.path.join(get_root_path(), "database", "{}.yml".format(name))
    path = os.path.normpath(path)
    return storage(path=path)


def get_templates():
    templates = os.path.join(get_root_path(), "database", "templates.yml")
    templates = os.path.normpath(templates)
    return storage(path=templates)


def get_last_version(parent=None):
    try:
        if parent._context.get("type") == "asset":
            data_path = {
                "asset_type": parent._context.get("asset_type"),
                "asset": parent._context.get("asset"),
                "step": parent._context.get("step"),
                "step_asset": parent._context.get("step").lower(),
                "version": 1,
                "name": "asset",
                "ext": parent._project.get("engine").get("ext")
            }
            template_name = "asset_work"
        else:
            template_name = "shot_work"
            data_path = {
                "sequence": parent._context.get("sequence"),
                "shot": parent._context.get("shot"),
                "step": parent._context.get("step"),
                "step_shot": parent._context.get("step").lower(),
                "version": 1,
                "name": "asset",
                "ext": parent._project.get("engine").get("ext")
            }
        path = os.path.join(parent._project.get("path"), parent._templates.get(template_name).format(**data_path))
        path = os.path.dirname(os.path.normpath(path))
        files = glob("{}/*.{}".format(path, parent._project.get("engine").get("ext")))
        if len(files) >= 1:
            return (len(files) + 1)
        else:
            return 1
    except:
        return 1


def generate_thumbnail(target=None):
    try:
        path = target or bpy.data.filepath
        if path:
            path = os.path.normpath(path)
            path = path.replace(".blend", ".png")
            path = path.replace("\\", "/")
            if os.path.exists(path):
                os.unlink(path)
            # sce = bpy.context.scene.name
            # bpy.data.scenes[sce].render.filepath = path
            bpy.context.scene.render.filepath = path
            time.sleep(.200)
            bpy.ops.render.opengl(animation=False, write_still=True, view_context=True)
            # time.sleep(.200)
            # bpy.render.opengl(write_still=True)

            return True
        else:
            return False
    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))
        return False

def get_context():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        context_override = {
                            "window": window,
                            "screen": window.screen,
                            "area": area,
                            "region": region,
                            "scene": bpy.context.scene,
                        }
                        return context_override
    return None