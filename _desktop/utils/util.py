import os
import sys
from library import yaml
import math
import os.path, time
from unicodedata import normalize
from PyQt5 import uic


def get_root_path():
    return os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


def storage(data=None, path=None, replace=False):
    try:
        if data:
            if replace:
                with open(path, 'w') as outfile:
                    yaml.dump(data, outfile, default_flow_style=False)

            if not os.path.exists(path):
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                with open(path, 'w') as outfile:
                    yaml.dump(data, outfile, default_flow_style=False)
            else:
                return None
        else:
            if os.path.exists(path):
                with open(path) as fl:
                    return yaml.safe_load(fl)
            else:
                return None
    except Exception as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error: : {}, {}, {}, {}".format(error, exc_type, fname, exc_tb.tb_lineno))
        return None


def get_size_file(path=None):
    file_stats = os.stat(path)
    return {
        "size": file_stats.st_size,
        "bytes": convert_size(file_stats.st_size)
    }


def get_data_file(path):
    return {
        "created": time.ctime(os.path.getctime(path)),
        "last_modified": time.ctime(os.path.getmtime(path)),
    }


def convert_size(size):
    if size == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return "%s %s" % (s, size_name[i])


def no_accents(value=""):
    return normalize('NFKD', value).encode('ASCII', 'ignore').decode('ASCII')


def get_settings(file):
    if os.path.exists(file):
        with open(file, 'r') as data:
            return yaml.safe_load(data)


def set_storage(data, file):
    file = file.replace('\\', '/')
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, 'w') as seq_file:
        yaml.dump(data, seq_file, default_flow_style=False)


def get_style(name='style'):
    path = os.path.join(get_root_path(), 'ui', '{}.qss'.format(name))
    with open(path, 'r') as fh:
        return fh.read()


def get_ui(name='main'):
    return os.path.join(get_root_path(), 'ui', '{}.ui'.format(name))


def load_ui(name='main', target=None):
    if target is None:
        return uic.loadUi(get_ui(name), target)
    else:
        return uic.loadUi(get_ui(name))


def get_ffmpeg():
    try:
        return os.path.normpath(os.path.join(get_root_path(), "library", "ffmpeg", "bin", "ffmpeg.exe"))
    except:
        return "ffmpeg path error"


def get_database(name="templates"):
    path = os.path.join(get_root_path(), "database", "{}.yml".format(name))
    path = os.path.normpath(path)
    return storage(path=path)
