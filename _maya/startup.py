from importlib import reload
from modules import main

reload(main)

try:
    mb_main.close()
except:
    pass

mb_main = main.MBMain()