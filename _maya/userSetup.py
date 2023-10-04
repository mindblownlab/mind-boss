import os
from maya import cmds, mel

if os.environ['MBL_PROJECT_ROOT']:
    mel.eval('setProject("{path}")'.format(path=os.environ['MBL_PROJECT_ROOT'].replace("\\", "/")))

cmds.evalDeferred('import startup')