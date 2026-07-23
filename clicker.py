import os
import sys
import time
import random
import datetime
import threading
import ctypes
from ctypes import wintypes
import winsound
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter.font as tkfont

# ==============================================================================
# 🔤 لود و تزریق جلسه‌ای فونت وزیرمتن در ویندوز
# ==============================================================================
WM_FONTCHANGE = 0x001D
HWND_BROADCAST = 0xFFFF

def register_vazirmatn_font():
    font_dir = os.path.dirname(os.path.abspath(__file__))
    ttf_files = [
        "Vazirmatn-Regular.ttf",
        "Vazirmatn-Bold.ttf",
        "Vazirmatn-Medium.ttf",
        "Vazirmatn-SemiBold.ttf"
    ]
    loaded = 0
    for file in ttf_files:
        path = os.path.join(font_dir, file)
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

register_vazirmatn_font()

# کتابخانه آیکون سینی ویندوز
try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False

# ==============================================================================
# 🌐 سیستم جامع ترجمه دو زبانه (فارسی / انگلیسی)
# ==============================================================================
TRANSLATIONS = {
    "FA": {
        "tab_auto": " ⚡ اتوکلیکر سریع ",
        "tab_sched": " 🎯 زمان‌بندی نقاط ",
        "tab_help": " ⚙️ تنظیمات عمومی ",
        "sub_title": "سبک، سریع و فوق‌العاده دقیق",
        "btn_mouse": "دکمه موس:",
        "click_type": "نوع کلیک:",
        "interval_ms": "فاصله زمانی (میلی‌ثانیه):",
        "jitter": "🎲 رندوم‌سازی کلیک (ضد شناسایی ±10ms)",
        "sound": "🔊 پخش صدای هشدار هنگام شروع/توقف",
        "theme_mode": "حالت تم (Mode):",
        "accent_color": "رنگ تم نئونی:",
        "lang_select": "زبان (Language):",
        "always_top": "📌 پنجره همیشه بالا باشد (Always On Top)",
        "frame_config": " ⚙️ تنظیمات دکمه و سرعت ",
        "frame_visuals": " 🎨 ظاهر، زبان و شناور‌سازی ",
        "duration_title": " ⏱️ مدت زمان کلیک (توقف خودکار) ",
        "unlimited": "♾️ کلیک نامحدود (توقف دستی)",
        "auto_stop_after": "⏱️ توقف خودکار پس از: ",
        "seconds": "ثانیه",
        "start_time_title": " ⏰ زمان شروع کلیک ",
        "start_instant": "⚡ شروع فوری (مستقیم با زدن کلید یا دکمه)",
        "start_scheduled": "⏰ شروع در ساعت مشخص: ",
        "hotkey_title": " ⌨️ انتخاب کلید میانبر ",
        "hotkey_lbl": "کلید شروع/توقف:",
        "pos_title": " 📍 موقعیت کلیک موس ",
        "pos_current": "موقعیت فعلی نشانگر موس",
        "pos_fixed": "مختصات ثابت",
        "select_pos": "🎯 انتخاب",
        "status_title": " 📊 وضعیت و اجرای سریع ",
        "status_stopped": "🔴 وضعیت: متوقف شده",
        "status_running": "🟢 وضعیت: در حال اجرا...",
        "status_waiting": "⏳ منتظر زمان شروع...",
        "click_count": "تعداد کلیک‌ها: ",
        "total_clicks": "مجموع کلیک‌ها: ",
        "status_ready": "🟢 سیستم آماده به کار است",
        "hotkey_tip": "💡 برای شروع یا توقف کلیک دکمه {key} را بزنید.",
        "btn_start": "▶ ({key}) شروع کلیک پیوسته",
        "btn_stop": "⏹ ({key}) توقف کلیک",
        "run_time": "⏱️ زمان اجرا: ",
        # تب زمان‌بندی نقاط
        "sched_cfg_title": " ⚙️ تنظیمات زمان و سرعت ",
        "sched_time_lbl": "زمان شروع (ساعت:دقیقه:ثانیه):",
        "sched_delay_lbl": "تاخیر بین کلیک‌ها (میلی‌ثانیه):",
        "sched_pts_title": " 🎯 مختصات نقاط کلیک ",
        "sched_add_btn": "➕ افزودن نقطه",
        "sched_rem_btn": "➖ حذف نقطه",
        "sched_status_ready": "وضعیت: آماده به کار",
        "sched_start_btn": "▶ شروع زمان‌بندی",
        "sched_stop_btn": "⏹ توقف",
        "point_prefix": "نقطه ",
        # کارت‌های ویژگی سمت چپ
        "f1_t": "🌐 دو زبانه (FA / EN)",
        "f1_d": "پشتیبانی کامل از فارسی و انگلیسی",
        "f2_t": "☀️ سوییچ تم روشن و تاریک",
        "f2_d": "امکان تغییر حالت بین Dark و Light",
        "f3_t": "📌 پنجره شناور (Always On Top)",
        "f3_d": "نگه‌داشتن پنجره روی بقیه بازی‌ها",
        "f4_t": "🎨 تغییر تم نئونی زنده",
        "f4_d": "امکان انتخاب رنگ سبز، آبی و بنفش",
        "f5_t": "⚡ موتور کلیک Win32",
        "f5_d": "سرعت مایکروثانیه‌ای (۱۰۰۰+ کلیک)",
        "f6_t": "⏱️ توقف خودکار زمان‌بندی",
        "f6_d": "محدود کردن کلیک به ۱۰ ثانیه",
        # راهنما
        "help_quick_title": "🚀 راهنمای سریع استفاده:",
        "help_quick_1": "۱. تنظیمات کلیک (دکمه موس، سرعت و زمان) را انجام دهید.",
        "help_quick_2": "۲. کلید میانبر دلخواه (مثلاً F6) را انتخاب کنید.",
        "help_quick_3": "۳. کلید میانبر را در هر کجای ویندوز بزنید تا کلیک فعال یا متوقف شود.",
        "help_features_title": "⚡ امکانات برجسته:",
        "help_feat_1": "• موتور کلیک لایه پایین Win32 با سرعت مایکروثانیه‌ای (1000+ CPS)",
        "help_feat_2": "• امکان شناورسازی پنجره روی بقیه بازی‌ها (Always On Top)",
        "help_feat_3": "• تایمر توقف خودکار و زمان‌بندی شروع رأس ساعت مشخص",
        "help_feat_4": "• مینی‌مایز به سینی ویندوز (System Tray) هنگام بستن برنامه"
    },
    "EN": {
        "tab_auto": " ⚡ Fast Clicker ",
        "tab_sched": " 🎯 Multi-Point Scheduler ",
        "tab_help": " ⚙️ General Settings ",
        "sub_title": "Lightweight, Ultra-Fast & Precise",
        "btn_mouse": "Mouse Button:",
        "click_type": "Click Type:",
        "interval_ms": "Interval (ms):",
        "jitter": "🎲 Randomize Interval (Anti-Detect ±10ms)",
        "sound": "🔊 Play Alert Beep on Start/Stop",
        "theme_mode": "Theme Mode:",
        "accent_color": "Neon Accent:",
        "lang_select": "Language:",
        "always_top": "📌 Always On Top Window",
        "frame_config": " ⚙️ Button & Speed Settings ",
        "frame_visuals": " 🎨 Appearance & Floating ",
        "duration_title": " ⏱️ Click Duration (Auto-Stop) ",
        "unlimited": "♾️ Unlimited Clicks (Manual Stop)",
        "auto_stop_after": "⏱️ Auto-stop after: ",
        "seconds": "sec",
        "start_time_title": " ⏰ Start Time ",
        "start_instant": "⚡ Instant Start (Press Hotkey / Button)",
        "start_scheduled": "⏰ Start at specific time: ",
        "hotkey_title": " ⌨️ Global Hotkey ",
        "hotkey_lbl": "Start/Stop Key:",
        "pos_title": " 📍 Mouse Location ",
        "pos_current": "Current Cursor Location",
        "pos_fixed": "Custom Fixed Position",
        "select_pos": "🎯 Select",
        "status_title": " 📊 Status & Control ",
        "status_stopped": "🔴 Status: Stopped",
        "status_running": "🟢 Status: Clicking...",
        "status_waiting": "⏳ Waiting for target time...",
        "click_count": "Click Count: ",
        "total_clicks": "Total Clicks: ",
        "status_ready": "🟢 System Ready",
        "hotkey_tip": "💡 Press {key} anytime to Start or Stop clicking.",
        "btn_start": "▶ ({key}) Start Continuous Clicks",
        "btn_stop": "⏹ ({key}) Stop Clicking",
        "run_time": "⏱️ Runtime: ",
        # Multi-point Scheduler Tab
        "sched_cfg_title": " ⚙️ Timer & Speed Settings ",
        "sched_time_lbl": "Start Time (HH:MM:SS):",
        "sched_delay_lbl": "Delay Between Clicks (ms):",
        "sched_pts_title": " 🎯 Multi-Point Coordinates ",
        "sched_add_btn": "➕ Add Point",
        "sched_rem_btn": "➖ Remove Point",
        "sched_status_ready": "Status: Ready",
        "sched_start_btn": "▶ Start Schedule",
        "sched_stop_btn": "⏹ Stop",
        "point_prefix": "Point ",
        # Left Feature Cards
        "f1_t": "🌐 Multilingual (FA / EN)",
        "f1_d": "Full support for English & Persian",
        "f2_t": "☀️ Light & Dark Themes",
        "f2_d": "Toggle between Light and Dark mode",
        "f3_t": "📌 Always On Top Window",
        "f3_d": "Keep window floating above games",
        "f4_t": "🎨 Live Neon Accents",
        "f4_d": "Choose Green, Blue & Purple accents",
        "f5_t": "⚡ Win32 Click Engine",
        "f5_d": "Microsecond speed (1000+ CPS)",
        "f6_t": "⏱️ Auto-Stop Timer",
        "f6_d": "Limit clicking duration to N seconds",
        # Help Tab
        "help_quick_title": "🚀 Quick Start Guide:",
        "help_quick_1": "1. Configure click interval (ms), mouse button, and click type.",
        "help_quick_2": "2. Select your preferred global hotkey (e.g., F6 or F7).",
        "help_quick_3": "3. Press your hotkey anywhere in Windows to Start or Stop clicking.",
        "help_features_title": "⚡ Key Features:",
        "help_feat_1": "• Low-level Win32 SendInput engine for ultra-high speed (1000+ CPS)",
        "help_feat_2": "• Always On Top floating mode for full-screen games",
        "help_feat_3": "• Precise Auto-Stop Timer & Scheduled Start Time",
        "help_feat_4": "• Minimize to Windows System Tray on close"
    }
}

