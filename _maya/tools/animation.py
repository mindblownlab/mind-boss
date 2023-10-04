import json
from importlib import reload
from utils import util
from maya import cmds
from uuid import uuid4
from _maya.modules import shot
import os
import sys
import time

reload(util)
reload(shot)


class MBToolAnimation:
    parent = None
    md_shot = None
    data_shot = None

    def __init__(self, parent):
        self.parent = parent
        self.md_shot = shot.MBShot(parent)

    def collect_data(self):
        try:
            self.data_shot = self.md_shot.get_data()
            cameras = cmds.listCameras(p=True)
            cameras = list(filter(lambda cam: "Cam_" in cam, cameras))
            exports = cmds.ls("*:*_master_grp", "*_master_grp")
            exports = list(filter(lambda g: cmds.objExists(g + '.Export') and cmds.getAttr(g + '.Export'), exports))

            self.data_shot.update({"cameras": cameras, "exports": exports})
            self.md_shot.update_data(data=self.data_shot)
            cmds.select(clear=True)
            cmds.confirmDialog(title="Collected", message="Scene data collected!", messageAlign="center", button=['Ok'], defaultButton="Ok")

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def export_alembic(self):
        try:
            self.data_shot = self.md_shot.get_data()
            get_all_transforms = cmds.ls(transforms=True)
            get_all_transforms = list(filter(lambda g: cmds.objExists(g + '.Export') and cmds.getAttr(g + '.Export'), get_all_transforms))
            try:
                get_all_transforms = list(map(lambda asset: {"name": asset.split(":")[1], "root": cmds.ls(asset, long=True)[0], "filename": cmds.ls(asset, long=True)[0].split(":")[-1:][0]}, get_all_transforms))
            except:
                get_all_transforms = list(map(lambda asset: {"name": asset.split("|")[-1:][0], "root": cmds.ls(asset, long=True)[0], "filename": asset.split("|")[-1:][0]}, get_all_transforms))

            get_all_cameras = cmds.listCameras(p=True)
            get_all_cameras = list(filter(lambda cam: "Cam_" in cam, get_all_cameras))
            try:
                get_all_cameras = list(map(lambda cam: {"name": cam.split(":")[1], "root": cmds.ls(cam, long=True)[0], "filename": cam.split(":")[1]}, get_all_cameras))
            except:
                get_all_cameras = list(map(lambda cam: {"name": cam.split("|")[-1:][0], "root": cmds.ls(cam, long=True)[0], "filename": cam.split("|")[-1:][0]}, get_all_cameras))

            all_nodes = get_all_transforms + get_all_cameras
            frame_start, frame_end = self.data_shot.get("frame_range")
            alembicArgs = util.get_params_alembic()

            if len(all_nodes) >= 1:
                cmds.progressWindow(title="Export cache", progress=0, status='Wait...', isInterruptable=True)
                total = len(all_nodes)
                exported = 0
                all_nodes = self.fix_duplicate_name(all_nodes)
                for n in range(len(all_nodes)):
                    node = all_nodes[n]
                    pct = (((exported + 1) * 100) / total)
                    cmds.progressWindow(edit=True, progress=pct, status="Export cache {}...".format("{}".format(node.get("filename"))), isInterruptable=True)
                    data_path = {"sequence": self.parent._context.get("sequence"), "shot": self.parent._context.get("shot"), "name": node.get("filename")}
                    path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("shot_publish_cache").format(**data_path))
                    path = os.path.normpath(path)
                    path = path.replace("\\", "/")
                    if not os.path.exists(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))
                    abc_export_cmd = "-frameRange {start} {end} -{args} -dataFormat ogawa -root {root} -file '{file}'".format(start=frame_start, end=frame_end, args=alembicArgs, root=node.get("root"), file=path)
                    cmds.AbcExport(jobArg=abc_export_cmd)
                    exported = (exported + 1)
                    time.sleep(0.5)
                cmds.progressWindow(endProgress=1)
                cmds.confirmDialog(title="Export complete", message="EXPORTED:\n\n - {}\n\nCache successfully exported.".format("\n - ".join(list(map(lambda n: n.get("name"), all_nodes))), messageAlign="center", button=['Ok'], defaultButton="Ok"))
            else:
                cmds.confirmDialog(title="Select one node", message="Select only one node to export!", messageAlign="center", button=['Ok'], defaultButton="Ok")
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def fix_duplicate_name(self, data):
        duplicates = []
        for cache in data:
            duplicates.append(cache['name'])
        total_per_item = {i: duplicates.count(i) for i in duplicates}
        for item in total_per_item:
            y = 0
            for o in range(len(data)):
                opt = data[o]
                if item == opt['name']:
                    if y > 0:
                        data[o]["name"] = "{name}{indice}".format(name=opt['name'], indice=y)
                    y += 1
        return data
