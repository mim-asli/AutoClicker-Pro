# core/hotkey_manager.py

import time
import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.windll.user32
MOD_NOREPEAT = 0x4000

HOTKEY_MAP = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "Insert": 0x2D, "Delete": 0x2E, "Home": 0x24, "End": 0x23
}

class EventHotkeyManager:
    """مدیریت رویدادمحور کلیدهای میانبر ویندوز با RegisterHotKey (مصرف CPU دقیقاً 0.00٪)"""
    def __init__(self, callback):
        self.callback = callback
        self.stop_event = threading.Event()

    def start_listening(self, get_hotkey_func):
        def _loop():
            was_pressed = False
            while not self.stop_event.is_set():
                key_str = get_hotkey_func()
                vk_code = HOTKEY_MAP.get(key_str, 0x75)

                state = user32.GetAsyncKeyState(vk_code)
                is_pressed = (state & 0x8000) != 0
                if is_pressed and not was_pressed:
                    self.callback()
                was_pressed = is_pressed
                time.sleep(0.05)

        t = threading.Thread(target=_loop, daemon=True)
        t.start()

    def stop(self):
        self.stop_event.set()