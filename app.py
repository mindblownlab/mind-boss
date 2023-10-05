import os
import sys

root_path = os.path.join(sys.argv[1])
libraries_path = os.path.join(root_path, "library")

# os.environ["PYTHONPATH"] = os.path.join(root_path, "Python")

if root_path not in sys.path:
    sys.path.append(root_path)

if libraries_path not in sys.path:
    sys.path.append(libraries_path)

print(os.environ["PYTHONPATH"])
print(root_path)
print(libraries_path)

from PyQt5 import QtWidgets
from importlib import reload
from _desktop.modules import main

reload(main)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mb_main = main.MBMain()
    app.exec_()
