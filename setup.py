# setup.py

import sys
import os
import glob
from cx_Freeze import setup, Executable

include_files = glob.glob("Vazirmatn-*.ttf") + glob.glob("*.ttf")
if os.path.exists("icon.ico"):
    include_files.append("icon.ico")

include_files = list(set(include_files))

font_table = [
    ("Vazirmatn-Regular.ttf", "Vazirmatn (TrueType)"),
    ("Vazirmatn-Bold.ttf", "Vazirmatn Bold (TrueType)"),
    ("Vazirmatn-Medium.ttf", "Vazirmatn Medium (TrueType)"),
    ("Vazirmatn-SemiBold.ttf", "Vazirmatn SemiBold (TrueType)")
]

shortcut_table = [
    (
        "DesktopShortcut",
        "DesktopFolder",
        "AutoClicker Pro",
        "TARGETDIR",
        "[TARGETDIR]AutoClickerPro.exe",
        None,
        "Auto Clicker Pro Application",
        None,
        None,
        None,
        None,
        'TARGETDIR'
    )
]

bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\AutoClickerPro",
    "data": {
        "Shortcut": shortcut_table,
        "Font": font_table
    }
}

build_exe_options = {
    "packages": [
        "ttkbootstrap",
        "pyautogui",
        "tkinter",
        "PIL",
        "threading",
        "datetime",
        "time",
        "pystray"
    ],
    "include_files": include_files,
    "include_msvcr": True
}

base = None
if sys.platform == "win32":
    base = "gui"

setup(
    name="AutoClickerPro",
    version="1.1.0",
    description="Auto Clicker Pro Application",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[
        Executable(
            "main.py",  # 👈 نقطه ورود جدید به ساختار ماژولار
            base=base,
            target_name="AutoClickerPro.exe",
            icon="icon.ico" if os.path.exists("icon.ico") else None
        )
    ]
)