import os
import sys
import bpy
from PySide2 import QtWidgets, QtCore, QtGui
from glob import glob
import json
from importlib import reload
from uuid import uuid4
from _blender.utils import util
from _blender.modules import asset, shot

reload(util)


class MBOpen:
    assets = []
    shots = []
    working = []
    publish = []
    data_asset = None
    data_shot = None
    ui = None
    parent = None
    data = None

    def __init__(self, parent):
        self.parent = parent
        self.data_asset = asset.MBAsset(parent)
        self.data_shot = shot.MBShot(parent)

    def opening(self):
        self.parent.close()
        self.ui = self.load_ui()
        self.parent.ui.main_layout.addWidget(self.ui)
        self.parent.setFixedSize(800, 600)

        self.ui.work_tab.currentChanged.connect(self.navigator)
        self.ui.files_tab.currentChanged.connect(self.reload_files)
        self.ui.assets.itemClicked.connect(self.open_files)
        self.ui.shots.itemClicked.connect(self.open_files)
        self.ui.work_files.itemClicked.connect(self.open_scene)
        self.ui.publish_files.itemClicked.connect(self.open_scene)
        self.ui.new_file.clicked.connect(self.new_file)
        self.ui.new_context.clicked.connect(self.new_context)
        self.ui.reload.clicked.connect(self.populate)
        self.ui.new_file.setDisabled(True)
        self.ui.new_context.setDisabled(True)

        if self.parent._context:
            if self.parent._context.get("type") == "asset":
                self.ui.work_tab.setCurrentIndex(0)
            else:
                self.ui.work_tab.setCurrentIndex(1)

        self.reset()
        self.populate()
        self.navigator()

        if self.parent._project:
            if self.parent._project:
                self.ui.setDisabled(False)
            else:
                self.ui.setDisabled(True)

        self.parent.show()

    def load_ui(self):
        return util.load_ui(name='open', target=self.parent)

    def navigator(self):
        tab_index = self.ui.work_tab.currentIndex()
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">OPEN </span><span style=" font-size:10pt;">{navigate}</span></p></body></html>'.format(navigate=self.ui.work_tab.tabText(tab_index)))
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

    def reset(self):
        self.assets = []
        self.shots = []
        self.working = []
        self.publish = []
        self.ui.work_files.clear()
        self.ui.publish_files.clear()
        self.ui.assets.clear()
        self.ui.shots.clear()

    def populate(self):
        self.get_assets()
        self.get_shots()

        self.ui.assets.clear()
        self.ui.shots.clear()

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
                    for asset_step in self.parent._project.get("steps").get("assets"):
                        step_shot_menu = QtWidgets.QTreeWidgetItem(asset_menu)
                        step_shot_menu.setText(0, asset_step)
                        icon_shot_step = QtGui.QIcon()
                        icon_shot_step.addPixmap(QtGui.QPixmap(":/icons/step.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                        step_shot_menu.setIcon(0, icon_shot_step)
                        step_asset_data = list(filter(lambda ast: ast.get("asset") == asset.get("name"), self.parent._assets))
                        if step_asset_data:
                            step_asset_data = dict(step_asset_data[0])
                            step_asset_data.update({"path": os.path.normpath(os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_asset"), step_asset_data.get("asset_type"), step_asset_data.get("asset"), asset_step))})
                        else:
                            step_asset_data = {
                                "step": asset_step,
                                "asset_type": asset_type.get("name"),
                                "type": "asset",
                                "asset": asset.get("name"),
                                "uuid": uuid4(),
                                "path": os.path.normpath(os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_asset"), asset_type.get("name"), asset.get("name"), asset_step))
                            }

                        step_shot_menu.setData(0, QtCore.Qt.UserRole, step_asset_data)

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
                    shot_menu.setData(0, QtCore.Qt.UserRole, shot)
                    for shot_step in self.parent._project.get("steps").get("shots"):
                        step_shot_menu = QtWidgets.QTreeWidgetItem(shot_menu)
                        step_shot_menu.setText(0, shot_step)
                        icon_shot_step = QtGui.QIcon()
                        icon_shot_step.addPixmap(QtGui.QPixmap(":/icons/step.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
                        step_shot_menu.setIcon(0, icon_shot_step)
                        step_shot_data = {
                            "step": shot_step,
                            "type": "shot",
                            "sequence": sequence.get("name"),
                            "shot": shot.get("name"),
                            "path": os.path.normpath(os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_shot"), sequence.get("name"), shot.get("name"), shot_step)),
                            "open": True
                        }
                        step_shot_menu.setData(0, QtCore.Qt.UserRole, step_shot_data)

    def reload_files(self):
        tab_index = self.ui.work_tab.currentIndex()
        if tab_index == 0:
            item = self.ui.assets.currentItem()
        else:
            item = self.ui.shots.currentItem()
        self.open_files(item)

    def open_files(self, it):
        data = dict(it.data(0, QtCore.Qt.UserRole))

        if it.parent() is None:
            self.ui.new_file.setEnabled(False)
            self.ui.new_context.setEnabled(True)
        else:
            self.ui.new_file.setEnabled(True)
            self.ui.new_context.setEnabled(False)

        self.ui.work_files.clear()
        self.ui.publish_files.clear()
        self.working = []
        self.publish = []

        type_file = self.ui.files_tab.currentIndex()

        if type_file == 0:
            path = data.get("path")
            target = self.ui.work_files
        else:
            path = data.get("path").replace("work", "")
            target = self.ui.publish_files

        path = os.path.join(path, self.parent._project.get("engine").get("ext"))

        files = self.get_files(path)
        for file in files:
            item_file = QtWidgets.QTreeWidgetItem(target)
            item_file.setText(0, " {name}\n Version: {version}\n Update: {date}\n Size: {bytes}".format(name=file.get("name"), version=file.get("version"), date=file.get("date").get("last_modified"), bytes=file.get("size").get("bytes")))
            icon_file = QtGui.QIcon()
            thumbnail = file.get("path").replace(".{}".format(self.parent._project.get("engine").get("ext")), ".png")
            if not os.path.exists(thumbnail):
                image = QtGui.QPixmap(":/icons/ico{}.png".format(self.parent._project.get("engine").get("type")))
                target.setIconSize(QtCore.QSize(60, 60))
            else:
                image = QtGui.QPixmap(thumbnail)
                target.setIconSize(QtCore.QSize(120, 60))

            icon_file.addPixmap(image, QtGui.QIcon.Normal, QtGui.QIcon.On)
            item_file.setIcon(0, icon_file)
            item_file.setData(0, QtCore.Qt.UserRole, {**data, **file})

    def get_files(self, path):
        files = glob(os.path.join(path, "*.{}".format(self.parent._project.get("engine").get("ext"))))
        files = list(filter(lambda sec: ".ini" not in sec and "edits" not in sec, files))
        files = list(map(lambda sec: os.path.normpath(sec), files))
        files = sorted(files, key=lambda file: os.path.getctime(file))
        files.reverse()
        list_all = []
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
            list_all.append(file_data)
        return list_all

    def get_assets(self):
        try:
            if self.parent._project:
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
            if self.parent._project:
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

    def check_save(self):
        return True

    def open_scene(self, it):
        try:
            if self.check_save():
                tab_index = self.ui.work_tab.currentIndex()
                if tab_index == 0:
                    item = self.ui.assets.currentItem()
                else:
                    item = self.ui.shots.currentItem()
                data = dict(it.data(0, QtCore.Qt.UserRole))
                data.update({"step": item.text(0)})
                os.environ['MB_CONTEXT'] = json.dumps(data)
                bpy.ops.wm.open_mainfile(filepath=data.get("path"))
                self.parent.refresh()
                self.parent.close()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.script.reload()

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def new_context(self):
        tab_index = self.ui.work_tab.currentIndex()
        if tab_index == 0:
            item = self.ui.assets.selectedItems()[0]
            data_list = self.assets
            template_name = "root_asset"
        else:
            item = self.ui.shots.selectedItems()[0]
            data_list = self.shots
            template_name = "root_shot"
        step = self.ui.work_tab.tabText(tab_index).lower()
        context_name = ""
        print(json.dumps(step, indent=2))
        print(json.dumps(data_list, indent=2))
        print(json.dumps(context_name, indent=2))

        # result = cmds.promptDialog(title='Context name', message='Enter Name:', button=['OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
        # if result == 'OK':
        #     context_name = cmds.promptDialog(query=True, text=True)
        #
        # if tab_index == 0:
        #     type = item.text(0)
        #     for ctx in self.parent._project.get("steps")[step]:
        #         ctx_path = os.path.normpath(os.path.join(self.parent._project.get("path"), self.parent._templates[template_name], type, context_name, ctx))
        #         if not os.path.exists(ctx_path):
        #             os.makedirs(ctx_path)
        # else:
        #     sequence = item.text(0)
        #     for ctx in self.parent._project.get("steps")[step]:
        #         ctx_path = os.path.normpath(os.path.join(self.parent._project.get("path"), self.parent._templates[template_name], sequence, context_name, ctx))
        #         if not os.path.exists(ctx_path):
        #             os.makedirs(ctx_path)

        self.populate()

    def new_file(self):
        if self.check_save():
            tab_index = self.ui.work_tab.currentIndex()
            if tab_index == 0:
                item = self.ui.assets.currentItem()
            else:
                item = self.ui.shots.currentItem()

            data = dict(item.data(0, QtCore.Qt.UserRole))
            data.update({"step": item.text(0)})
            os.environ['MB_CONTEXT'] = json.dumps(data)

            bpy.ops.wm.read_homefile(app_template="")

            self.reset()
            self.parent.close()
            self.parent.refresh()

            assetName = "{}_master_grp".format(self.parent._context.get("asset"))
            for collect in bpy.data.collections:
                if collect.name == "Collection":
                    bpy.data.collections.remove(collect)

            if self.parent._context.get("type") == "asset" and self.parent._context.get("step") in ["Model", "LookDev"]:
                if assetName not in list(filter(lambda asset: asset.name, bpy.data.collections)):
                    bpy.ops.collection.create(name=assetName)
                    bpy.context.scene.collection.children.link(bpy.data.collections[assetName])
                bpy.data.collections[assetName]["Export"] = True
                bpy.data.collections[assetName]["AssetId"] = data.get("uuid")

            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.script.reload()

    def callback(self, call):
        call()


from _blender.utils import resources
