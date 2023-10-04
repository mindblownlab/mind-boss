#!J:\desktop-packages\_Output\Python3\Debug\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'OpenTimelineIO==0.14.0.dev1','console_scripts','otioconvert'
__requires__ = 'OpenTimelineIO==0.14.0.dev1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('OpenTimelineIO==0.14.0.dev1', 'console_scripts', 'otioconvert')()
    )
