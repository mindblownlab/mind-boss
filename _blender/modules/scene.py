import copy
import os
import sys
from importlib import reload

import bpy

from _blender.utils import util

reload(util)


class MBScene:
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def publish(self):
        try:
            convert_version = "{:03d}".format(1)
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
                template_name = "asset_publish"
            else:
                filename = "{}_{}".format(self.parent._context.get("shot").lower(), self.parent._context.get("step").lower())
                data_path = {
                    "sequence": self.parent._context.get("sequence"),
                    "shot": self.parent._context.get("shot"),
                    "step": self.parent._context.get("step"),
                    "step_shot": self.parent._context.get("step").lower(),
                    "version": convert_version,
                    "name": filename,
                    "ext": self.parent._project.get("engine").get("ext")
                }
                template_name = "shot_publish"
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get(template_name).format(**data_path))
            path = os.path.normpath(path)
            path = path.replace("\\", "/")
            asset_path = os.path.dirname(path)

            if not os.path.exists(asset_path):
                os.makedirs(asset_path)

            if self.parent._context.get("step") == "LookDev":
                bpy.ops.object.select_all(action='DESELECT')
                for collection in bpy.context.scene.collection.children:
                    for obj in collection.all_objects:
                        try:
                            if obj.type == "MESH":
                                is_cache = list(filter(lambda m: "_Cache" in m[0], obj.modifiers.items()))
                                if len(is_cache) <= 0:
                                    bpy.ops.object.select_all(action='DESELECT')
                                    bpy.context.view_layer.objects.active = obj
                                    obj.select_set(True)
                                    cache_name = "{}_Cache".format(obj.name)
                                    bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
                                    bpy.ops.object.modifier_add(type='SUBSURF')
                                    bpy.context.object.modifiers["MeshSequenceCache"].name = cache_name
                                else:
                                    if self.parent._context.get("asset") not in obj.name:
                                        obj.name = "{}_{}".format(self.parent._context.get("asset"), obj.name)
                                    modifie = list(filter(lambda mdf: mdf.type == "MESH_SEQUENCE_CACHE", obj.modifiers))
                                    if modifie:
                                        modifie = modifie[0]
                                        modifie.name = obj.name
                        except:
                            pass
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
                print(path)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def check_scene(self):
        message = '''
            <b>CHECK SCENE SETTINGS</b><br/>
            ----------------------------------<br/>
            Resolution: {resolution}<br/>
            FPS: {fps}<br/>
            Aspect: {aspect}<br/>
            Frame range: {framerange}'''.format(
            resolution="x".join(list(map(lambda r: str(r), self.parent._project.get('resolution')))),
            fps=self.parent._project.get('fps'),
            aspect=int(self.parent._project.get("aspect")),
            framerange="-".join(list(map(lambda r: str(r), self.get_context_data().get('frame_range')))))

    def set_scene(self):
        project_data = self.parent.mb_project.get_data()
        data_shot = self.parent.mb_shot.get_data()
        width, height = project_data.get('resolution')
        aspect = project_data.get('aspect')
        frame_start, frame_end = data_shot.get("frame_range")
        fps = project_data.get('fps')

        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.pixel_aspect_x = aspect
        bpy.context.scene.render.pixel_aspect_y = aspect
        bpy.context.scene.view_layers["ViewLayer"].use_pass_diffuse_direct = True
        bpy.context.scene.view_layers["ViewLayer"].eevee.use_pass_volume_direct = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_emit = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_environment = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_object = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_material = True
        bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_asset = True
        bpy.context.scene.render.filepath = os.path.join(project_data.get("path"), "assets")
        bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR'
        bpy.context.scene.render.fps = fps

        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_end = frame_end

        try:
            bpy.data.scenes["Scene"].node_tree.nodes["File Output"].base_path = os.path.join(project_data.get("path"), "assets")
            bpy.data.scenes["Scene"].node_tree.nodes["File Output"].format.file_format = 'PNG'
        except:
            pass

        try:
            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            area.spaces[0].region_3d.view_perspective = 'CAMERA'
        except:
            pass

    def get_context_data(self):
        context = copy.deepcopy(self.parent._context)
        return context
