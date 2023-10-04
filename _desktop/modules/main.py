import copy
import json
import sys
import os
import shutil
from PyQt5 import QtWidgets, QtCore, QtGui
from importlib import reload
from _desktop.utils import util
from _blender.lib.PIL import Image, ImageQt

reload(util)


class MBMain(QtWidgets.QMainWindow):
    project = None

    def __init__(self):
        super(MBMain, self).__init__()
        self.setStyleSheet(util.get_style(name='project_style'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.resize(400, 800)
        self.setMinimumSize(QtCore.QSize(400, 0))
        self.statusBar().showMessage('Develop by MBLab - v1.0.0')
        self.setWindowTitle('MBLab Manager')

        projects = util.get_database(name='projects')
        engines = util.get_database(name='engines')
        engines = list(filter(lambda eng: os.path.exists(eng.get("path")), engines))

        self.ui = util.load_ui(target=self, name="app")
        self.ui.panels.setCurrentIndex(0)
        self.setCentralWidget(self.ui.centralwidget)
        self.setMenuBar(self.ui.menubar)

        self.ui.projects.clear()
        self.ui.engines.clear()
        self.ui.tools.clear()

        if not 'PYTHONPATH' in os.environ.keys():
            os.environ['PYTHONPATH'] = os.path.join(util.get_root_path(), 'Python')

        for proj in projects:
            self.item(proj)

        for engine in engines:
            self.item_engine(engine)

        self.ui.btn_back.clicked.connect(lambda evt: self.ui.panels.setCurrentIndex(0))
        self.show()

    def item(self, data):
        ui_item = util.load_ui(name="project_item")
        root_menu = QtWidgets.QTreeWidgetItem(self.ui.projects)

        frame_start, frame_end = data.get("frame_range")
        text = """<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{project}<br/></span><b>FPS:</b> {fps}, <b>Frames:</b> {frames}<br/><b>Status:</b> {status}<br/>Render: {render}</p></body></html>""".format(
            fps=data.get("fps"),
            render=data.get("render").get("name"),
            frames="{}-{}".format(frame_start, frame_end),
            status=data.get("current_status"),
            project=data.get("name"))

        ui_item.detail.setText(text)
        proj_thumb = os.path.join(util.get_root_path(), "_desktop", "storage", "projects", data.get("name"), "thumb.png")
        if not os.path.exists(proj_thumb):
            proj_thumb = os.path.join(util.get_root_path(), "_desktop", "storage", "projects", "thumb.png")
        pixmap = QtGui.QPixmap(proj_thumb)
        ui_item.thumb.setPixmap(pixmap)

        root_menu.setData(0, QtCore.Qt.UserRole, {**data})
        self.ui.projects.setItemWidget(root_menu, 0, ui_item)
        ui_item.proj_open.clicked.connect(lambda evt: self.open_project(data))

    def item_engine(self, data):
        ui_item = util.load_ui(name="item_engine")
        root_menu = QtWidgets.QTreeWidgetItem(self.ui.engines)
        main_item = ui_item.findChild(QtWidgets.QWidget, "main_engine_item")
        text = """<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{engine}<br/></span><b>Version:</b> {version}</p></body></html>""".format(
            version=data.get("version"),
            engine=data.get("name"))

        ui_item.detail.setText(text)
        ui_item.detail.setStyleSheet("padding:5px")
        ui_item.thumb.setStyleSheet("margin:5px")

        icon_path = os.path.join(util.get_root_path(), '_desktop', 'storage', 'engines', '{}.png'.format(data.get('id')))
        pixmap = QtGui.QPixmap(icon_path)
        ui_item.thumb.setPixmap(pixmap)

        self.ui.engines.setItemWidget(root_menu, 0, main_item)
        ui_item.eng_open.clicked.connect(lambda evt: self.open_engine(data))

    def open_engine(self, data):
        try:
            r = 0
            PYTHONPATH = []
            for prp in os.environ['PYTHONPATH'].split(";"):
                if "_blender" not in prp:
                    PYTHONPATH.append(prp)
                r += 1

            os.environ['PYTHONPATH'] = ";".join(PYTHONPATH)

            x = 0
            for pr in sys.path:
                if "_blender" in pr:
                    del sys.path[x]
                x += 1

            if data.get("type") == "_maya":

                root_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
                icon_path = os.path.join(root_path, 'storage', 'projects', data.get("name"))
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(root_path, 'storage', 'projects')
                environment_path = os.path.join(os.environ['APPDATA'], 'MBLAB')

                if not os.path.exists(environment_path):
                    os.makedirs(environment_path)

                module = r"""+ Boss 1.0 {root}\_maya
PYTHONPATH += {root}\_maya
PYTHONPATH += {root}\lib
MAYA_PLUG_IN_PATH += {root}\_maya\plug-in
MAYA_SHELF_PATH += {root}\_maya\shelves
""".format(root=os.path.dirname(root_path))

                modules_path = os.path.join(environment_path, 'modules', 'boss.mod')
                if not os.path.exists(os.path.dirname(modules_path)):
                    os.makedirs(os.path.dirname(modules_path))

                with open(modules_path, 'w') as f:
                    f.write(module)

                os.environ['MAYA_APP_DIR'] = environment_path
                os.environ['MBL_PROJECT_ROOT'] = self.project.get("path")

                version_path = os.path.join(environment_path, str(data.get("version")), 'prefs', 'icons')
                if not os.path.exists(version_path):
                    os.makedirs(version_path)

                splash_ori = os.path.join(icon_path, 'splash.png')
                splash_ori = splash_ori.replace("\\", "/")
                splash_dst = os.path.join(version_path, 'MayaStartupImage.png')
                splash_dst = splash_dst.replace("\\", "/")
                shutil.copy2(splash_ori, splash_dst)

            else:
                root_lib = os.path.normpath(os.path.join(util.get_root_path(), 'library'))
                root_engine = os.path.normpath(os.path.join(util.get_root_path(), data.get('type')))
                engine_lib = os.path.normpath(os.path.join(root_engine, 'lib'))
                libs = [util.get_root_path(), root_engine, root_lib, engine_lib]

                if data.get("type") == "_blender":
                    engine_scripts = os.path.normpath(os.path.join(root_engine))
                    os.environ['BLENDER_USER_SCRIPTS'] = engine_scripts

                try:
                    PYTHONPATH = os.environ['PYTHONPATH'].split(";")
                except:
                    PYTHONPATH = []

                for lib_path in libs:
                    if lib_path not in PYTHONPATH:
                        PYTHONPATH.append(lib_path)

                    if lib_path not in sys.path:
                        sys.path.append(lib_path)

                os.environ['PYTHONPATH'] = ";".join(libs)

            os.environ['MB_CONTEXT'] = 'null'
            project = dict(copy.deepcopy(self.project))
            engine_path = project["path{}".format(data.get("type"))]
            project.update({"path": engine_path})
            project.update({"engine": data})
            os.environ['MB_PROJECT'] = json.dumps(project)

            cmd = 'start /B "App" "{}"'.format(data.get("path"))
            os.system(cmd)

        except Exception as error:
            print(error)

    def open_project(self, data):
        try:
            self.project = data
            self.ui.panels.setCurrentIndex(1)
            frame_start, frame_end = data.get("frame_range")
            text = """<html><head/><body><p><span style=" font-size:10pt; font-weight:600;">{project}<br/></span><b>FPS:</b> {fps}, <b>Frames:</b> {frames}<br/>Status: {status}<br/>Render: {render}</p></body></html>""".format(
                fps=self.project.get("fps"),
                render=self.project.get("render").get("name"),
                frames="{}-{}".format(frame_start, frame_end),
                status=self.project.get("current_status"),
                project=self.project.get("name"))

            self.ui.detail.setText(text)
            self.ui.project_name.setText("""<html><head/><body><p><span style=" font-size:11pt;">{project}</span></p></body></html>""".format(project=data.get("name")))
            proj_thumb = os.path.join(util.get_root_path(), "_desktop", "storage", "projects", data.get("name"), "thumb.png")
            if not os.path.exists(proj_thumb):
                proj_thumb = os.path.join(util.get_root_path(), "_desktop", "storage", "projects", "thumb.png")
            pixmap = QtGui.QPixmap(proj_thumb)
            self.ui.thumb.setPixmap(pixmap)

        except Exception as error:
            print(error)


from _desktop.utils import resources
