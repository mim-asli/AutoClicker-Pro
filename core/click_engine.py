# core/click_engine.py

import time
import atexit
import ctypes
from ctypes import wintypes

PUL = ctypes.POINTER(ctypes.c_ulong)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_input", _INPUT)
    ]

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN   = 0x0002
MOUSEEVENTF_LEFTUP     = 0x0004
MOUSEEVENTF_RIGHTDOWN  = 0x0008
MOUSEEVENTF_RIGHTUP    = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP   = 0x0040

# 👈 اصلاح نقد ۳: ثبت پاکسازی timeEndPeriod با atexit موقع بستن برنامه
try:
    ctypes.windll.winmm.timeBeginPeriod(1)
    atexit.register(lambda: ctypes.windll.winmm.timeEndPeriod(1))
except Exception:
    pass

def win32_fast_click(button="left", click_type="Single", x=None, y=None):
    if x is not None and y is not None:
        ctypes.windll.user32.SetCursorPos(int(x), int(y))

    down_flag = MOUSEEVENTF_LEFTDOWN
    up_flag = MOUSEEVENTF_LEFTUP
    if button == "right":
        down_flag, up_flag = MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
    elif button == "middle":
        down_flag, up_flag = MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP

    inp_down = INPUT(type=INPUT_MOUSE)
    inp_down.mi = MOUSEINPUT(0, 0, 0, down_flag, 0, None)
    inp_up = INPUT(type=INPUT_MOUSE)
    inp_up.mi = MOUSEINPUT(0, 0, 0, up_flag, 0, None)

    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))

    if click_type == "Double":
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))

def high_precision_sleep(seconds):
    """تایمر ترکیبی دقیق برای جلوگیری از قفل شدن CPU در بازه‌های بزرگ"""
    if seconds <= 0:
        return
    start = time.perf_counter()
    while (time.perf_counter() - start) < seconds:
        rem = seconds - (time.perf_counter() - start)
        if rem > 0.002:
            time.sleep(0.001)