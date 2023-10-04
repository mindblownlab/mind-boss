import json
import os
import sys
from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds, mel
from glob import glob
from importlib import reload
import datetime
from library import ffmpeg
from _maya.utils import util
from _maya.modules import asset, shot

reload(util)
reload(asset)
reload(shot)


class MBBLast:
    ui = None
    parent = None
    data_shot = None

    def __init__(self, parent):
        self.parent = parent
        self.data_shot = {}


    # close window
    def closeEvent(self):
        self.prepare_viewport(active=False)

    def open(self):
        try:
            self.data_shot = list(filter(lambda item: item.get("shot") == self.parent._context.get("shot"), self.parent._shots))

            if self.data_shot:
                self.data_shot = self.data_shot[0]

            self.parent.close()
            self.ui = self.load_ui()
            self.parent.ui.main_layout.addWidget(self.ui)
            self.parent.setFixedSize(500, 230)

            # main_blast = sel  f.ui.findChild(QtWidgets.QWidget, "main_blast")
            # self.parent.manager_layout.addWidget(main_blast)
            # self.parent.manager_layout.addWidget(self.parent.footer_widget)

            self.parent.show()
            self.navigator()
            self.populate()

            if self.data_shot.get("animator"):
                self.ui.animator.setEnabled(False)
                self.ui.animator.setText(self.data_shot.get("animator").upper())

            QtCore.QCoreApplication.processEvents()
            self.ui.cameras.currentIndexChanged.connect(self.set_camera)
            self.ui.play_pause.clicked.connect(self.play_pause)
            self.ui.export_blast.clicked.connect(self.create_blast)
            QtCore.QTimer.singleShot(250, self.get_all_cameras)

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def load_ui(self):
        return util.load_ui(name='blast', target=self.parent)

    def populate(self):
        try:
            sequences = glob(os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_shot"), "*"))
            sequences = list(map(lambda sec: os.path.basename(sec), sequences))

            shots = glob(os.path.join(self.parent._project.get("path"), self.parent._templates.get("root_shot"), "*", "*"))
            shots = list(map(lambda sec: os.path.basename(sec), shots))

            self.ui.sequence.clear()
            self.ui.shot.clear()
            self.ui.step.clear()
            self.ui.resolution.clear()
            self.ui.format.clear()

            self.ui.sequence.addItems(sequences)
            self.ui.shot.addItems(shots)
            self.ui.step.addItems(self.parent._project.get("playblast").get("steps"))
            resolution = list(self.parent._project.get("playblast").get("resolution").keys())
            resolution = list(map(lambda rs: rs.replace("_", " "), resolution))
            self.ui.resolution.addItems(resolution)
            self.ui.format.addItems(self.parent._project.get("playblast").get("format"))

            self.ui.shot.setCurrentText(self.parent._context.get("shot"))

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("{}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def navigator(self):
        try:
            self.parent.ui.navigate.setText('<html><head/><body><p><span style=" font-size:11pt; font-weight:600;">PLAYBLAST </span></p></body></html>')
            self.parent.ui.project_label.setText('<html><head/><body><p align="right"><span style=" font-size:9pt; font-weight:600;">Notan | {type}</span><span style=" font-size:9pt;"><br/>{step} Asset {name}</span></p></body></html>'.format(type=self.parent._context.get("type").capitalize(), step=self.parent._context.get("step"), name=self.parent._context[self.parent._context.get('type')]))
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    # get all cameras
    def get_all_cameras(self):
        try:
            self.ui.cameras.clear()
            self.all_cameras = cmds.listCameras(p=True)
            self.all_cameras.sort()
            self.all_cameras = list(map(lambda cam: {"name": cam.upper(), "cam": cam}, self.all_cameras))
            for cam in self.all_cameras:
                self.ui.cameras.addItem(cam.get("name"))
        except:
            pass

    # set camera select
    def set_camera(self):
        try:
            current_camera_index = self.ui.cameras.currentIndex()
            current_camera = self.all_cameras[current_camera_index].get("cam")
            self.viewport = cmds.getPanel(withFocus=True)
            if self.viewport != "modelPanel4":
                self.viewport = "modelPanel4"
            cmds.modelEditor(self.viewport, e=True, camera=current_camera)
            self.prepare_viewport()
            cmds.modelEditor(self.viewport, edit=True,
                             displayAppearance='smoothShaded',
                             grid=False,
                             activeView=True,
                             displayLights='default',
                             cameras=False,
                             nurbsCurves=False,
                             headsUpDisplay=False,
                             displayTextures=True,
                             lights=False,
                             shadows=True)

            cmds.select(clear=True)
        except:
            pass

    # prepare viewport for playblast
    def prepare_viewport(self, active=True):
        camera_index = self.ui.cameras.currentIndex()
        camera = self.all_cameras[camera_index]
        if active:
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", True)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(self.viewport, e=True,
                             allObjects=False,
                             polymeshes=True,
                             shadows=False,
                             displayTextures=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             headsUpDisplay=False,
                             pluginObjects=("gpuCacheDisplayFilter", True)
                             )
            mel.eval('generateAllUvTilePreviews;')
            cmds.grid(toogle=False)
            # cmds.camera(camera.get("cam"), e=True, displayResolution=False)
            # cmds.camera(camera.get("cam"), e=True, displayGateMask=True)

        else:
            cmds.grid(toogle=True)
            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", False)
            cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable ", False)
            cmds.modelEditor(self.viewport, e=True,
                             allObjects=True,
                             shadows=False,
                             displayTextures=True,
                             headsUpDisplay=True,
                             displayAppearance='smoothShaded',
                             displayLights='default',
                             pluginObjects=("gpuCacheDisplayFilter", False)
                             )
            # cmds.camera(camera.get("cam"), e=True, displayResolution=True)
            # cmds.camera(camera.get("cam"), e=True, displayGateMask=True)

    # get sound timeline
    def get_sound(self):
        try:
            PlayBackSlider = mel.eval('$tmpVar=$gPlayBackSlider')
            audio = cmds.timeControl(PlayBackSlider, q=True, sound=True, displaySound=True)
            if audio:
                return audio
            else:
                cmds.warning('No sound node.')
                return ""
        except:
            return ""

    def create_blast(self):
        try:
            if self.ui.animator.text() == "":
                cmds.confirmDialog(title="Animator", message="Enter the name of the animator!", button=['Ok'], defaultButton="Ok")
                return

            QtCore.QCoreApplication.processEvents()
            self.ui.progress_bar.setVisible(True)
            cmds.optionVar(stringValue=())

            self.data = {
                "animator": self.ui.animator.text(),
                "format": self.ui.format.currentText(),
                "step": self.ui.step.currentText(),
                "sequence": self.ui.sequence.currentText(),
                "shot": self.ui.shot.currentText(),
                "date": datetime.date.today().strftime("%d/%m/%Y")
            }

            # Get the file path from Maya
            file_path = cmds.file(q=True, sn=True)

            if file_path is None:
                cmds.confirmDialog(title="Scene", message="I do not save", button=['Ok'], defaultButton="Ok")
                return

            data_blast = {
                "sequence": self.ui.sequence.currentText(),
                "shot": self.ui.shot.currentText(),
                "name": self.ui.shot.currentText(),
                "version": "{:03d}".format(1),
            }
            # Get the file name
            path = os.path.join(util.get_root_project(), self.parent._templates.get("playblast_review").format(**data_blast))
            path = os.path.normpath(path)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            frame_start, frame_end = (cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True))
            QtCore.QCoreApplication.processEvents()

            resolution = self.ui.resolution.currentText().replace(" ", "_")
            width, height = list(self.parent._project.get("playblast").get("resolution")[resolution])
            self.filename = path.replace("\\", "/")
            QtCore.QCoreApplication.processEvents()
            self.ui.progress_bar.setFormat("Create playblast")
            self.ui.progress_bar.setProperty("value", 33)
            cmds.select(clear=True)
            cmds.playblast(
                format='avi',
                percent=100,
                quality=100,
                viewer=False,
                sequenceTime=False,
                combineSound=True,
                sound=self.get_sound(),
                clearCache=True,
                startTime=int(frame_start),
                endTime=int(frame_end),
                offScreen=True,
                showOrnaments=True,
                forceOverwrite=True,
                filename=self.filename,
                widthHeight=[width, height],
                rawFrameNumbers=False,
                framePadding=4)

            cmds.optionVar(stringValue=("animator", self.ui.animator.text()))
            QtCore.QTimer.singleShot(300, self.create_layout)

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def create_layout(self):
        try:
            logo_path = os.path.join(util.get_root_path(), "resources", "logo.png")
            font_path = os.path.join(util.get_root_path(), "resources", "font.ttf")
            QtCore.QCoreApplication.processEvents()

            height_bar = 120
            space = (height_bar / 2)
            font_size = 18
            font_color = '#FFFFFF'
            border_color = '#3c3c3c00'
            border_width = 1
            line_spacing = -2

            base = ffmpeg.input(self.filename)
            if self.get_sound():
                audio = base.audio
            else:
                audio = None

            base = ffmpeg.filter([base, ffmpeg.input(logo_path)], 'overlay', 'W-overlay_w-{}'.format(space), (space / 2), )
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text=self.data.get("date"), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='ANIMATOR: {}'.format(self.data.get('animator')), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text="{}".format(self.data.get('step')), fontcolor=font_color, escape_text=True, x=space, y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='COUNT\: %{n}', start_number=1, fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2-th-8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='FRAMES\: {0}-{1}'.format(int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))), fontcolor=font_color, escape_text=False, x='{} * 5 + 100'.format(space), y='{}-th/2'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)
            base = ffmpeg.drawtext(base, fontsize=font_size, fontfile=font_path, text='{} {}'.format(self.data.get('sequence'), self.data.get('shot')), fontcolor=font_color, escape_text=True, x='{} * 5 + 100'.format(space), y='{}-th/2+th+8'.format(space), borderw=border_width, bordercolor=border_color, line_spacing=line_spacing)

            try:
                self.ui.progress_bar.setFormat("Convert and create layout")
                self.ui.progress_bar.setProperty("value", 66)

                if self.get_sound():
                    joined = ffmpeg.concat(base, audio, v=1, a=1).node
                    # , loglevel="quiet"
                    cmd_blast = ffmpeg.output(joined[0], joined[1], self.filename.replace(".avi", ".{}".format(self.data.get("format").lower())))
                else:
                    # , loglevel="quiet"
                    cmd_blast = ffmpeg.output(base, self.filename.replace(".avi", ".{}".format(self.data.get("format").lower())))

                try:
                    cmd_blast.global_args('-y').run(cmd=util.get_ffmpeg())
                    cmds.launch(mov=self.filename.replace(".avi", ".{}".format(self.data.get("format").lower())))
                except Exception as error:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("A: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

            except Exception as error:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("B: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

            QtCore.QCoreApplication.processEvents()
            self.ui.progress_bar.setVisible(False)
            self.ui.progress_bar.setFormat("Playnlast complete create")
            self.ui.progress_bar.setProperty("value", 99)
            os.unlink(self.filename)
            self.prepare_viewport(active=False)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("C: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    # playpause timeslider
    def play_pause(self):
        if self.ui.play_pause.isChecked():
            cmds.play(state=True)
            name = "pause"
        else:
            name = "play"
            cmds.play(state=False)

        QtCore.QCoreApplication.processEvents()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/{}".format(name)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.play_pause.setIcon(icon)


from _maya.utils import resources
