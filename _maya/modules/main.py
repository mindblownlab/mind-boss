import json
import os
import sys
from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds, mel
from importlib import reload
from _maya.utils import util
from _maya.modules import project, open, save, load, blast, scene, asset, shot, info, manager
from _maya.tools import modeling, lookdev, rigging, animation

reload(util)
reload(project)
reload(open)
reload(save)
reload(load)
reload(blast)
reload(scene)
reload(asset)
reload(shot)
reload(info)
reload(manager)

reload(rigging)
reload(animation)

root_menu = "mind_menu"
menu_label = "MBLab"


class MBMain(QtWidgets.QMainWindow):
    _context = None
    _templates = None
    _project = None
    _shots = []
    _assets = []
    _projects = []
    _engines = []
    _users = []

    mb_project = None
    mb_open = None
    mb_save = None
    mb_load = None
    mb_blast = None
    mb_scene = None
    mb_asset = None
    mb_shot = None
    mb_info = None
    mb_manager = None

    tool_rig = None
    tool_anim = None

    def __init__(self):
        super(MBMain, self).__init__(util.main_maya())
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
        self.mb_open = open.MBOpen(self)
        self.mb_save = save.MBSave(self)
        self.mb_load = load.MBLoad(self)
        self.mb_blast = blast.MBBLast(self)
        self.mb_scene = scene.MBScene(self)
        self.mb_info = info.MBInfo(self)
        self.mb_manager = manager.MBManager(self)

        self.tool_rig = rigging.MBToolRigging(self)
        self.tool_anim = animation.MBToolAnimation(self)

        self.ui.set_project.clicked.connect(self.mb_project.set_project)

    def menu(self):
        try:
            if 'MB_CONTEXT' in os.environ.keys():
                if os.environ['MB_CONTEXT'] != "null":
                    self._context = dict(json.loads(os.environ['MB_CONTEXT'])) or None

            if 'MB_PROJECT' in os.environ.keys():
                if os.environ['MB_PROJECT'] != "null":
                    self._project = dict(json.loads(os.environ['MB_PROJECT'])) or None
                    self.ui.set_project.setVisible(False)
            else:
                self.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">FILE OPEN </span></p></body></html>')

            if cmds.menu(root_menu, exists=1):
                cmds.deleteUI(root_menu, menu=1)

            gMainWindow = mel.eval("global string $gMainWindow;$temp = $gMainWindow")
            cmds.menu(root_menu, label=menu_label, parent=gMainWindow, tearOff=1, allowOptionBoxes=1)

            if self._context is None:
                if self._project is None:
                    cmds.menuItem(label="Set Project", image="project.png", parent=root_menu, command=lambda x=None: self.mb_project.set_project())
                else:
                    menu_project = cmds.menuItem(label="Project {}".format(self._project.get("name")), image="project.png", parent=root_menu, command=lambda x=None: self.mb_project.set_project(), subMenu=True)
                    cmds.menuItem(label="Open project folder", image="proj_folder.png", parent=menu_project, command=lambda x=None: self.mb_project.open_project())

                cmds.menuItem(divider=True, parent=root_menu)
                cmds.menuItem(label="File Open", image="folder.png", parent=root_menu, command=lambda x=None: self.mb_open.opening())
                cmds.menuItem(divider=True, parent=root_menu)
                cmds.menuItem(label="Create folder structure", image="publish.png", parent=root_menu, command=lambda x=None: self.mb_project.create_structure())

            else:
                if self._context.get("type") == "asset":
                    menu_project = cmds.menuItem(label="{}, {} {}".format(self._context.get("step"), self._context.get("type").capitalize(), self._context.get("asset")), image="project.png", parent=root_menu, subMenu=True)
                else:
                    menu_project = cmds.menuItem(label="{}, {} {}".format(self._context.get("step"), self._context.get("type").capitalize(), self._context.get("shot")), image="project.png", parent=root_menu, subMenu=True)

                cmds.menuItem(divider=True, parent=root_menu)
                cmds.menuItem(label="File Open", parent=root_menu, image="folder.png", command=lambda x=None: self.mb_open.opening())
                cmds.menuItem(label="Open Project folder", parent=menu_project, image="proj_folder.png", command=lambda x=None: self.mb_project.open_project())
                cmds.menuItem(label="Open Asset {} folder".format(self._context.get("step")), image="proj_folder.png", parent=menu_project, command=lambda x=None: self.mb_project.open_context())
                cmds.menuItem(label="Set and Check Scene settings", image="proj_cog.png", parent=menu_project, command=lambda x=None: self.mb_scene.set_scene())
                cmds.menuItem(label="File Save", image="saving.png", parent=root_menu, command=lambda x=None: self.mb_save.saving())
                menu_pub = cmds.menuItem(label="Publish", image="publish.png", parent=root_menu, command=lambda x=None: self.mb_scene.publish(), subMenu=True)
                cmds.menuItem(label="File", parent=menu_pub, image="pub_file.png", command=lambda x=None: self.mb_scene.publish())
                if self._context.get("type") == "asset":
                    cmds.menuItem(label="Cache asset", parent=menu_pub, image="pub_alembic.png", command=lambda x=None: self.tool_rig.export_alembic())
                else:
                    cmds.menuItem(label="Cache animation", parent=menu_pub, image="pub_alembic.png", command=lambda x=None: self.tool_anim.export_alembic())
                cmds.menuItem(label="Camera", parent=menu_pub, image="pub_cam.png")

                cmds.menuItem(divider=True, parent=root_menu)
                menu_manager = cmds.menuItem(label="Manager", image="manager.png", parent=root_menu, subMenu=True)
                cmds.menuItem(label="Reference", image="manager.png", parent=menu_manager)
                cmds.menuItem(label="Backup", image="man_backup.png", parent=menu_manager)
                cmds.menuItem(label="{}".format(self._context.get("type").capitalize()), image="man_backup.png", parent=menu_manager, command=lambda x=None: self.mb_manager.loader())

                cmds.menuItem(divider=True, parent=root_menu)
                cmds.menuItem(label="Load File", image="load.png", parent=root_menu, command=lambda x=None: self.mb_load.loading())

                # if self._context.get("type") == "asset":
                cmds.menuItem(divider=True, parent=root_menu)
                tool_modeling = cmds.menuItem(label="Modeling", parent=root_menu, image="modeling.png")
                tool_lookdev = cmds.menuItem(label="Lookdev", parent=root_menu, image="publish.png")

                tool_rigging = cmds.menuItem(label="Rigging", parent=root_menu, image="rigging.png", subMenu=True)
                cmds.menuItem(label="Add attribute export", parent=tool_rigging, image="cog.png", command=lambda x=None: self.tool_rig.add_export())

                if self._context.get("type") == "shot":
                    tool_animation = cmds.menuItem(label="Animation", parent=root_menu, image="animation.png", subMenu=True)
                    # cmds.menuItem(label="Collect data shot", parent=tool_animation, image="anim_data.png", command=lambda x=None: self.tool_anim.collect_data())
                    cmds.menuItem(label="Playblast", image="anim_blast.png", parent=tool_animation, command=lambda x=None: self.mb_blast.open())

                cmds.menuItem(divider=True, parent=root_menu)
                cmds.menuItem(label="Reload", image="refresh.png", parent=root_menu, command=lambda x=None: self.refresh())
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def refresh(self):
        if cmds.menu(root_menu, exists=1):
            cmds.deleteUI(root_menu, menu=1)
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


from _maya.utils import resources
