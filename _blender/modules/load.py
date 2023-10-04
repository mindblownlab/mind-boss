import os
import sys
from PySide2 import QtWidgets, QtCore, QtGui
from glob import glob
from importlib import reload
from _blender.utils import util
from _blender.modules import asset, shot

reload(util)
reload(asset)
reload(shot)


class MBLoad:
    assets = []
    shots = []
    publish = []
    ui = None
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def loading(self):
        try:
            self.parent.close()
            self.ui = self.load_ui()
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setFixedSize(800, 600)

            if self.parent._context:
                if self.parent._context.get("type") == "asset":
                    self.ui.work_tab.setCurrentIndex(0)
                else:
                    self.ui.work_tab.setCurrentIndex(1)

            self.ui.assets.itemClicked.connect(self.open_files)
            self.ui.shots.itemClicked.connect(self.open_files)
            self.ui.load_type.currentIndexChanged.connect(self.check_type)
            self.ui.button_reference.clicked.connect(self.reference_file)
            self.ui.button_import.clicked.connect(self.import_file)
            self.ui.load_type.setEnabled(False)
            self.navigator()
            self.populate()
            self.parent.show()

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def load_ui(self):
        return util.load_ui(name='load', target=self.parent)

    def populate(self):
        self.get_assets()
        self.get_shots()

        self.ui.assets.clear()
        self.ui.shots.clear()
        self.ui.publish.clear()

        for asset_type in self.assets:
            type_menu = QtWidgets.QTreeWidgetItem(self.ui.assets)
            type_menu.setText(0, os.path.basename(asset_type.get("name")))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/icons/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            type_menu.setIcon(0, icon)
            type_menu.setData(0, QtCore.Qt.UserRole, asset_type)
            if len(asset_type.get("assets")) > 0:
                for asset in asset_type.get("assets"):
                    asset_menu = QtWidgets.QTreeWidgetItem(type_menu)
                    asset_menu.setText(0, os.path.basename(asset.get("name")))
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/icons/cube.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                    asset_menu.setIcon(0, icon)
                    asset_menu.setData(0, QtCore.Qt.UserRole, asset)
                    step_asset_data = {
                        "asset_type": asset_type.get("name"),
                        "type": "asset",
                        "asset": asset.get("name"),
                        "load": True,
                        "path": asset.get("path")
                    }
                    asset_menu.setData(0, QtCore.Qt.UserRole, step_asset_data)

        for sequence in self.shots:
            sec_menu = QtWidgets.QTreeWidgetItem(self.ui.shots)
            sec_menu.setText(0, os.path.basename(sequence.get("name")))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/icons/folder.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            sec_menu.setIcon(0, icon)
            sec_menu.setData(0, QtCore.Qt.UserRole, sequence)
            if len(sequence.get("shots")) > 0:
                for shot in sequence.get("shots"):
                    shot_menu = QtWidgets.QTreeWidgetItem(sec_menu)
                    shot_menu.setText(0, os.path.basename(shot.get("name")))
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/icons/movie.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                    shot_menu.setIcon(0, icon)
                    step_shot_data = {
                        "type": "shot",
                        "sequence": sequence.get("name"),
                        "shot": shot.get("name")
                    }
                    shot_menu.setData(0, QtCore.Qt.UserRole, step_shot_data)

    def get_assets(self):
        try:
            self.assets = []
            assets_path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_asset"), "*")
            assets_path = os.path.normpath(assets_path)
            types = glob(assets_path)
            types = list(filter(lambda typ: ".ini" not in typ and "edits" not in typ, types))
            types = list(map(lambda typ: os.path.normpath(typ), types))
            for type_path in types:
                type_name = os.path.basename(type_path)
                type_data = {
                    "name": type_name,
                    "path": type_path,
                    "assets": []
                }
                assets = glob(os.path.join(type_path, "*"))
                assets = list(filter(lambda ass: ".ini" not in ass, assets))
                assets = list(map(lambda ass: os.path.normpath(ass), assets))
                for asset_path in assets:
                    asset_name = os.path.basename(asset_path)
                    asset_data = {
                        "name": asset_name,
                        "path": asset_path
                    }
                    type_data["assets"].append(asset_data)
                self.assets.append(type_data)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("{}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def get_shots(self):
        try:
            self.shots = []
            sequences = glob(os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_shot"), "*"))
            sequences = list(filter(lambda sec: ".ini" not in sec and "edits" not in sec, sequences))
            sequences = list(map(lambda sec: os.path.normpath(sec), sequences))
            for sec_path in sequences:
                sec_name = os.path.basename(sec_path)
                sec_data = {
                    "name": sec_name,
                    "path": sec_path,
                    "shots": []
                }
                shots = glob(os.path.join(sec_path, "*"))
                shots = list(filter(lambda ass: ".ini" not in ass, shots))
                shots = list(map(lambda ass: os.path.normpath(ass), shots))
                for shot_path in shots:
                    asset_name = os.path.basename(shot_path)
                    asset_data = {
                        "name": asset_name,
                        "path": shot_path
                    }
                    sec_data["shots"].append(asset_data)
                self.shots.append(sec_data)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("{}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def open_files(self, it):
        try:
            data = dict(it.data(0, QtCore.Qt.UserRole))
            tab_index = self.ui.work_tab.currentIndex()
            self.parent.ui.project_label.setText("")
            if it.parent():
                self.ui.load_type.setEnabled(True)
                if tab_index == 0:
                    self.parent.ui.project_label.setText('<html><head/><body><p><span style=" font-weight:600;">{type}</span> &gt; {asset_type} &gt; {asset}</p></body></html>'.format(type=data.get("type").capitalize(), asset_type=data.get("asset_type"), asset=data.get("asset")))
                else:
                    self.parent.ui.project_label.setText('<html><head/><body><p><span style=" font-weight:600;">{type}</span> &gt; {sequence} &gt; {shot}</p></body></html>'.format(type=data.get("type").capitalize(), sequence=data.get("sequence"), shot=data.get("shot")))
                self.ui.publish.clear()
                self.publish = []
                proxy = self.ui.load_type.currentText()
                if tab_index == 0:
                    if proxy == "proxy":
                        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("asset_publish_proxy"))
                    elif proxy == "work":
                        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("asset_work"))
                    else:
                        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("asset_publish"))
                else:
                    if proxy == "proxy":
                        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("shot_publish_proxy"))
                    elif proxy == "work":
                        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("shot_work"))
                    else:
                        path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("shot_publish"))
                path = os.path.normpath(path)
                path = os.path.dirname(path)
                data.update({"step": self.parent._context.get("step"), "ext": self.parent._project.get("engine").get("ext")})
                path = path.format(**data)
                if proxy == "proxy":
                    path = os.path.normpath(path)
                else:
                    path = os.path.dirname(os.path.dirname(os.path.normpath(path)))

                self.get_files(path=path)
                extensions = {".ma": "maya", ".abc": "alembic", ".obj": "obj", ".fbx": "fbx"}
                for file in self.publish:
                    item_file = QtWidgets.QTreeWidgetItem(self.ui.publish)
                    item_file.setText(0, " {name}\n Version: {version}\n Update: {date}\n Size: {bytes}".format(name=file.get("name"), version=file.get("version"), date=file.get("date").get("last_modified"), bytes=file.get("size").get("bytes")))
                    icon_file = QtGui.QIcon()
                    if proxy == "proxy":
                        file_name, file_extension = os.path.splitext(file.get("path"))
                        image = QtGui.QPixmap(":/icons/{}.png".format(extensions[file_extension]))
                        self.ui.publish.setIconSize(QtCore.QSize(80, 80))
                    else:
                        thumbnail = file.get("path").replace(".{}".format(format(self.parent._project.get("engine").get("ext"))), ".png")
                        image = QtGui.QPixmap(":/icons/ico{}.png".format(format(self.parent._project.get("engine").get("type"))))
                        if os.path.exists(thumbnail):
                            image = QtGui.QPixmap(thumbnail)
                        self.ui.publish.setIconSize(QtCore.QSize(120, 60))

                    icon_file.addPixmap(image, QtGui.QIcon.Normal, QtGui.QIcon.On)
                    item_file.setIcon(0, icon_file)
                    item_file.setData(0, QtCore.Qt.UserRole, {**data, **file})
            else:
                self.ui.load_type.setEnabled(False)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def get_files(self, path):
        proxy = self.ui.load_type.currentText()
        if proxy == "proxy":
            file_path = os.path.join(path, "*")
        else:
            file_path = os.path.join(path, "*", "*", "*.{}".format(self.parent._project.get("engine").get("ext")))

        files = glob(file_path)

        files = list(filter(lambda sec: ".ini" not in sec and "edits" not in sec, files))
        files = list(map(lambda sec: os.path.normpath(sec), files))
        files = sorted(files, key=lambda file: os.path.getctime(file))
        files.reverse()
        for file_path in files:
            filename = os.path.basename(file_path)
            version = int(filename.split(".")[1].replace("v", ""))
            file_data = {
                "name": filename,
                "version": version,
                "path": file_path,
                "date": util.get_data_file(file_path),
                "size": util.get_size_file(file_path),
            }
            self.publish.append(file_data)

    def check_type(self):
        tab_index = self.ui.work_tab.currentIndex()
        if tab_index == 0:
            item = self.ui.assets.selectedItems()[0]
        else:
            item = self.ui.shots.selectedItems()[0]
        self.open_files(item)

    def reference_file(self):
        if len(self.ui.publish.selectedItems()) > 0:
            for file in self.ui.publish.selectedItems():
                data = dict(file.data(0, QtCore.Qt.UserRole))
                path = data.get("path").replace("\\", "/")
                tab_index = self.ui.work_tab.currentIndex()
                proxy = self.ui.load_type.currentText()
                if proxy == "proxy":
                    path = path.replace("/cache", "//cache")
                else:
                    if tab_index == 0:
                        path = path.replace("/assets", "//assets")
                    else:
                        path = path.replace("/scenes", "//scenes")

                for i in range(self.ui.limit.value()):
                    print(data.get('name'))
                    # cmds.file(path, reference=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace=data.get('name'), groupReference=True)

    def import_file(self):
        if len(self.ui.publish.selectedItems()) > 0:
            for file in self.ui.publish.selectedItems():
                data = dict(file.data(0, QtCore.Qt.UserRole))
                # cmds.file(data.get("path").replace("\\", "/"), i=True, renameAll=True, gr=True, namespace=data.get(data.get('type')), preserveReferences=False)
                # ref_node = cmds.ls(selection=True)
                # if ref_node:
                #     cmds.rename(ref_node, '{}RN_{:03d}'.format(data.get(data.get('type')), data.get('version')))

    def navigator(self):
        tab_index = self.ui.work_tab.currentIndex()
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">LOAD </span><span style=" font-size:10pt;">{navigate}</span></p></body></html>'.format(navigate=self.ui.work_tab.tabText(tab_index)))
            self.ui.new_context.setText("+ New {navigate}".format(navigate=self.ui.work_tab.tabText(tab_index)[:-1]))
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
