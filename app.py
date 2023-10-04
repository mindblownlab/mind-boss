import sys
import os

root_path = os.path.join(os.path.dirname(__file__))
libraries_path = os.path.join(root_path, "library")

if root_path not in sys.path:
    sys.path.append(root_path)

if libraries_path not in sys.path:
    sys.path.append(libraries_path)

from PyQt5 import QtWidgets
from importlib import reload
from _desktop.modules import main

reload(main)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mb_main = main.MBMain()
    app.exec_()