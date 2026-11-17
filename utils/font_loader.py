# utils/font_loader.py

import os
import sys
import glob
import ctypes

FR_PRIVATE = 0x10


def _get_font_dirs():
    dirs = []
    if getattr(sys, "frozen", False):
        dirs.append(os.path.dirname(sys.executable))
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in dirs:
        dirs.append(base_dir)
    return dirs


def register_vazirmatn_font():
    """ثبت خصوصی و سریع فونت‌های وزیرمتن در ویندوز"""
    if sys.platform != "win32":
        return

    loaded = set()
    for folder in _get_font_dirs():
        for path in glob.glob(os.path.join(folder, "Vazirmatn-*.ttf")):
            if path in loaded:
                continue
            try:
                res = ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0)
                if res > 0:
                    loaded.add(path)
            except Exception:
                pass