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
    "Insert": 0x2D, "Delete": 0x2E, "Home": 0x24, "End": 0x23
}

class EventHotkeyManager:
    """مدیریت ۱۰۰٪ رویدادمحور کلیدهای میانبر با RegisterHotKey و GetMessageW (مصرف CPU 0.00%)"""
    def __init__(self, callback):
        self.callback = callback
        self.hotkey_id = 1001
        self.thread = None
        self.thread_id = None
        self.current_vk = 0x75  # F6
        self.running = False

    def start(self, key_str="F6"):
        self.stop()
        self.current_vk = HOTKEY_MAP.get(key_str, 0x75)
        self.running = True
        self.thread = threading.Thread(target=self._msg_loop, daemon=True)
        self.thread.start()

    def update_key(self, key_str):
        self.start(key_str)

    def _msg_loop(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        # ثبت کلید میانبر در نوار پیام‌های ترد
        if not user32.RegisterHotKey(None, self.hotkey_id, MOD_NOREPEAT, self.current_vk):
            return

        msg = wintypes.MSG()
        while self.running:
            # GetMessageW به صورت کاملاً غیربلاک‌کننده و رویدادمحور منتظر پیام ویندوز می‌ماند (0.00% CPU)
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res == 0 or res == -1:
                break
            if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                self.callback()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, self.hotkey_id)

    def stop(self):
        if self.running:
            self.running = False
            if self.thread_id:
                user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
            user32.UnregisterHotKey(None, self.hotkey_id)