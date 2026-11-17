# core/hotkey_manager.py

import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

HOTKEY_MAP = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "Insert": 0x2D, "Delete": 0x2E, "Home": 0x24, "End": 0x23,
}


class EventHotkeyManager:
    """مدیریت رویدادمحور کلیدهای میانبر با RegisterHotKey و GetMessageW"""

    def __init__(self, callback):
        self.callback = callback
        self.hotkey_id = 1001
        self.thread = None
        self.thread_id = None
        self._ready_event = threading.Event()
        self.current_vk = 0x75  # F6
        self.running = False

    def start(self, key_str="F6"):
        self.stop()
        self.current_vk = HOTKEY_MAP.get(key_str, 0x75)
        self.running = True
        self._ready_event.clear()
        self.thread = threading.Thread(target=self._msg_loop, daemon=True)
        self.thread.start()
        self._ready_event.wait(timeout=1.0)

    def update_key(self, key_str):
        self.start(key_str)

    def _msg_loop(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        registered = bool(
            user32.RegisterHotKey(None, self.hotkey_id, MOD_NOREPEAT, self.current_vk)
        )
        self._ready_event.set()
        if not registered:
            self.running = False
            return

        msg = wintypes.MSG()
        try:
            while self.running:
                res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res == 0 or res == -1:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    try:
                        self.callback()
                    except Exception:
                        pass
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, self.hotkey_id)
            self.thread_id = None

    def stop(self):
        if self.running or (self.thread and self.thread.is_alive()):
            self.running = False
            if self.thread_id:
                user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)
        self.thread = None