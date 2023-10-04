import os
import sys
from importlib import reload
from _maya.utils import util
from maya import cmds, mel
from PySide2 import QtWidgets, QtCore, QtGui
import copy

reload(util)


class MBScene:
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def publish(self):
        try:
            saved = cmds.file(q=True, sn=True) or None
            convert_version = "{:03d}".format(1)
            if "assets" in saved:
                data_path = {
                    "asset_type": self.parent._context.get("asset_type"),
                    "asset": self.parent._context.get("asset"),
                    "step": self.parent._context.get("step"),
                    "step_asset": self.parent._context.get("step").lower(),
                    "version": convert_version,
                    "name": self.parent._context.get("asset"),
                    "ext": self.parent._project.get("engine").get("ext")
                }
                template_name = "asset_publish"
            else:
                filename = "{}_{}".format(self.parent._context.get("shot").lower(), self.parent._context.get("step").lower())
                data_path = {
                    "sequence": self.parent._context.get("sequence"),
                    "shot": self.parent._context.get("shot"),
                    "step": self.parent._context.get("step"),
                    "step_shot": self.parent._context.get("step").lower(),
                    "version": convert_version,
                    "name": filename,
                    "ext": self.parent._project.get("engine").get("ext")
                }
                template_name = "shot_publish"
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get(template_name).format(**data_path))
            path = os.path.normpath(path)
            path = path.replace("\\", "/")
            asset_path = os.path.dirname(path)

            if not os.path.exists(asset_path):
                os.makedirs(asset_path)

            if self.parent._context.get("step") == "LookDev":
                try:
                    if cmds.objExists("{}_master_grp".format(self.parent._context.get("asset"))):
                        cmds.select("{}_master_grp".format(self.parent._context.get("asset")), r=True)
                    cmds.file(path, force=True, options="v=0;", typ="mayaAscii", es=True, preserveReferences=True, constraints=False)
                except:
                    if cmds.objExists("*:{}_master_grp".format(self.parent._context.get("asset"))):
                        cmds.select("*:{}_master_grp".format(self.parent._context.get("asset")), r=True)
                    cmds.file(path, force=True, options="v=0;", typ="mayaAscii", es=True, preserveReferences=True, constraints=False)
            else:
                cmds.file(path, force=True, options="v=0;", type="mayaAscii", pr=True, ea=True)

            while util.generate_thumbnail(target=path):
                cmds.select(clear=True)
                QtWidgets.QMessageBox.question(None, "Publish", "File published successfully!", QtWidgets.QMessageBox.Ok)
                break
            cmds.file(save=True)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def check_scene(self):
        message = '''
            <b>CHECK SCENE SETTINGS</b><br/>
            ----------------------------------<br/>
            Resolution: {resolution}<br/>
            FPS: {fps}<br/>
            Aspect: {aspect}<br/>
            Frame range: {framerange}'''.format(
            resolution="x".join(list(map(lambda r: str(r), self.parent._project.get('resolution')))),
            fps=self.parent._project.get('fps'),
            aspect=int(self.parent._project.get("aspect")),
            framerange="-".join(list(map(lambda r: str(r), self.get_context_data().get('frame_range')))))

        cmds.confirmDialog(title='Check Scene', message=message, button=['OK'], defaultButton='OK')

    def set_scene(self):
        project_data = self.parent.mb_project.get_data()
        width, height = project_data.get('resolution')
        frame_start, frame_end = self.get_context_data().get("frame_range")

        cmds.currentUnit(time='film')
        cmds.setAttr("defaultResolution.width", int(width))
        cmds.setAttr("defaultResolution.height", int(height))

        cmds.playbackOptions(minTime=int(frame_start), maxTime=int(frame_end), animationStartTime=int(frame_start), animationEndTime=int(frame_end))
        cmds.setAttr("defaultRenderGlobals.startFrame", int(frame_start))
        cmds.setAttr("defaultRenderGlobals.endFrame", int(frame_end))
        cmds.setAttr("defaultResolution.dar", int(project_data.get("aspect")))
        #
        self.check_scene()
        saved = cmds.file(q=True, sn=True) or None
        if saved:
            cmds.file(save=True, type='mayaAscii')

    def get_context_data(self):
        if self.parent._context.get("type") == "shot":
            data = list(filter(lambda sht: sht.get("shot") == self.parent._context.get("shot"), self.parent._shots))[0]
        else:
            data = list(filter(lambda sht: sht.get("asset") == self.parent._context.get("asset"), self.parent._assets))[0]
        return copy.deepcopy(data)
