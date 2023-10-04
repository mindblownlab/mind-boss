from PySide2 import QtWidgets, QtCore, QtGui
from importlib import reload
from _maya.utils import util
from _maya.modules import asset, shot

reload(util)
reload(asset)
reload(shot)


class MBInfo:
    ui = None
    parent = None
    data_asset = None
    data_shot = None

    def __init__(self, parent):
        self.parent = parent
        self.data_asset = asset.MBAsset(parent)
        self.data_shot = shot.MBShot(parent)

    def detail(self):
        self.parent.close()
        self.ui = self.load_ui()
        self.parent.ui.main_layout.addWidget(self.ui)

        # form_info = self.ui.findChild(QtWidgets.QWidget, "form_info")
        # self.parent.manager_layout.addWidget(form_info)
        # self.parent.manager_layout.addWidget(self.parent.footer_widget)

        self.ui.status.addItems(self.parent._project.get("status"))
        self.ui.animator.setText(self.data_shot.get_data().get("animator"))
        frame_start, frame_end = self.data_shot.get_data().get("frame_range")
        self.ui.frame_start.setValue(frame_start)
        self.ui.frame_end.setValue(frame_end)

        nodes = self.data_shot.get_data().get("exports") + self.data_shot.get_data().get("cameras")

        for node in nodes:
            type_menu = QtWidgets.QTreeWidgetItem(self.ui.assets)
            type_menu.setText(0, "{} ".format(node))
            icon = QtGui.QIcon()
            if "cam_" in node.lower():
                icon.addPixmap(QtGui.QPixmap(":/icons/camera.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            else:
                icon.addPixmap(QtGui.QPixmap(":/icons/cube.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
            type_menu.setIcon(0, icon)

        self.ui.button_cancel.clicked.connect(self.parent.close)
        self.navigator()
        self.parent.show()

    def load_ui(self):
        return util.load_ui(name='info', target=self.parent)

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">MANAGER {} </span></p></body></html>'.format(self.parent._context.get("type").upper()))
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
