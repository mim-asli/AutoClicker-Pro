# core/click_engine.py

import time
import atexit
import ctypes

PUL = ctypes.POINTER(ctypes.c_ulong)


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_input", _INPUT),
    ]


INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

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

    if click_type == "Double":
        inputs = (INPUT * 4)(inp_down, inp_up, inp_down, inp_up)
        ctypes.windll.user32.SendInput(4, ctypes.byref(inputs), ctypes.sizeof(INPUT))
    else:
        inputs = (INPUT * 2)(inp_down, inp_up)
        ctypes.windll.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))


def high_precision_sleep(seconds, stop_event=None):
    """تایمر ترکیبی دقیق با قابلیت توقف فوری و جلوگیری از مصرف بالای CPU"""
    if seconds <= 0:
        return

    end = time.perf_counter() + seconds
    while True:
        if stop_event is not None and stop_event.is_set():
            return
        rem = end - time.perf_counter()
        if rem <= 0:
            return
        if rem > 0.005:
            sleep_chunk = rem - 0.003
            if stop_event is not None:
                if stop_event.wait(timeout=sleep_chunk):
                    return
            else:
                time.sleep(min(sleep_chunk, 0.05))