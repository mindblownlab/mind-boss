import json
import os
import bpy
from importlib import reload
from PySide2 import QtWidgets, QtCore
from _blender.utils import util
from _blender.modules import open, project, shot, asset, scene, save, load, manager

reload(open)
reload(util)
reload(asset)
reload(shot)
reload(scene)
reload(project)
reload(load)
reload(manager)
reload(save)


class MBMain(QtWidgets.QMainWindow):
    _context = None
    _templates = None
    _project = None
    _shots = []
    _assets = []
    _users = []
    _projects = []
    _engines = []

    app = None
    mb_open = None
    mb_asset = None
    mb_shot = None
    mb_project = None
    mb_scene = None
    mb_save = None
    mb_load = None
    mb_manager = None

    def __init__(self, parent=None, app=None):
        super(MBMain, self).__init__(parent)
        self.app = app
        self.setStyleSheet(util.get_style())
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setWindowTitle('MBLab Manager')

        self.ui = util.load_ui(target=self)
        self.setCentralWidget(self.ui.main_container)

        self._templates = util.get_templates()
        self._shots = util.storage(path=os.path.join(util.get_root_path(), 'database', 'shots.yml'))
        self._assets = util.storage(path=os.path.join(util.get_root_path(), 'database', 'assets.yml'))
        self._publishes = util.storage(path=os.path.join(util.get_root_path(), 'database', 'publishes.yml'))
        self._users = util.storage(path=os.path.join(util.get_root_path(), 'database', 'users.yml'))
        self._projects = util.storage(path=os.path.join(util.get_root_path(), 'database', 'projects.yml'))
        self._engines = util.storage(path=os.path.join(util.get_root_path(), 'database', 'engines.yml'))
        self.menu()

        self.mb_project = project.MBProject(self)
        self.mb_asset = asset.MBAsset(self)
        self.mb_shot = shot.MBShot(self)
        self.mb_scene = scene.MBScene(self)
        self.mb_open = open.MBOpen(self)
        self.mb_save = save.MBSave(self)
        self.mb_load = load.MBLoad(self)
        self.mb_manager = manager.MBManager(self)

        self.ui.set_project.clicked.connect(self.mb_project.set_project)

    def menu(self):
        if 'MB_CONTEXT' in os.environ.keys():
            if os.environ['MB_CONTEXT'] != "null":
                self._context = dict(json.loads(os.environ['MB_CONTEXT'])) or None

        if 'MB_PROJECT' in os.environ.keys():
            if os.environ['MB_PROJECT'] != "null":
                self._project = dict(json.loads(os.environ['MB_PROJECT'])) or None
                self.ui.set_project.setVisible(False)
        else:
            self.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">FILE OPEN </span></p></body></html>')

    def refresh(self):
        self.menu()

    def startup_context(self):
        self.close()
        self.refresh()

    def closeEvent(self, event):
        try:
            if self.ui.main_layout.count() > 0:
                for i in range(self.ui.main_layout.count()):
                    item = self.ui.main_layout.takeAt(i)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
        except:
            pass

        try:
            self.mb_blast.closeEvent()
        except:
            pass


from _blender.utils import resources
