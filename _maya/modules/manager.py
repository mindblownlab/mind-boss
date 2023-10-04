import os
import sys
import json
import time

from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds, mel
from glob import glob
from importlib import reload
from _maya.utils import util
from _maya.modules import asset, shot

reload(util)
reload(asset)
reload(shot)


class MBManager:
    publish = {}
    assets = []
    ui = None
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def loader(self):
        try:
            self.parent.close()
            self.ui = self.load_ui()
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setFixedSize(800, 600)
            self.ui.publish.clear()
            self.navigator()
            self.ui.up_scene.clicked.connect(self.up_scene)
            # self.ui.publish.itemClicked.connect(self.load_selected)
            self.ui.engine.currentIndexChanged.connect(self.set_engine)
            self.ui.progress.setFormat("")
            for engine in self.parent._engines:
                if os.path.exists(engine.get("path")):
                    self.ui.engine.addItem(engine.get("name"))

            self.parent.show()
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def set_engine(self):
        engine = self.parent._engines[self.ui.engine.currentIndex()]
        self.ui.publish.clear()
        self.get_files(target=self.parent._project.get("path{}".format(engine.get("type"))))

    def load_ui(self):
        return util.load_ui(name='manager', target=self.parent)

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">MANAGER </span></p></body></html>')
            if self.parent._context is not None:
                self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">Notan | {type}</span><span style=" font-size:9pt;"><br/>{step} Asset {name}</span></p></body></html>'.format(type=self.parent._context.get("type").capitalize(), step=self.parent._context.get("step"), name=self.parent._context[self.parent._context.get('type')]))
            else:
                if self.parent._project:
                    self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">Notan | Project</span><span style=" font-size:9pt;"><br/>{project_name}</span></p></body></html>'.format(project_name=self.parent._project.get("name").upper()))
                else:
                    self.parent.ui.project_label.setText('')
        except:
            pass

    def open_files(self):

        for file in self.publish.values():
            try:
                item_asset = QtWidgets.QTreeWidgetItem(self.ui.publish)

                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/icons/{}.png".format(file.get("icon"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
                item_asset.setIcon(0, icon)

                item_asset.setText(0, "{} | {}".format(file.get("type"), file.get("name")))
                item_asset.setExpanded(True)
                item_asset.setData(0, QtCore.Qt.UserRole, file)

                for item in file.get("items"):
                    item_object = QtWidgets.QTreeWidgetItem(item_asset)
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/icons/{}.png".format(item.get("icon"))), QtGui.QIcon.Normal, QtGui.QIcon.On)
                    item_object.setIcon(0, icon)
                    if item.get("lookdev"):
                        item_object.setText(0, " {type} | Lookdev | {name}\n Update: {date} | Size: {bytes}".format(name=item.get("name"), type=item.get("type"), date=item.get("date").get("last_modified"), bytes=item.get("size").get("bytes")))
                    else:
                        item_object.setText(0, " {type} | {name}\n Update: {date} | Size: {bytes}".format(name=item.get("name"), type=item.get("type"), date=item.get("date").get("last_modified"), bytes=item.get("size").get("bytes")))
                    item_object.setData(0, QtCore.Qt.UserRole, item)

            except Exception as error:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def get_files(self, target=None):
        try:
            self.publish = {}
            data = {
                "sequence": self.parent._context.get("sequence"),
                "shot": self.parent._context.get("shot"),
                "name": "*",
            }

            root_path = self.parent._project.get("path")
            if target:
                root_path = target

            lookdev_root = os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_asset_publish"))
            lookdev_root = os.path.normpath(lookdev_root)
            lookdev_root = lookdev_root.format(**data)

            alembics = os.path.join(root_path, self.parent._templates.get("shot_publish_cache"))
            alembics = os.path.normpath(alembics)
            alembics = alembics.format(**data)

            alembics_files = glob(alembics)
            lookdevs_files = glob(os.path.join(lookdev_root, "*", "*", "*", "*", "*.{}".format(self.parent._project.get("engine").get("ext"))))
            lookdevs_files = list(filter(lambda src: "LookDev" in src, lookdevs_files))

            list_assets = []
            for abc in alembics_files:
                asset_name = os.path.basename(abc).split("_")[0]
                if asset_name == "Cam":
                    list_assets.append(os.path.basename(abc).split(".")[0])
                else:
                    list_assets.append(asset_name)
            list_assets = list(dict.fromkeys(list_assets))

            for asset in list_assets:
                type = "Asset"
                icon = "cube"
                if "Cam" in asset:
                    type = "Camera"
                    icon = "camera"

                self.publish[asset] = {
                    "name": asset,
                    "type": type,
                    "icon": icon,
                    "items": []
                }
            lookdevs = []
            for lookdev in lookdevs_files:
                lookdev_data = {
                    "name": os.path.basename(lookdev).split("_")[0],
                    "node_name": os.path.basename(lookdev),
                    "path": lookdev,
                    "icon": "ico{}".format(self.parent._project.get("engine").get("type")),
                    "type": "Lookdev",
                    "size": dict(util.get_size_file(lookdev)),
                    "date": dict(util.get_data_file(lookdev))
                }
                lookdevs.append(lookdev_data)

            alembics = []
            for alembic in alembics_files:
                alembic_name = os.path.basename(alembic).split("_")[0]
                type = "Alembic"
                if "Cam" in alembic:
                    type = "Camera"

                lookdev = list(filter(lambda lkd: lkd.get("name") == alembic_name, lookdevs))
                if lookdev:
                    lookdev = dict(lookdev[0])
                else:
                    lookdev = None

                alembic_data = {
                    "name": alembic_name,
                    "node_name": os.path.basename(alembic),
                    "path": alembic,
                    "lookdev": lookdev,
                    "icon": "alembic",
                    "type": type,
                    "size": dict(util.get_size_file(alembic)),
                    "date": dict(util.get_data_file(alembic)),
                }
                alembics.append(alembic_data)

            for pub in self.publish.keys():
                if "Cam" in pub:
                    self.publish[pub]["items"] = list(filter(lambda abc: abc.get("name") == "Cam", alembics))
                else:
                    self.publish[pub]["items"] = list(filter(lambda abc: abc.get("name") == pub, alembics))

            self.open_files()

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def up_scene(self):
        total = self.ui.publish.topLevelItemCount()
        collector = []
        for i in range(total):
            item = self.ui.publish.topLevelItem(i)
            if item.childCount() > 0:
                for s in range(item.childCount()):
                    sub_item = item.child(s)
                    sub_data = dict(sub_item.data(0, QtCore.Qt.UserRole))
                    collector.append(sub_data)

        if len(collector) > 0:
            preloader = 0
            index = 0
            total = len(collector)
            while index < len(collector):
                try:
                    exp = collector[index]
                    QtCore.QCoreApplication.processEvents()
                    self.mount_scene(data=exp)
                    pct = (((preloader + 1) * 100) / total)
                    preloader += 1
                    self.ui.progress.setProperty("value", pct)
                except:
                    preloader += 1
                index += 1
        self.ui.progress.setProperty("value", 0)
        self.parent.close()
        cmds.select(clear=True)

    def mount_scene(self, data):
        try:
            if data.get("type") == "Camera":
                camera_name = data.get("node_name").split(".")[0]
                if not cmds.objExists("{}RN".format(camera_name)):
                    cmds.file(data.get("path"), reference=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace=camera_name, groupReference=False)
                    cmds.referenceQuery(data.get("path"), referenceNode=True)
                model_editor = cmds.getPanel(withFocus=True)
                if model_editor != 'modelPanel4':
                    model_editor = 'modelPanel4'
                node_camera = "{0}:{0}".format(camera_name)
                cmds.camera(node_camera, edit=True, lockTransform=True)
                cmds.modelEditor(model_editor, e=True, camera=node_camera)

                if not cmds.objExists("CAM"):
                    cmds.group(name="CAM", empty=True)

                if cmds.objExists("CAM"):
                    cmds.parent(node_camera, "CAM")
            else:
                QtCore.QCoreApplication.processEvents()
                alembic_name = data.get('node_name').replace("_master_grp", "").replace(".abc", "")
                if data.get("lookdev"):
                    cmds.file(data.get("lookdev").get("path"), reference=True, loadReferenceDepth="all", mergeNamespacesOnClash=False, namespace=alembic_name, groupReference=False)
                    node_asset = "{0}:{1}_master_grp".format(alembic_name, data.get("name"))
                    cmds.AbcImport(data.get("path"), mode='import', connect=node_asset)
                    if not cmds.objExists("CHAR"):
                        cmds.group(name="CHAR", empty=True)

                    if cmds.objExists("CHAR"):
                        cmds.parent(node_asset, "CHAR")
                else:
                    cmds.AbcImport(data.get("path"), mode='import')
                    if not cmds.objExists("ABC"):
                        cmds.group(name="ABC", empty=True)

                    if cmds.objExists("ABC"):
                        cmds.parent(alembic_name, "ABC")

                cmds.select(clear=True)

                project_data = self.parent.mb_project.get_data()
                width, height = project_data.get('resolution')
                frame_start, frame_end = self.parent.mb_scene.get_context_data().get("frame_range")

                cmds.currentUnit(time='film')
                cmds.setAttr("defaultResolution.width", int(width))
                cmds.setAttr("defaultResolution.height", int(height))

                cmds.playbackOptions(minTime=int(frame_start), maxTime=int(frame_end), animationStartTime=int(frame_start), animationEndTime=int(frame_end))
                cmds.setAttr("defaultRenderGlobals.startFrame", int(frame_start))
                cmds.setAttr("defaultRenderGlobals.endFrame", int(frame_end))
                cmds.setAttr("defaultResolution.dar", int(project_data.get("aspect")))

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))


from _maya.utils import resources
