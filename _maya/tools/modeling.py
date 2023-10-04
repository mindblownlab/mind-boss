import copy
import os
import sys
from importlib import reload
from utils import util

reload(util)


class MBToolModeling:
    parent = None

    def __init__(self, parent):
        self.parent = parent