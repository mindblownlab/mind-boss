import os
import sys
from library import yaml
import math
from maya import cmds, mel
import os.path, time
from unicodedata import normalize
from glob import glob
from uuid import uuid4
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtUiTools import QUiLoader


def get_root_path():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def get_root_project():
    return os.path.normpath(cmds.workspace(query=True, rootDirectory=True))


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


def viewport_preview(active=True):
    mel.eval("paneLayout -e -manage false $gMainPane")
    try:
        viewport = cmds.getPanel(withFocus=True)
        if viewport != "modelPanel4":
            viewport = "modelPanel4"

        if active:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(viewport, e=True,
                             allObjects=False,
                             polymeshes=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )
            mel.eval('generateAllUvTilePreviews;')
            cmds.grid(toggle=False)
        else:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(viewport, e=True,
                             allObjects=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )
            cmds.grid(toggle=True)
    except:
        pass

    mel.eval("paneLayout -e -manage true $gMainPane")


def generate_thumbnail(target=None):
    try:
        path = target or cmds.file(q=True, sn=True)
        if path:
            path = os.path.normpath(path)
            path = path.replace(".ma", ".jpg")
            try:
                check_cameras = cmds.ls("cam_shot_*") + cmds.ls("Cam_shot_*") or []
                if len(check_cameras) <= 0:
                    cmds.select("*master_grp")
                    cmds.select(clear=True)
            except:
                pass

            if os.path.exists(path):
                os.unlink(path)

            viewport_preview()
            time.sleep(.4)
            cmds.playblast(
                compression='JPG',
                format='image',
                percent=100,
                quality=100,
                viewer=False,
                offScreen=True,
                frame=int(cmds.currentTime(query=True)),
                forceOverwrite=True,
                completeFilename=path,
                widthHeight=[640, 400],
                rawFrameNumbers=False,
                framePadding=4)
            viewport_preview(active=False)
            cmds.file(save=True)
            return True
        else:
            return False
    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))
        return False


def get_templates():
    templates = os.path.join(get_root_path(), "database", "templates.yml")
    templates = os.path.normpath(templates)
    return storage(path=templates)


def get_project_data():
    data = os.path.join(get_root_project(), "data", "project.yml")
    data = os.path.normpath(data)
    if os.path.exists(data):
        return storage(path=data)
    else:
        return None


def get_context_data(path):
    if os.path.exists(path):
        return storage(path=path)
    else:
        return None


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
                "version": 1,
                "name": "asset",
                "ext": parent._project.get("engine").get("ext")
            }
        path = os.path.join(parent._project.get("path"), parent._templates.get(template_name).format(**data_path))
        path = os.path.dirname(os.path.normpath(path))
        files = glob("{}/*.ma".format(path))
        if len(files) >= 1:
            return (len(files) + 1)
        else:
            return 1
    except:
        return 1


def get_conext_path(path=None):
    if path:
        path = os.path.normpath(path)
        path = path.replace("\\", "/")


def set_export_param():
    selected = cmds.ls(sl=True)
    if len(selected) > 0:
        assetName = selected[0]
        if "master_grp" not in assetName:
            assetName = cmds.rename(selected[0], "{}_master_grp".format(assetName))
        uuid = str(uuid4())

        if not cmds.objExists("{}.Export".format(assetName)):
            cmds.addAttr("{}".format(assetName), ln='Export', at='bool')
            cmds.setAttr("{}.Export".format(assetName), 1, e=True, keyable=True)
            cmds.setAttr("{}.Export".format(assetName), lock=True)

        if not cmds.objExists("{}.AssetId".format(assetName)):
            cmds.addAttr("{}".format(assetName), ln="AssetId", dt="string")
            cmds.setAttr("{}.AssetId".format(assetName), uuid, type="string")
            cmds.setAttr("{}.AssetId".format(assetName), lock=True)


def get_params_alembic_framerange():
    frame_start = int(cmds.playbackOptions(q=True, min=True))
    frame_end = int(cmds.playbackOptions(q=True, max=True))
    args = ["uvWrite", "stripNamespaces", "worldSpace", "writeVisibility", "writeUVSets"]
    alembicArgs = " -".join(args)
    return (frame_start, frame_end, alembicArgs)


def get_params_alembic():
    args = ["uvWrite", "stripNamespaces", "worldSpace", "writeVisibility", "writeUVSets"]
    return " -".join(args)


def main_maya():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def get_style(name='style'):
    path = os.path.join(get_root_path(), 'ui', '{}.qss'.format(name))
    with open(path, 'r') as fh:
        return fh.read()


def get_ui(name='main'):
    return os.path.join(get_root_path(), 'ui', '{}.ui'.format(name))


def load_ui(name='main', target=None):
    loader = QUiLoader()
    return loader.load(get_ui(name), target)


def get_path_project():
    try:
        path_output = cmds.fileDialog2(fileMode=2)
        if len(path_output) > 0:
            return path_output[0]
        else:
            return False
    except:
        return False


def get_ffmpeg():
    try:
        return os.path.normpath(os.path.join(get_root_path(), "lib", "ffmpeg", "bin", "ffmpeg.exe"))
    except:
        return "ffmpeg path error"
