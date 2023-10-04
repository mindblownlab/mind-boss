import copy
import json
import os
import sys
from importlib import reload
from _blender.utils import util

reload(util)


class MBProject:
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def set_project(self):
        try:
            pass
            # check_path = util.get_path_project()
            # if check_path:
            #     path = os.path.normpath(check_path)
            #     project_name = "Project_Default"
            #     result = cmds.promptDialog(title='Set project name', message='Enter Name:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
            #     if result == 'OK':
            #         project_name = cmds.promptDialog(query=True, text=True)
            #
            #     path = os.path.join(path, project_name)
            #     path = os.path.normpath(path)
            #
            #     data_project_path = os.path.join(path, 'data', 'project.yml')
            #     project = {
            #         "name": project_name,
            #         "frame_range": [1, 72],
            #         "fps": 24,
            #         "aspect": 1,
            #         "resolution": [1920, 1080],
            #         "render": {"name": "arnold", "plugin": "mtoa"},
            #         "engine": {
            #             "name": cmds.about(product=True),
            #             "ext": "ma",
            #         },
            #         "path": path,
            #         "steps": {
            #             "assets": ["Model", "LookDev", "Rig"],
            #             "shots": ["Animation", "Assembly", "Light"]
            #         },
            #         "status": ["rts", "in progress", "polishing", "standby"],
            #         "playblast": {
            #             "format": ["MP4", "MOV"],
            #             "resolution": {
            #                 "HD_1080": [1920, 1080],
            #                 "HD_720": [1280, 720],
            #                 "HD_540": [960, 540],
            #                 "Custom": [3000, 3000],
            #             },
            #             "steps": ["Story Poses", "Blocking", "Blocking Plus", "Spline/Polish", "Final"]
            #         }
            #     }
            #     context = {
            #         "project": project,
            #         "context": None,
            #     }
            #     util.set_storage(context, data_project_path)
            #     mel.eval('setProject("{path}")'.format(path=path.replace("\\", "/")))
            #
            #     if not os.path.exists(os.path.join(path, 'work')):
            #         self.create_structure(project=project)
            #
            #     # QtCore.QTimer.singleShot(300, self.parent.startup_context)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("C: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def open_project(self):
        os.startfile(self.parent._project.get("path"))

    def open_context(self):
        version = util.get_last_version(self.parent)
        convert_version = "{:03d}".format(version)
        if self.parent._context.get("type") == "asset":
            data_path = {
                "asset_type": self.parent._context.get("asset_type"),
                "asset": self.parent._context.get("asset"),
                "step": self.parent._context.get("step"),
                "step_asset": self.parent._context.get("step").lower(),
                "version": convert_version,
                "name": self.parent._context.get("asset"),
                "ext": self.parent._project.get("engine").get("ext")
            }
            template_name = "asset_work"
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
            template_name = "shot_work"

        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get(template_name).format(**data_path))
        path = os.path.normpath(path)
        path = path.replace("\\", "/")
        path = os.path.dirname(path)

        if not os.path.exists(path):
            os.makedirs(path)

        os.startfile(path)

    def get_data(self):
        try:
            current_project = copy.deepcopy(self.parent._project)
            project = list(filter(lambda prj: prj.get("name") == current_project.get("name"), self.parent._projects))
            if project:
                project = project[0]
                project.update({
                    "engine": current_project.get("engine"),
                    "path": current_project.get("path"),
                })
                return project
            else:
                return self.parent._project
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def create_structure(self, project=None):
        folders = ['asset', 'cache', 'images', 'movies', 'scenes', 'sourceimages', 'work', 'work/assets', 'work/scenes']

        if self.parent._project is None:
            prj = project
        else:
            prj = self.parent._project
        for folder in folders:
            path = os.path.join(prj.get("path"), folder)
            if not os.path.exists(path):
                os.makedirs(path)

        for shot in self.parent._shots:
            path_shot = os.path.join(prj.get("path"), "work", "scenes", shot.get("sequence"), shot.get("shot"))
            for step in prj.get("steps").get("shots"):
                path_shot_step = os.path.join(path_shot, step)
                if not os.path.exists(path_shot_step):
                    os.makedirs(path_shot_step)

        for asset in self.parent._assets:
            path_asset = os.path.join(prj.get("path"), "work", "assets", asset.get("asset_type"), asset.get("asset"))
            for step in prj.get("steps").get("assets"):
                path_asset_step = os.path.join(path_asset, step)
                if not os.path.exists(path_asset_step):
                    os.makedirs(path_asset_step)

        self.parent.refresh()
