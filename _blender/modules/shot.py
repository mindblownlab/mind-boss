import copy
import os
import sys
from importlib import reload
from _blender.utils import util

reload(util)


class MBShot:
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def check_data(self):
        try:
            data_path = {
                "sequence": self.parent._context.get("sequence"),
                "shot": self.parent._context.get("shot")
            }
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("shot_data").format(**data_path))
            if not os.path.exists(path):
                path_folder = os.path.dirname(path)
                if not os.path.exists(path_folder):
                    os.makedirs(path_folder)
                data = copy.deepcopy(self.parent._context)
                data.update({"frame_range": [1, 120]})
                progress = {}
                for prg in self.parent._project.get("steps").get("shots"):
                    progress[prg] = "rts"
                data.update({"progress": progress})
                util.storage(data, path, replace=True)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def get_data(self):
        try:
            if self.parent._context.get("type") == "shot":
                current_shot = copy.deepcopy(self.parent._context)
                asset = list(filter(lambda sht: sht.get("shot") == current_shot.get("shot"), self.parent._shots))
                if asset:
                    return asset[0]
                else:
                    return self.parent._context
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def update_data(self, data):
        try:
            data_path = {"sequence": self.parent._context.get("sequence"), "shot": self.parent._context.get("shot")}
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("shot_data").format(**data_path))
            path = os.path.normpath(path)
            path = path.replace("\\", "/")
            if os.path.exists(path) and data:
                util.storage(path=path, data=data, replace=True)

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))
