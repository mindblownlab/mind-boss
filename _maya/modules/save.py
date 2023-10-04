import os
import sys
from importlib import reload
from maya import cmds, mel
from _maya.utils import util
from _maya.modules import asset, shot

reload(util)
reload(asset)
reload(shot)


class MBSave:
    ui = None
    parent = None
    data_asset = None
    data_shot = None

    def __init__(self, parent):
        self.parent = parent
        self.data_asset = asset.MBAsset(parent)
        self.data_shot = shot.MBShot(parent)

    def saving(self):
        self.parent.close()
        self.ui = self.load_ui()
        self.parent.ui.main_layout.addWidget(self.ui)
        self.parent.setFixedSize(500, 300)

        self.ui.button_cancel.clicked.connect(self.parent.close)
        self.ui.button_save.clicked.connect(self.save)
        self.navigator()
        self.get_info()
        self.parent.show()

    def get_info(self):
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
            data_path = {
                "sequence": self.parent._context.get("sequence"),
                "shot": self.parent._context.get("shot"),
                "step": self.parent._context.get("step"),
                "step_shot": self.parent._context.get("step").lower(),
                "version": convert_version,
                "name": self.parent._context.get("shot").lower(),
                "ext": self.parent._project.get("engine").get("ext")
            }
            template_name = "shot_work"

        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get(template_name).format(**data_path))
        path = os.path.normpath(path)
        path = path.replace("\\", "/")

        self.ui.asset_name.setText(os.path.basename(path))
        self.ui.asset_version.setValue(version)
        self.ui.asset_preview.setText(os.path.basename(path))
        self.ui.asset_work.setText(path)

    def save(self):
        try:
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
                data_path = {
                    "sequence": self.parent._context.get("sequence"),
                    "shot": self.parent._context.get("shot"),
                    "step": self.parent._context.get("step"),
                    "step_shot": self.parent._context.get("step").lower(),
                    "version": convert_version,
                    "name": self.parent._context.get("shot").lower(),
                    "ext": self.parent._project.get("engine").get("ext")
                }
                template_name = "shot_work"
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get(template_name).format(**data_path))
            path = os.path.normpath(path)
            path = path.replace("\\", "/")

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            cmds.file(rename=path)
            cmds.file(save=True, type='mayaAscii')
            util.generate_thumbnail()
            self.parent.close()
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def load_ui(self):
        return util.load_ui(name='save', target=self.parent)

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">SAVE </span></p></body></html>')
            if self.parent._context is not None:
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">Notan | {type}</span><span style=" font-size:9pt;"><br/>{step} Asset {name}</span></p></body></html>'.format(type=self.parent._context.get("type").capitalize(), step=self.parent._context.get("step"), name=self.parent._context[self.parent._context.get('type')]))
            else:
                if self.parent._project:
                    self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">Notan | Project</span><span style=" font-size:9pt;"><br/>{project_name}</span></p></body></html>'.format(project_name=self.parent._project.get("name").upper()))
                else:
                    self.parent.ui.project_label.setText('')
        except:
            pass


from _maya.utils import resources
