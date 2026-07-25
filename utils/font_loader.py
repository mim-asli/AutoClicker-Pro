# utils/font_loader.py

import os
import ctypes

WM_FONTCHANGE = 0x001D
HWND_BROADCAST = 0xFFFF

def register_vazirmatn_font():
    """ثبت بومی و جلسه‌ای فونت‌های وزیرمتن در سیستم‌عامل ویندوز"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ttf_files = [
        "Vazirmatn-Regular.ttf",
        "Vazirmatn-Bold.ttf",
        "Vazirmatn-Medium.ttf",
        "Vazirmatn-SemiBold.ttf"
    ]
    loaded = 0
    for file in ttf_files:
        path = os.path.join(base_dir, file)
        if os.path.exists(path):
            res = ctypes.windll.gdi32.AddFontResourceW(path)
            if res > 0:
                loaded += 1

    if loaded > 0:
        try:
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_FONTCHANGE, 0, 0, 0x0002, 1000, None
            )
        except Exception:
            pass