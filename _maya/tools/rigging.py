from importlib import reload
from utils import util
from maya import cmds
from uuid import uuid4
from _maya.modules import asset
from _maya.modules import shot
import os
import sys
import time

reload(util)
reload(asset)
reload(shot)


class MBToolRigging:
    parent = None
    md_asset = None
    md_shot = None

    def __init__(self, parent):
        self.parent = parent
        self.md_asset = asset.MBAsset(parent)
        self.md_shot = shot.MBShot(parent)

    def export_alembic(self):
        try:
            self.data_shot = self.md_shot.get_data()
            get_all_transforms = cmds.ls(transforms=True)
            get_all_transforms = list(filter(lambda g: cmds.objExists(g + '.Export') and cmds.getAttr(g + '.Export'), get_all_transforms))
            try:
                get_all_transforms = list(map(lambda asset: {"name": asset.split(":")[1], "root": cmds.ls(asset, long=True)[0]}, get_all_transforms))
            except:
                get_all_transforms = list(map(lambda asset: {"name": asset, "root": cmds.ls(asset, long=True)[0]}, get_all_transforms))
            alembicArgs = util.get_params_alembic()
            if len(get_all_transforms) >= 1:
                cmds.progressWindow(title="Export cache", progress=0, status='Wait...', isInterruptable=True)
                total = len(get_all_transforms)
                exported = 0
                for n in range(len(get_all_transforms)):
                    node = get_all_transforms[n]
                    pct = (((exported + 1) * 100) / total)
                    cmds.progressWindow(edit=True, progress=pct, status="Export cache {}...".format("{}".format(node.get("name"))), isInterruptable=True)
                    data_path = {"asset_type": self.parent._context.get("asset_type"), "step": self.parent._context.get("step"), "asset": self.parent._context.get("asset"), "name": node.get("name"), "ext": "abc"}
                    path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("asset_publish_cache").format(**data_path))
                    path = os.path.normpath(path)
                    path = path.replace("\\", "/")
                    if not os.path.exists(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))
                    abc_export_cmd = "-frameRange 1 1 -{args} -dataFormat ogawa -root {root} -file '{file}'".format(args=alembicArgs, root=node.get("root"), file=path)
                    cmds.AbcExport(jobArg=abc_export_cmd)
                    exported = (exported + 1)
                    time.sleep(0.5)
                cmds.progressWindow(endProgress=1)
                cmds.confirmDialog(title="Export complete", message="EXPORTED:\n\n - {}\n\nCache successfully exported.".format("\n - ".join(list(map(lambda n: n.get("name"), get_all_transforms))), messageAlign="center", button=['Ok'], defaultButton="Ok"))
            else:
                cmds.confirmDialog(title="Select one node", message="Select only one node to export!", messageAlign="center", button=['Ok'], defaultButton="Ok")
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def add_export(self):
        selected = cmds.ls(sl=True)
        data_asset = self.md_asset.get_data()
        if len(selected) > 0:
            group = selected[0] or None
        else:
            asset_name = "{}_master_grp".format(data_asset.get("asset"))
            selected = cmds.ls(asset_name)
            group = selected[0] or None

        if group:
            group = cmds.ls(group, long=True)[0]

            uuid = str(uuid4())
            if data_asset:
                if data_asset.get("uuid"):
                    uuid = data_asset.get("uuid")

            if not cmds.objExists("{}.Export".format(group)):
                cmds.addAttr("{}".format(group), ln='Export', at='bool')
                cmds.setAttr("{}.Export".format(group), 1, e=True, keyable=True)
                try:
                    cmds.setAttr("{}.Export".format(group), lock=True)
                except:
                    pass

            if not cmds.objExists("{}.AssetId".format(group)):
                cmds.addAttr("{}".format(group), ln="AssetId", dt="string")
                cmds.setAttr("{}.AssetId".format(group), uuid, type="string")
                try:
                    cmds.setAttr("{}.AssetId".format(group), lock=True)
                except:
                    pass

            cmds.select(clear=True)
        else:
            cmds.confirmDialog(title='Object not selected', message='Select an object to add the attribute!', button=['OK'], defaultButton='OK')
