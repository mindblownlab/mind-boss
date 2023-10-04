import copy
import os
import sys
from importlib import reload
from _blender.utils import util

reload(util)


class MBAsset:
    parent = None
    data_asset = None
    data_shot = None

    def __init__(self, parent):
        self.parent = parent

    def check_data(self):
        try:
            data_path = {
                "asset_type": self.parent._context.get("asset_type"),
                "asset": self.parent._context.get("asset")
            }
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("asset_data").format(**data_path))
            if not os.path.exists(path):
                path_folder = os.path.dirname(path)
                if not os.path.exists(path_folder):
                    os.makedirs(path_folder)

                data = copy.deepcopy(self.parent._context)
                data.update({"frame_range": [1, 144]})
                progress = {}
                for prg in self.parent._project.get("steps").get("assets"):
                    progress[prg] = "rts"
                data.update({"progress": progress})
                try:
                    data.pop("path")
                    data.pop("version")
                except:
                    pass
                util.storage(data, path, replace=True)
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def get_data(self):
        try:
            if self.parent._context.get("type") == "asset":
                current_asset = copy.deepcopy(self.parent._context)
                asset = list(filter(lambda ast: ast.get("asset") == current_asset.get("asset"), self.parent._assets))
                if asset:
                    return asset[0]
                else:
                    return self.parent._context
        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def update_data(self, data):
        try:
            data_path = {
                "asset_type": self.parent._context.get("asset_type"),
                "asset": self.parent._context.get("asset")
            }
            path = os.path.join(self.parent._project.get("path"), self.parent._templates.get("asset_data").format(**data_path))
            path = os.path.normpath(path)
            path = path.replace("\\", "/")
            if os.path.exists(path) and data:
                util.storage(path=path, data=data, replace=True)

        except Exception as error:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))

    def report(self):
        path = os.path.join(util.get_path_project(), "scenes", "SC01", "*", "*")
        print(path)

        # data = []
        # for shot in glob(shots):
        #     if "Animation" in shot:
        #         anim_path = os.path.join(shot, "ma", "*.ma")
        #         files = glob(anim_path)
        #         max_file = max(files, key=os.path.getctime)
        #         start = ""
        #         if len(files) > 1:
        #             start = "started"
        #
        #         data_shot = {
        #             "shot": os.path.basename(os.path.dirname(shot)),
        #             "create": datetime.datetime.strptime(time.ctime(os.path.getctime(shot)), "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d"),
        #             "name": os.path.basename(max_file),
        #             "start animation": start,
        #             "update": datetime.datetime.strptime(time.ctime(os.path.getmtime(shot)), "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d"),
        #             "version": len(files)
        #
        #         }
        #         data.append(data_shot)
        #
        # df = pd.DataFrame(data)
        # # print(tabulate(df, headers='keys', tablefmt='html'))
        # df2 = df.copy()
        # with pd.ExcelWriter('SC01.xlsx') as writer:
        #     df2.to_excel(writer, sheet_name='SC01')
