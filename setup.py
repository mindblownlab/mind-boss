from cx_Freeze import setup, Executable
import sys

company_name = "Mindblownlab"
product_name = "BossMind"

shortcut_table = [
    ("DesktopShortcut",  # Shortcut
     "DesktopFolder",  # Directory_
     "BossMind",  # Name
     "TARGETDIR",  # Component_
     "[TARGETDIR]boss_mind.exe",  # Target
     None,  # Arguments
     None,  # Description
     None,  # Hotkey
     None,  # Icon
     None,  # IconIndex
     None,  # ShowCmd
     'TARGETDIR'  # WkDir
     )
]

msi_data = {"Shortcut": shortcut_table}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "path": sys.path,
    "excludes": ["tkinter"],
    "include_msvcr": True,
    "zip_include_packages": ["encodings"],
    "include_files": ["_blender", "_cinema", "_desktop", "_maya", "database", "library", "Python", "resources", "ui"]
}

bdist_msi_options = {
    "environment_variables": [
        ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
    ],
    "upgrade_code": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}",
    "add_to_path": True,
    "data": msi_data,
    "initial_target_dir": r"c:\{}\{}".format(company_name, product_name),
    "target_name": product_name,
    "summary_data": {"author": "Mindblowblab Studio", "comments": "Pipeline mindblownlab"}
}

setup(
    name=product_name,
    maintainer="Mindblown Lab Studio",
    author=company_name,
    author_email="support@mindblownlab.studio",
    description="Pipeline mindblownlab",
    version="1.0",
    executables=[Executable(r"app.py", base=base, icon="icon.ico")],
    options={"bdist_msi": bdist_msi_options, "build_exe": build_exe_options}
)