THEME_ACCENTS_FA = {
    "🟢 سبز نئونی": "#00FFB2",
    "🔵 آبی سایبرپانک": "#00D2FF",
    "🟣 بنفش گیمینگ": "#C77DFF"
}

THEME_ACCENTS_EN = {
    "🟢 Neon Green": "#00FFB2",
    "🔵 Cyberpunk Blue": "#00D2FF",
    "🟣 Gaming Purple": "#C77DFF"
}

BG_DARK = "#0B0F19"
SIDEBAR_BG = "#101622"
CARD_BG = "#161F2E"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#8B9BB4"

# ==============================================================================
# ⚡ موتور کلیک لایه پایین ویندوز (Win32 SendInput)
# ==============================================================================
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

try:
    ctypes.windll.winmm.timeBeginPeriod(1)
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
    if seconds <= 0:
        return
    start = time.perf_counter()
    while (time.perf_counter() - start) < seconds:
        rem = seconds - (time.perf_counter() - start)
        if rem > 0.002:
            time.sleep(0.001)

HOTKEY_MAP = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "Insert": 0x2D, "Delete": 0x2E, "Home": 0x24, "End": 0x23
}


class AutoClickerProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker Pro")
        self.root.geometry("1060x840")
        self.root.minsize(960, 680)

        self.current_lang = "FA"

        self.bg_dark = "#0B0F19"
        self.text_white = "#FFFFFF"
        self.text_muted = "#8B9BB4"
        self.root.configure(bg=self.bg_dark)

        self.font_family = "Vazirmatn"
        self.setup_vazir_theme()

        self.load_app_icon()

        self.current_accent = "#00FFB2"
        self.accent_labels = []
        self.feature_card_labels = []

        self.auto_running = False
        self.auto_click_count = 0
        self.sched_running = False
        self.points_data = []

        self.start_app_time = time.time()
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.build_main_layout()

        for _ in range(8):
            self.add_point_row()

        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        self.update_status_bar_loop()

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def setup_vazir_theme(self):
        style = tb.Style()
        for s in [".", "TLabel", "TButton", "TEntry", "TRadiobutton", "TCheckbutton", "TCombobox", "TLabelframe.Label", "TLabelframe"]:
            try:
                style.configure(s, font=(self.font_family, 10))
            except Exception:
                pass

        try:
            self.root.option_add("*Font", (self.font_family, 10))
        except Exception:
            pass

    def load_app_icon(self):
        self.icon_image_obj = None
        for icon_name in ["icon.ico", "icon.png"]:
            if os.path.exists(icon_name):
                try:
                    self.icon_image_obj = Image.open(icon_name)
                    if icon_name.endswith(".ico"):
                        self.root.iconbitmap(icon_name)
                    else:
                        img = ImageTk.PhotoImage(self.icon_image_obj)
                        self.root.iconphoto(False, img)
                    break
                except Exception:
                    pass

    def minimize_to_tray(self):
        if not HAS_PYSTRAY:
            self.root.destroy()
            return

        self.root.withdraw()

        if self.icon_image_obj:
            tray_img = self.icon_image_obj
        else:
            tray_img = Image.new('RGB', (64, 64), color=(0, 255, 178))

        hk_str = self.auto_hotkey_var.get()
        menu = pystray.Menu(
            pystray.MenuItem("Show Auto Clicker Pro", self.restore_from_tray, default=True),
            pystray.MenuItem(f"Start / Stop ({hk_str})", lambda icon, item: self.root.after(0, self.toggle_auto_clicker)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_app)
        )

        self.tray_icon = pystray.Icon("AutoClickerPro", tray_img, "Auto Clicker Pro", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self, icon=None, item=None):
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)

    # 👈 سوییچ زنده زبان و به‌روزرسانی ۱۰۰٪ تمام اجزا (از جمله تب ۲ و ۳)
    def _on_language_changed(self, event=None):
        lang_str = self.lang_var.get()
        self.current_lang = "EN" if "English" in lang_str else "FA"

        if self.current_lang == "EN":
            self.combo_mode.config(values=["🌙 Dark", "☀️ Light"])
            self.combo_accent.config(values=list(THEME_ACCENTS_EN.keys()))
            if "تاریک" in self.mode_theme_var.get(): self.mode_theme_var.set("🌙 Dark")
            elif "روشن" in self.mode_theme_var.get(): self.mode_theme_var.set("☀️ Light")
            self.accent_theme_var.set("🟢 Neon Green")
        else:
            self.combo_mode.config(values=["🌙 تاریک (Dark)", "☀️ روشن (Light)"])
            self.combo_accent.config(values=list(THEME_ACCENTS_FA.keys()))
            if "Dark" in self.mode_theme_var.get(): self.mode_theme_var.set("🌙 تاریک (Dark)")
            elif "Light" in self.mode_theme_var.get(): self.mode_theme_var.set("☀️ روشن (Light)")
            self.accent_theme_var.set("🟢 سبز نئونی")

        # به‌روزرسانی متون تب‌ها
        self.notebook.tab(0, text=self.t("tab_auto"))
        self.notebook.tab(1, text=self.t("tab_sched"))
        self.notebook.tab(2, text=self.t("tab_help"))

        # به‌روزرسانی کارت‌های ویژگی سمت چپ
        for i, (t_key, d_key) in enumerate([
            ("f1_t", "f1_d"), ("f2_t", "f2_d"), ("f3_t", "f3_d"),
            ("f4_t", "f4_d"), ("f5_t", "f5_d"), ("f6_t", "f6_d")
        ]):
            if i < len(self.feature_card_labels):
                self.feature_card_labels[i][0].config(text=self.t(t_key))
                self.feature_card_labels[i][1].config(text=self.t(d_key))

        # به‌روزرسانی تب ۱
        self.frame_config.config(text=self.t("frame_config"))
        self.lbl_btn_mouse.config(text=self.t("btn_mouse"))
        self.lbl_click_type.config(text=self.t("click_type"))
        self.lbl_interval.config(text=self.t("interval_ms"))
        self.chk_jitter.config(text=self.t("jitter"))
        self.chk_sound.config(text=self.t("sound"))

        self.frame_duration.config(text=self.t("duration_title"))
        self.radio_dur1.config(text=self.t("unlimited"))
        self.radio_dur2.config(text=self.t("auto_stop_after"))
        self.lbl_sec.config(text=self.t("seconds"))

        self.frame_start_time.config(text=self.t("start_time_title"))
        self.radio_time1.config(text=self.t("start_instant"))
        self.radio_time2.config(text=self.t("start_scheduled"))

        self.frame_pos.config(text=self.t("pos_title"))
        self.radio_pos1.config(text=self.t("pos_current"))
        self.radio_pos2.config(text=self.t("pos_fixed"))
        self.btn_pick_pos.config(text=self.t("select_pos"))

        self.frame_status.config(text=self.t("status_title"))

        # به‌روزرسانی تب ۲ (زمان‌بندی نقاط - ترجمه کامل)
        self.frame_sched_cfg.config(text=self.t("sched_cfg_title"))
        self.lbl_sched_time.config(text=self.t("sched_time_lbl"))
        self.lbl_sched_delay.config(text=self.t("sched_delay_lbl"))
        self.frame_sched_pts.config(text=self.t("sched_pts_title"))
        self.btn_sched_add.config(text=self.t("sched_add_btn"))
        self.btn_sched_rem.config(text=self.t("sched_rem_btn"))
        self.sched_status_label.config(text=self.t("sched_status_ready"))
        self.sched_start_btn.config(text=self.t("sched_start_btn"))
        self.sched_stop_btn.config(text=self.t("sched_stop_btn"))

        # به‌روزرسانی سطرهای نقاط در تب ۲
        prefix = self.t("point_prefix")
        btn_txt = self.t("select_pos")
        for idx, p in enumerate(self.points_data):
            p["lbl_p"].config(text=f"{prefix}{idx+1}: X=")
            p["btn_pick"].config(text=btn_txt)

        # به‌روزرسانی تب ۳ (تنظیمات عمومی و راهنما)
        self.frame_visuals.config(text=self.t("frame_visuals"))
        self.lbl_theme_mode.config(text=self.t("theme_mode"))
        self.lbl_accent_color.config(text=self.t("accent_color"))
        self.lbl_lang_select.config(text=self.t("lang_select"))
        self.chk_topmost.config(text=self.t("always_top"))

        self.frame_hotkey.config(text=self.t("hotkey_title"))
        self.lbl_hk.config(text=self.t("hotkey_lbl"))

        self.lbl_help_q_title.config(text=self.t("help_quick_title"))
        self.lbl_help_q1.config(text=self.t("help_quick_1"))
        self.lbl_help_q2.config(text=self.t("help_quick_2"))
        self.lbl_help_q3.config(text=self.t("help_quick_3"))
        self.lbl_help_f_title.config(text=self.t("help_features_title"))
        self.lbl_help_f1.config(text=self.t("help_feat_1"))
        self.lbl_help_f2.config(text=self.t("help_feat_2"))
        self.lbl_help_f3.config(text=self.t("help_feat_3"))
        self.lbl_help_f4.config(text=self.t("help_feat_4"))

        # به‌روزرسانی نوار وضعیت زیرین
        self.lbl_ready.config(text=self.t("status_ready"))
        self.lbl_total_clicks_bottom.config(text=self.t("total_clicks") + str(self.auto_click_count))
        self.lbl_sub_brand.config(text=self.t("sub_title"))

        if self.auto_running:
            self.lbl_auto_status.config(text=self.t("status_running"))
        else:
            self.lbl_auto_status.config(text=self.t("status_stopped"))

        self._on_hotkey_changed()
        self._update_click_ui()

    def _on_mode_theme_changed(self, event=None):
        mode = self.mode_theme_var.get()
        style = tb.Style()

        if "روشن" in mode or "Light" in mode:
            style.theme_use("flatly")
            self.bg_dark = "#F1F5F9"
            self.text_white = "#0F172A"
            self.text_muted = "#475569"
        else:
            style.theme_use("darkly")
            self.bg_dark = "#0B0F19"
            self.text_white = "#FFFFFF"
            self.text_muted = "#8B9BB4"

        self.root.configure(bg=self.bg_dark)
        self.setup_vazir_theme()
        self.lbl_title_brand.config(foreground=self.text_white)
        self.lbl_sub_brand.config(foreground=self.text_muted)
        self.lbl_total_clicks_bottom.config(foreground=self.text_white)

    # 👈 به‌روزرسانی رنگ حاشیه‌ها همگام با رنگ تم نئونی (ویژگی تغییر رنگ حاشیه)
    def _on_accent_changed(self, event=None):
        selected_theme = self.accent_theme_var.get()
        new_color = THEME_ACCENTS_EN.get(selected_theme) or THEME_ACCENTS_FA.get(selected_theme, "#00FFB2")
        self.current_accent = new_color

        for lbl in self.accent_labels:
            try:
                lbl.config(foreground=new_color)
            except Exception:
                pass

        # تغییر رنگ حاشیه کادرها در استایل
        style = tb.Style()
        try:
            style.configure("TLabelframe", bordercolor=new_color, lightcolor=new_color)
            style.configure("TLabelframe.Label", foreground=new_color)
            style.configure("Info.TLabelframe", bordercolor=new_color)
            style.configure("Primary.TLabelframe", bordercolor=new_color)
        except Exception:
            pass

        if not self.auto_running:
            self.lbl_auto_count.config(foreground=new_color)
        self.lbl_ready.config(foreground=new_color)

    def toggle_topmost(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def build_main_layout(self):
        main_container = tb.Frame(self.root)
        main_container.pack(fill=BOTH, expand=True, padx=12, pady=12)

        left_panel = tb.Frame(main_container, width=280, padding=15)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 12))

        self.lbl_title_brand = tb.Label(left_panel, text="AUTO ⚡", font=(self.font_family, 26, "bold"), foreground=self.text_white)
        self.lbl_title_brand.pack(anchor="w")

        lbl_brand_accent = tb.Label(left_panel, text="CLICKER PRO", font=(self.font_family, 22, "bold"), foreground=self.current_accent)
        lbl_brand_accent.pack(anchor="w")
        self.accent_labels.append(lbl_brand_accent)

        self.lbl_sub_brand = tb.Label(left_panel, text=self.t("sub_title"), font=(self.font_family, 9), foreground=self.text_muted)
        self.lbl_sub_brand.pack(anchor="w", pady=(0, 20))

        self.feature_card_labels = []
        for i in range(1, 7):
            card = tb.Frame(left_panel, padding=10)
            card.pack(fill=X, pady=4)
            lbl_t = tb.Label(card, text=self.t(f"f{i}_t"), font=(self.font_family, 10, "bold"), foreground=self.current_accent)
            lbl_t.pack(anchor="w")
            self.accent_labels.append(lbl_t)

            lbl_d = tb.Label(card, text=self.t(f"f{i}_d"), font=(self.font_family, 8), foreground=self.text_muted)
            lbl_d.pack(anchor="w")
            self.feature_card_labels.append((lbl_t, lbl_d))

        right_panel = tb.Frame(main_container)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)

        self.notebook = tb.Notebook(right_panel, bootstyle=PRIMARY)
        self.notebook.pack(fill=BOTH, expand=True)

        self.auto_tab = tb.Frame(self.notebook, padding=12)
        self.sched_tab = tb.Frame(self.notebook, padding=12)
        self.help_tab = tb.Frame(self.notebook, padding=12)

        self.notebook.add(self.auto_tab, text=self.t("tab_auto"))
        self.notebook.add(self.sched_tab, text=self.t("tab_sched"))
        self.notebook.add(self.help_tab, text=self.t("tab_help"))

        self.build_auto_tab()
        self.build_sched_tab()
        self.build_general_settings_tab()

        status_bar = tb.Frame(right_panel, padding=(12, 6))
        status_bar.pack(fill=X, side=BOTTOM, pady=(8, 0))

        self.lbl_ready = tb.Label(status_bar, text=self.t("status_ready"), font=(self.font_family, 9, "bold"), foreground=self.current_accent)
        self.lbl_ready.pack(side=LEFT)

        self.lbl_total_clicks_bottom = tb.Label(status_bar, text=self.t("total_clicks") + "0", font=(self.font_family, 9, "bold"), foreground=self.text_white)
        self.lbl_total_clicks_bottom.pack(side=RIGHT, padx=15)

        self.lbl_timer_bottom = tb.Label(status_bar, text=self.t("run_time") + "00:00:00", font=(self.font_family, 9), foreground=self.text_muted)
        self.lbl_timer_bottom.pack(side=RIGHT)

    def build_auto_tab(self):
        grid_frame = tb.Frame(self.auto_tab)
        grid_frame.pack(fill=BOTH, expand=True)

        col_left = tb.Frame(grid_frame)
        col_left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6))

        col_right = tb.Frame(grid_frame)
        col_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 0))

        # --- ستون چپ: 1. تنظیمات اصلی کلیک ---
        self.frame_config = tb.Labelframe(col_left, text=self.t("frame_config"), padding=12, bootstyle=PRIMARY)
        self.frame_config.pack(fill=X, pady=(0, 10))

        r1 = tb.Frame(self.frame_config)
        r1.pack(fill=X, pady=4)
        self.lbl_btn_mouse = tb.Label(r1, text=self.t("btn_mouse"))
        self.lbl_btn_mouse.pack(side=LEFT, padx=(0, 5))
        self.auto_btn_var = tb.StringVar(value="left")
        tb.Combobox(r1, values=["left", "right", "middle"], textvariable=self.auto_btn_var, state="readonly", width=8).pack(side=LEFT, padx=(0, 15))

        self.lbl_click_type = tb.Label(r1, text=self.t("click_type"))
        self.lbl_click_type.pack(side=LEFT, padx=(0, 5))
        self.auto_type_var = tb.StringVar(value="Single")
        tb.Combobox(r1, values=["Single", "Double"], textvariable=self.auto_type_var, state="readonly", width=8).pack(side=LEFT)

        r2 = tb.Frame(self.frame_config)
        r2.pack(fill=X, pady=6)
        self.lbl_interval = tb.Label(r2, text=self.t("interval_ms"))
        self.lbl_interval.pack(side=LEFT, padx=(0, 5))
        self.auto_interval_var = tb.StringVar(value="100")
        tb.Entry(r2, textvariable=self.auto_interval_var, width=7, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)
        tb.Label(r2, text=" (0.1ms)", font=(self.font_family, 8), foreground=self.text_muted).pack(side=LEFT, padx=5)

        self.auto_jitter_var = tb.BooleanVar(value=False)
        self.chk_jitter = tb.Checkbutton(
            self.frame_config, 
            text=self.t("jitter"), 
            variable=self.auto_jitter_var, 
            bootstyle="success-square-toggle"
        )
        self.chk_jitter.pack(anchor="w", pady=(6, 2))

        self.auto_sound_var = tb.BooleanVar(value=True)
        self.chk_sound = tb.Checkbutton(
            self.frame_config, 
            text=self.t("sound"), 
            variable=self.auto_sound_var, 
            bootstyle="success-square-toggle"
        )
        self.chk_sound.pack(anchor="w", pady=2)

        # --- ستون چپ: 2. مدت زمان کلیک ---
        self.frame_duration = tb.Labelframe(col_left, text=self.t("duration_title"), padding=12, bootstyle=PRIMARY)
        self.frame_duration.pack(fill=X, pady=(0, 10))

        self.auto_duration_mode = tb.StringVar(value="unlimited")
        self.radio_dur1 = tb.Radiobutton(self.frame_duration, text=self.t("unlimited"), variable=self.auto_duration_mode, value="unlimited", bootstyle=PRIMARY)
        self.radio_dur1.pack(anchor="w", pady=2)

        rd2 = tb.Frame(self.frame_duration)
        rd2.pack(fill=X, pady=2)
        self.radio_dur2 = tb.Radiobutton(rd2, text=self.t("auto_stop_after"), variable=self.auto_duration_mode, value="limited", bootstyle=PRIMARY)
        self.radio_dur2.pack(side=LEFT)
        self.auto_duration_val = tb.StringVar(value="10")
        tb.Entry(rd2, textvariable=self.auto_duration_val, width=5, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT, padx=5)
        self.lbl_sec = tb.Label(rd2, text=self.t("seconds"))
        self.lbl_sec.pack(side=LEFT)

        # --- ستون چپ: 3. زمان شروع کلیک ---
        self.frame_start_time = tb.Labelframe(col_left, text=self.t("start_time_title"), padding=12, bootstyle=PRIMARY)
        self.frame_start_time.pack(fill=X, pady=(0, 10))

        self.auto_start_mode = tb.StringVar(value="instant")
        self.radio_time1 = tb.Radiobutton(self.frame_start_time, text=self.t("start_instant"), variable=self.auto_start_mode, value="instant", bootstyle=PRIMARY)
        self.radio_time1.pack(anchor="w", pady=2)

        rt2 = tb.Frame(self.frame_start_time)
        rt2.pack(fill=X, pady=2)
        self.radio_time2 = tb.Radiobutton(rt2, text=self.t("start_scheduled"), variable=self.auto_start_mode, value="scheduled", bootstyle=PRIMARY)
        self.radio_time2.pack(side=LEFT)

        now_plus_1m = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.auto_hour_var = tb.StringVar(value=now_plus_1m.strftime("%H"))
        self.auto_min_var = tb.StringVar(value=now_plus_1m.strftime("%M"))
        self.auto_sec_var = tb.StringVar(value=now_plus_1m.strftime("%S"))

        tb.Entry(rt2, textvariable=self.auto_hour_var, width=3, justify="center", font=(self.font_family, 9, "bold")).pack(side=LEFT)
        tb.Label(rt2, text=":").pack(side=LEFT, padx=1)
        tb.Entry(rt2, textvariable=self.auto_min_var, width=3, justify="center", font=(self.font_family, 9, "bold")).pack(side=LEFT)
        tb.Label(rt2, text=":").pack(side=LEFT, padx=1)
        tb.Entry(rt2, textvariable=self.auto_sec_var, width=3, justify="center", font=(self.font_family, 9, "bold")).pack(side=LEFT)

        # --- ستون چپ: 4. موقعیت کلیک ---
        self.frame_pos = tb.Labelframe(col_left, text=self.t("pos_title"), padding=12, bootstyle=PRIMARY)
        self.frame_pos.pack(fill=X, pady=(0, 10))

        self.auto_pos_mode = tb.StringVar(value="current")
        self.radio_pos1 = tb.Radiobutton(self.frame_pos, text=self.t("pos_current"), variable=self.auto_pos_mode, value="current", bootstyle=PRIMARY)
        self.radio_pos1.pack(anchor="w", pady=2)

        rc = tb.Frame(self.frame_pos)
        rc.pack(fill=X, pady=2)
        self.radio_pos2 = tb.Radiobutton(rc, text=self.t("pos_fixed"), variable=self.auto_pos_mode, value="custom", bootstyle=PRIMARY)
        self.radio_pos2.pack(side=LEFT)

        tb.Label(rc, text="X:").pack(side=LEFT, padx=(6, 2))
        self.auto_x_var = tb.StringVar(value="0")
        tb.Entry(rc, textvariable=self.auto_x_var, width=5, justify="center").pack(side=LEFT, padx=2)

        tb.Label(rc, text="Y:").pack(side=LEFT, padx=(6, 2))
        self.auto_y_var = tb.StringVar(value="0")
        tb.Entry(rc, textvariable=self.auto_y_var, width=5, justify="center").pack(side=LEFT, padx=2)

        self.btn_pick_pos = tb.Button(rc, text=self.t("select_pos"), bootstyle=(INFO, OUTLINE), command=self.pick_auto_custom_pos, width=10)
        self.btn_pick_pos.pack(side=LEFT, padx=6)

        # --- ستون راست: کارت بزرگ، خلوت و برجسته اجرا ---
        self.frame_status = tb.Labelframe(col_right, text=self.t("status_title"), padding=20, bootstyle=SUCCESS)
        self.frame_status.pack(fill=BOTH, expand=True)

        self.lbl_auto_status = tb.Label(self.frame_status, text=self.t("status_stopped"), font=(self.font_family, 15, "bold"), foreground="#FF5555")
        self.lbl_auto_status.pack(pady=10)

        self.lbl_auto_count = tb.Label(self.frame_status, text=self.t("click_count") + "0", font=(self.font_family, 13, "bold"), foreground=self.current_accent)
        self.lbl_auto_count.pack(pady=10)

        self.lbl_hotkey_tip = tb.Label(
            self.frame_status, 
            text=self.t("hotkey_tip").format(key="F6"), 
            font=(self.font_family, 10), 
            foreground="#FFB86C"
        )
        self.lbl_hotkey_tip.pack(pady=10)

        self.btn_auto_toggle = tb.Button(
            self.frame_status, 
            text=self.t("btn_start").format(key="F6"), 
            bootstyle=SUCCESS, 
            command=self.toggle_auto_clicker
        )
        self.btn_auto_toggle.pack(pady=20, fill=X, ipady=15)

    # 👈 تب سوم: «تنظیمات عمومی» (انتقال کادرهای ظاهر و کلید میانبر به این تب)
    def build_general_settings_tab(self):
        grid_frame = tb.Frame(self.help_tab)
        grid_frame.pack(fill=BOTH, expand=True)

        col1 = tb.Frame(grid_frame)
        col1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6))

        col2 = tb.Frame(grid_frame)
        col2.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 0))

        # کادر ۱: تنظیمات ظاهر، زبان و شناورسازی
        self.frame_visuals = tb.Labelframe(col1, text=self.t("frame_visuals"), padding=12, bootstyle=INFO)
        self.frame_visuals.pack(fill=X, pady=(0, 10))

        rv_lang = tb.Frame(self.frame_visuals)
        rv_lang.pack(fill=X, pady=3)
        self.lbl_lang_select = tb.Label(rv_lang, text=self.t("lang_select"))
        self.lbl_lang_select.pack(side=LEFT, padx=(0, 8))
        self.lang_var = tb.StringVar(value="🇮🇷 فارسی (Persian)")
        self.combo_lang = tb.Combobox(
            rv_lang,
            values=["🇮🇷 فارسی (Persian)", "🇬🇧 English"],
            textvariable=self.lang_var,
            state="readonly",
            width=16
        )
        self.combo_lang.pack(side=LEFT)
        self.combo_lang.bind("<<ComboboxSelected>>", self._on_language_changed)

        rv0 = tb.Frame(self.frame_visuals)
        rv0.pack(fill=X, pady=5)
        self.lbl_theme_mode = tb.Label(rv0, text=self.t("theme_mode"))
        self.lbl_theme_mode.pack(side=LEFT, padx=(0, 8))
        self.mode_theme_var = tb.StringVar(value="🌙 تاریک (Dark)")
        self.combo_mode = tb.Combobox(
            rv0, 
            values=["🌙 تاریک (Dark)", "☀️ روشن (Light)"], 
            textvariable=self.mode_theme_var, 
            state="readonly", 
            width=14
        )
        self.combo_mode.pack(side=LEFT)
        self.combo_mode.bind("<<ComboboxSelected>>", self._on_mode_theme_changed)

        rv1 = tb.Frame(self.frame_visuals)
        rv1.pack(fill=X, pady=5)
        self.lbl_accent_color = tb.Label(rv1, text=self.t("accent_color"))
        self.lbl_accent_color.pack(side=LEFT, padx=(0, 8))
        self.accent_theme_var = tb.StringVar(value="🟢 سبز نئونی")
        self.combo_accent = tb.Combobox(
            rv1, 
            values=list(THEME_ACCENTS_FA.keys()), 
            textvariable=self.accent_theme_var, 
            state="readonly", 
            width=14
        )
        self.combo_accent.pack(side=LEFT)
        self.combo_accent.bind("<<ComboboxSelected>>", self._on_accent_changed)

        rv2 = tb.Frame(self.frame_visuals)
        rv2.pack(fill=X, pady=5)
        self.always_on_top_var = tb.BooleanVar(value=False)
        self.chk_topmost = tb.Checkbutton(
            rv2, 
            text=self.t("always_top"), 
            variable=self.always_on_top_var, 
            command=self.toggle_topmost,
            bootstyle="info-square-toggle"
        )
        self.chk_topmost.pack(anchor="w")

        # کادر ۲: انتخاب کلید میانبر
        self.frame_hotkey = tb.Labelframe(col1, text=self.t("hotkey_title"), padding=12, bootstyle=INFO)
        self.frame_hotkey.pack(fill=X, pady=(0, 10))

        rhk = tb.Frame(self.frame_hotkey)
        rhk.pack(fill=X)
        self.lbl_hk = tb.Label(rhk, text=self.t("hotkey_lbl"))
        self.lbl_hk.pack(side=LEFT, padx=(0, 10))
        self.auto_hotkey_var = tb.StringVar(value="F6")
        self.combo_hotkey = tb.Combobox(rhk, values=list(HOTKEY_MAP.keys()), textvariable=self.auto_hotkey_var, state="readonly", width=8)
        self.combo_hotkey.pack(side=LEFT)
        self.combo_hotkey.bind("<<ComboboxSelected>>", self._on_hotkey_changed)

        # کادر ۳: راهنمای سریع و امکانات
        card_q = tb.Labelframe(col2, text=" 🚀 Guide & Features ", padding=12, bootstyle=PRIMARY)
        card_q.pack(fill=BOTH, expand=True)

        self.lbl_help_q_title = tb.Label(card_q, text=self.t("help_quick_title"), font=(self.font_family, 11, "bold"))
        self.lbl_help_q_title.pack(anchor="w", pady=(0, 5))

        self.lbl_help_q1 = tb.Label(card_q, text=self.t("help_quick_1"), font=(self.font_family, 10))
        self.lbl_help_q1.pack(anchor="w", pady=2)

        self.lbl_help_q2 = tb.Label(card_q, text=self.t("help_quick_2"), font=(self.font_family, 10))
        self.lbl_help_q2.pack(anchor="w", pady=2)

        self.lbl_help_q3 = tb.Label(card_q, text=self.t("help_quick_3"), font=(self.font_family, 10))
        self.lbl_help_q3.pack(anchor="w", pady=(2, 10))

        self.lbl_help_f_title = tb.Label(card_q, text=self.t("help_features_title"), font=(self.font_family, 11, "bold"))
        self.lbl_help_f_title.pack(anchor="w", pady=(5, 5))

        self.lbl_help_f1 = tb.Label(card_q, text=self.t("help_feat_1"), font=(self.font_family, 10))
        self.lbl_help_f1.pack(anchor="w", pady=2)

        self.lbl_help_f2 = tb.Label(card_q, text=self.t("help_feat_2"), font=(self.font_family, 10))
        self.lbl_help_f2.pack(anchor="w", pady=2)

        self.lbl_help_f3 = tb.Label(card_q, text=self.t("help_feat_3"), font=(self.font_family, 10))
        self.lbl_help_f3.pack(anchor="w", pady=2)

        self.lbl_help_f4 = tb.Label(card_q, text=self.t("help_feat_4"), font=(self.font_family, 10))
        self.lbl_help_f4.pack(anchor="w", pady=2)

    def _on_hotkey_changed(self, event=None):
        key = self.auto_hotkey_var.get()
        if self.auto_running:
            self.btn_auto_toggle.config(text=self.t("btn_stop").format(key=key))
        else:
            self.btn_auto_toggle.config(text=self.t("btn_start").format(key=key))
        self.lbl_hotkey_tip.config(text=self.t("hotkey_tip").format(key=key))

    def _play_sound_feedback(self, is_start):
        if not self.auto_sound_var.get():
            return
        def _beep():
            try:
                if is_start:
                    winsound.Beep(1000, 80)
                    winsound.Beep(1500, 100)
                else:
                    winsound.Beep(1000, 80)
                    winsound.Beep(600, 120)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()

    def toggle_auto_clicker(self):
        if self.auto_running:
            self.stop_auto_clicker()
        else:
            self.start_auto_clicker()

    def start_auto_clicker(self):
        if self.auto_running: return
        try:
            self.auto_interval_sec = float(self.auto_interval_var.get()) / 1000.0
            if self.auto_pos_mode.get() == "custom":
                int(self.auto_x_var.get()); int(self.auto_y_var.get())
            if self.auto_duration_mode.get() == "limited":
                float(self.auto_duration_val.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return

        key = self.auto_hotkey_var.get()
        self.auto_running = True
        self.btn_auto_toggle.config(text=self.t("btn_stop").format(key=key), bootstyle=DANGER)
        self.lbl_auto_status.config(text=self.t("status_running"), foreground=self.current_accent)

        self._play_sound_feedback(True)
        threading.Thread(target=self._auto_click_loop, daemon=True).start()

    def stop_auto_clicker(self):
        key = self.auto_hotkey_var.get()
        self.auto_running = False
        self.btn_auto_toggle.config(text=self.t("btn_start").format(key=key), bootstyle=SUCCESS)
        self.lbl_auto_status.config(text=self.t("status_stopped"), foreground="#FF5555")

        self._play_sound_feedback(False)

    def _auto_click_loop(self):
        if self.auto_start_mode.get() == "scheduled":
            try:
                h = int(self.auto_hour_var.get())
                m = int(self.auto_min_var.get())
                s = int(self.auto_sec_var.get())
                now = datetime.datetime.now()
                target_time = now.replace(hour=h, minute=m, second=s, microsecond=0)
                if target_time < now:
                    target_time += datetime.timedelta(days=1)
            except ValueError:
                target_time = None

            while self.auto_running and target_time:
                now = datetime.datetime.now()
                if now >= target_time:
                    break
                time_left = str(target_time - now).split(".")[0]
                self.root.after(0, lambda t=time_left: self.lbl_auto_status.config(
                    text=self.t("status_waiting") + f" ({t})", foreground="#FFB86C"
                ))
                time.sleep(0.2)

        if not self.auto_running:
            return

        self.root.after(0, lambda: self.lbl_auto_status.config(text=self.t("status_running"), foreground=self.current_accent))
        btn = self.auto_btn_var.get()
        click_type = self.auto_type_var.get()

        click_start_time = time.time()
        try:
            max_duration = float(self.auto_duration_val.get())
        except ValueError:
            max_duration = 0.0

        loop_counter = 0

        while self.auto_running:
            if self.auto_duration_mode.get() == "limited" and max_duration > 0:
                if (time.time() - click_start_time) >= max_duration:
                    self.root.after(0, self.stop_auto_clicker)
                    break

            pos_x, pos_y = None, None
            if self.auto_pos_mode.get() == "custom":
                pos_x, pos_y = int(self.auto_x_var.get()), int(self.auto_y_var.get())

            win32_fast_click(button=btn, click_type=click_type, x=pos_x, y=pos_y)
            self.auto_click_count += 1
            loop_counter += 1

            if loop_counter % 5 == 0:
                self.root.after(0, self._update_click_ui)

            delay = self.auto_interval_sec
            if self.auto_jitter_var.get():
                jitter = random.uniform(-0.010, 0.010)
                delay = max(0.001, delay + jitter)

            high_precision_sleep(delay)

        self.root.after(0, self._update_click_ui)

    def _update_click_ui(self):
        self.lbl_auto_count.config(text=self.t("click_count") + str(self.auto_click_count))
        self.lbl_total_clicks_bottom.config(text=self.t("total_clicks") + str(self.auto_click_count))

    def pick_auto_custom_pos(self):
        overlay = tb.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.4)
        overlay.config(cursor="crosshair")

        lbl_text = "Select Position & Click\n(Esc = Cancel)" if self.current_lang == "EN" else "موس را روی نقطه ببر و کلیک کن\n(Esc = انصراف)"
        lbl = tb.Label(overlay, text=lbl_text, font=(self.font_family, 22, "bold"), bootstyle=INVERSE)
        lbl.pack(expand=True)

        def on_click(e):
            self.auto_x_var.set(str(e.x_root))
            self.auto_y_var.set(str(e.y_root))
            self.auto_pos_mode.set("custom")
            overlay.destroy()

        overlay.bind("<Button-1>", on_click)
        overlay.bind("<Escape>", lambda e: overlay.destroy())

    def _hotkey_listener(self):
        was_pressed = False
        while True:
            current_key_str = self.auto_hotkey_var.get()
            vk_code = HOTKEY_MAP.get(current_key_str, 0x75)

            state = ctypes.windll.user32.GetAsyncKeyState(vk_code)
            is_pressed = (state & 0x8000) != 0
            if is_pressed and not was_pressed:
                self.root.after(0, self.toggle_auto_clicker)
            was_pressed = is_pressed
            time.sleep(0.05)

    def update_status_bar_loop(self):
        elapsed = int(time.time() - self.start_app_time)
        formatted_time = str(datetime.timedelta(seconds=elapsed))
        self.lbl_timer_bottom.config(text=self.t("run_time") + formatted_time)
        self.root.after(1000, self.update_status_bar_loop)

    def build_sched_tab(self):
        self.frame_sched_cfg = tb.Labelframe(self.sched_tab, text=self.t("sched_cfg_title"), padding=15, bootstyle=INFO)
        self.frame_sched_cfg.pack(fill=X, pady=(0, 15))

        time_row = tb.Frame(self.frame_sched_cfg)
        time_row.pack(fill=X, pady=5)
        self.lbl_sched_time = tb.Label(time_row, text=self.t("sched_time_lbl"), font=(self.font_family, 10))
        self.lbl_sched_time.pack(side=LEFT, padx=(0, 10))

        now_plus_1m = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.hour_var = tb.StringVar(value=now_plus_1m.strftime("%H"))
        self.min_var = tb.StringVar(value=now_plus_1m.strftime("%M"))
        self.sec_var = tb.StringVar(value=now_plus_1m.strftime("%S"))

        tb.Entry(time_row, textvariable=self.hour_var, width=4, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)
        tb.Label(time_row, text=":", font=(self.font_family, 11, "bold")).pack(side=LEFT, padx=2)
        tb.Entry(time_row, textvariable=self.min_var, width=4, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)
        tb.Label(time_row, text=":", font=(self.font_family, 11, "bold")).pack(side=LEFT, padx=2)
        tb.Entry(time_row, textvariable=self.sec_var, width=4, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)

        delay_row = tb.Frame(self.frame_sched_cfg)
        delay_row.pack(fill=X, pady=10)
        self.lbl_sched_delay = tb.Label(delay_row, text=self.t("sched_delay_lbl"), font=(self.font_family, 10))
        self.lbl_sched_delay.pack(side=LEFT, padx=(0, 10))
        self.delay_var = tb.StringVar(value="100")
        tb.Entry(delay_row, textvariable=self.delay_var, width=8, justify="center", font=(self.font_family, 10)).pack(side=LEFT)

        self.frame_sched_pts = tb.Labelframe(self.sched_tab, text=self.t("sched_pts_title"), padding=10, bootstyle=PRIMARY)
        self.frame_sched_pts.pack(fill=BOTH, expand=True)

        ctrl_frame = tb.Frame(self.frame_sched_pts)
        ctrl_frame.pack(fill=X, pady=(0, 10))
        self.btn_sched_add = tb.Button(ctrl_frame, text=self.t("sched_add_btn"), bootstyle=SUCCESS, command=self.add_point_row)
        self.btn_sched_add.pack(side=LEFT, padx=5)
        self.btn_sched_rem = tb.Button(ctrl_frame, text=self.t("sched_rem_btn"), bootstyle=DANGER, command=self.remove_point_row)
        self.btn_sched_rem.pack(side=LEFT, padx=5)

        canvas_frame = tb.Frame(self.frame_sched_pts)
        canvas_frame.pack(fill=BOTH, expand=True)

        self.canvas = tb.Canvas(canvas_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = tb.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tb.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.sched_status_label = tb.Label(self.sched_tab, text=self.t("sched_status_ready"), font=(self.font_family, 12, "bold"), bootstyle=PRIMARY)
        self.sched_status_label.pack(pady=10)

        btn_frame = tb.Frame(self.sched_tab)
        btn_frame.pack(fill=X, pady=5)
        self.sched_start_btn = tb.Button(btn_frame, text=self.t("sched_start_btn"), bootstyle=(SUCCESS, OUTLINE), command=self.start_sched_timer)
        self.sched_start_btn.pack(side=LEFT, expand=True, padx=5, fill=X)
        self.sched_stop_btn = tb.Button(btn_frame, text=self.t("sched_stop_btn"), bootstyle=(DANGER, OUTLINE), command=self.stop_sched_timer, state=DISABLED)
        self.sched_stop_btn.pack(side=LEFT, expand=True, padx=5, fill=X)

    def add_point_row(self):
        idx = len(self.points_data)
        row_frame = tb.Frame(self.scrollable_frame)
        row_frame.pack(fill=X, pady=4, padx=5)

        prefix = self.t("point_prefix")
        lbl_p = tb.Label(row_frame, text=f"{prefix}{idx+1}: X=", font=(self.font_family, 9))
        lbl_p.pack(side=LEFT)

        x_var = tb.StringVar(value="0")
        tb.Entry(row_frame, textvariable=x_var, width=6, justify="center", font=(self.font_family, 9)).pack(side=LEFT, padx=5)

        tb.Label(row_frame, text="Y=", font=(self.font_family, 9)).pack(side=LEFT)
        y_var = tb.StringVar(value="0")
        tb.Entry(row_frame, textvariable=y_var, width=6, justify="center", font=(self.font_family, 9)).pack(side=LEFT, padx=5)

        btn_pick = tb.Button(row_frame, text=self.t("select_pos"), bootstyle=(INFO, OUTLINE), command=lambda i=idx: self.start_mouse_selection(i))
        btn_pick.pack(side=RIGHT, padx=10)

        self.points_data.append({"frame": row_frame, "lbl_p": lbl_p, "x_var": x_var, "y_var": y_var, "btn_pick": btn_pick})

    def remove_point_row(self):
        if len(self.points_data) > 0:
            last = self.points_data.pop()
            last["frame"].destroy()

    def start_mouse_selection(self, index):
        overlay = tb.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.4)
        overlay.config(cursor="crosshair")

        lbl_text = f"Point {index+1}\n(Esc = Cancel)" if self.current_lang == "EN" else f"موس را روی نقطه {index+1} ببر و کلیک کن\n(انصراف = Esc)"
        lbl = tb.Label(overlay, text=lbl_text, font=(self.font_family, 22, "bold"), bootstyle=INVERSE)
        lbl.pack(expand=True)

        def record(e):
            self.points_data[index]["x_var"].set(str(e.x_root))
            self.points_data[index]["y_var"].set(str(e.y_root))
            overlay.destroy()

        overlay.bind("<Button-1>", record)
        overlay.bind("<Escape>", lambda e: overlay.destroy())

    def start_sched_timer(self):
        self.sched_running = True
        self.sched_start_btn.config(state=DISABLED)
        self.sched_stop_btn.config(state=NORMAL)
        threading.Thread(target=self._sched_wait_and_click, daemon=True).start()

    def stop_sched_timer(self):
        self.sched_running = False
        self.sched_start_btn.config(state=NORMAL)
        self.sched_stop_btn.config(state=DISABLED)

    def _sched_wait_and_click(self):
        now = datetime.datetime.now()
        h, m, s = int(self.hour_var.get()), int(self.min_var.get()), int(self.sec_var.get())
        target = now.replace(hour=h, minute=m, second=s, microsecond=0)
        if target < now: target += datetime.timedelta(days=1)

        while self.sched_running:
            if datetime.datetime.now() >= target:
                for p in self.points_data:
                    if not self.sched_running: break
                    win32_fast_click(x=int(p["x_var"].get()), y=int(p["y_var"].get()))
                    time.sleep(float(self.delay_var.get()) / 1000.0)
                break
            time.sleep(0.1)

        self.sched_running = False
        self.root.after(0, lambda: self.sched_start_btn.config(state=NORMAL))


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = AutoClickerProApp(root)
    root.mainloop()