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

# پلت‌های رنگی نئونی (ویژگی تغییر تم)
THEME_ACCENTS = {
    "🟢 سبز نئونی": "#00FFB2",
    "🔵 آبی سایبرپانک": "#00D2FF",
    "🟣 بنفش گیمینگ": "#C77DFF"
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
        self.root.geometry("1060x820")
        self.root.minsize(960, 680)
        self.root.configure(bg=BG_DARK)

        self.font_family = "Vazirmatn"
        self.setup_vazir_theme()

        self.load_app_icon()

        # رنگ هایلایت پیش‌فرض
        self.current_accent = "#00FFB2"
        self.accent_labels = []

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
            pystray.MenuItem("نمایش Auto Clicker Pro", self.restore_from_tray, default=True),
            pystray.MenuItem(f"توقف / شروع ({hk_str})", lambda icon, item: self.root.after(0, self.toggle_auto_clicker)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("خروج کامل", self.quit_app)
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

    # 👈 تغییر زنده تم نئونی (ویژگی تغییر تم)
    def _on_accent_changed(self, event=None):
        selected_theme = self.accent_theme_var.get()
        new_color = THEME_ACCENTS.get(selected_theme, "#00FFB2")
        self.current_accent = new_color

        for lbl in self.accent_labels:
            try:
                lbl.config(foreground=new_color)
            except Exception:
                pass

        if not self.auto_running:
            self.lbl_auto_count.config(foreground=new_color)
        self.lbl_ready.config(foreground=new_color)

    # 👈 سوئیچ سنجاق کردن پنجره (ویژگی همیشه بالا)
    def toggle_topmost(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def build_main_layout(self):
        main_container = tb.Frame(self.root, bootstyle="dark")
        main_container.pack(fill=BOTH, expand=True, padx=12, pady=12)

        # 1. پنل سمت چپ
        left_panel = tb.Frame(main_container, width=280, padding=15)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 12))

        tb.Label(left_panel, text="AUTO ⚡", font=(self.font_family, 26, "bold"), foreground=TEXT_WHITE).pack(anchor="w")
        lbl_brand_accent = tb.Label(left_panel, text="CLICKER PRO", font=(self.font_family, 22, "bold"), foreground=self.current_accent)
        lbl_brand_accent.pack(anchor="w")
        self.accent_labels.append(lbl_brand_accent)

        tb.Label(left_panel, text="سبک، سریع و فوق‌العاده دقیق", font=(self.font_family, 9), foreground=TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        features = [
            ("📌 پنجره شناور (Always On Top)", "نگه‌داشتن پنجره روی بقیه بازی‌ها"),
            ("🎨 تغییر تم نئونی زنده", "امکان انتخاب رنگ سبز، آبی و بنفش"),
            ("⚡ موتور کلیک Win32", "سرعت مایکروثانیه‌ای (۱۰۰۰+ کلیک)"),
            ("⏱️ توقف خودکار زمان‌بندی", "محدود کردن کلیک به ۱۰ ثانیه"),
            ("⏰ زمان‌بندی کلیک پیوسته", "امکان شروع رأس ساعت مشخص"),
            ("⌨️ کلید میانبر سفارشی", "انتخاب دلخواه کلید شروع/توقف")
        ]

        for title, desc in features:
            card = tb.Frame(left_panel, padding=10)
            card.pack(fill=X, pady=5)
            lbl_f_title = tb.Label(card, text=title, font=(self.font_family, 10, "bold"), foreground=self.current_accent)
            lbl_f_title.pack(anchor="w")
            self.accent_labels.append(lbl_f_title)

            tb.Label(card, text=desc, font=(self.font_family, 8), foreground=TEXT_MUTED).pack(anchor="w")

        # 2. پنل سمت راست
        right_panel = tb.Frame(main_container)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)

        self.notebook = tb.Notebook(right_panel, bootstyle=PRIMARY)
        self.notebook.pack(fill=BOTH, expand=True)

        self.auto_tab = tb.Frame(self.notebook, padding=12)
        self.sched_tab = tb.Frame(self.notebook, padding=12)
        self.help_tab = tb.Frame(self.notebook, padding=12)

        self.notebook.add(self.auto_tab, text=" ⚙️ تنظیمات عمومی ")
        self.notebook.add(self.sched_tab, text=" 🎯 زمان‌بندی نقاط ")
        self.notebook.add(self.help_tab, text=" ℹ️ درباره و راهنما ")

        self.build_auto_tab()
        self.build_sched_tab()
        self.build_help_tab()

        status_bar = tb.Frame(right_panel, padding=(12, 6))
        status_bar.pack(fill=X, side=BOTTOM, pady=(8, 0))

        self.lbl_ready = tb.Label(status_bar, text="🟢 سیستم آماده به کار است", font=(self.font_family, 9, "bold"), foreground=self.current_accent)
        self.lbl_ready.pack(side=LEFT)

        self.lbl_total_clicks_bottom = tb.Label(status_bar, text="مجموع کلیک‌ها: 0", font=(self.font_family, 9, "bold"), foreground=TEXT_WHITE)
        self.lbl_total_clicks_bottom.pack(side=RIGHT, padx=15)

        self.lbl_timer_bottom = tb.Label(status_bar, text="⏱️ زمان اجرا: 00:00:00", font=(self.font_family, 9), foreground=TEXT_MUTED)
        self.lbl_timer_bottom.pack(side=RIGHT)

    def build_auto_tab(self):
        grid_frame = tb.Frame(self.auto_tab)
        grid_frame.pack(fill=BOTH, expand=True)

        col_left = tb.Frame(grid_frame)
        col_left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6))

        col_right = tb.Frame(grid_frame)
        col_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 0))

        # --- ستون چپ: 1. تنظیمات اصلی کلیک ---
        frame_config = tb.Labelframe(col_left, text=" ⚙️ تنظیمات دکمه و سرعت ", padding=12, bootstyle=PRIMARY)
        frame_config.pack(fill=X, pady=(0, 10))

        r1 = tb.Frame(frame_config)
        r1.pack(fill=X, pady=4)
        tb.Label(r1, text="دکمه موس:").pack(side=LEFT, padx=(0, 5))
        self.auto_btn_var = tb.StringVar(value="left")
        tb.Combobox(r1, values=["left", "right", "middle"], textvariable=self.auto_btn_var, state="readonly", width=8).pack(side=LEFT, padx=(0, 15))

        tb.Label(r1, text="نوع کلیک:").pack(side=LEFT, padx=(0, 5))
        self.auto_type_var = tb.StringVar(value="Single")
        tb.Combobox(r1, values=["Single", "Double"], textvariable=self.auto_type_var, state="readonly", width=8).pack(side=LEFT)

        r2 = tb.Frame(frame_config)
        r2.pack(fill=X, pady=6)
        tb.Label(r2, text="فاصله زمانی (میلی‌ثانیه):").pack(side=LEFT, padx=(0, 5))
        self.auto_interval_var = tb.StringVar(value="100")
        tb.Entry(r2, textvariable=self.auto_interval_var, width=7, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)
        tb.Label(r2, text=" (0.1ms = سرعت مایکروثانیه‌ای)", font=(self.font_family, 8), foreground=TEXT_MUTED).pack(side=LEFT, padx=5)

        self.auto_jitter_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            frame_config, 
            text="🎲 رندوم‌سازی کلیک (ضد شناسایی ±10ms)", 
            variable=self.auto_jitter_var, 
            bootstyle="success-square-toggle"
        ).pack(anchor="w", pady=(6, 2))

        self.auto_sound_var = tb.BooleanVar(value=True)
        tb.Checkbutton(
            frame_config, 
            text="🔊 پخش صدای هشدار هنگام شروع/توقف", 
            variable=self.auto_sound_var, 
            bootstyle="success-square-toggle"
        ).pack(anchor="w", pady=2)

        # 👈 2. کادر شخصی‌سازی ظاهری (تم نئونی + همیشه بالا)
        frame_visuals = tb.Labelframe(col_left, text=" 🎨 ظاهر و شناور‌سازی ", padding=12, bootstyle=INFO)
        frame_visuals.pack(fill=X, pady=(0, 10))

        rv1 = tb.Frame(frame_visuals)
        rv1.pack(fill=X, pady=2)
        tb.Label(rv1, text="رنگ تم نئونی:").pack(side=LEFT, padx=(0, 8))
        self.accent_theme_var = tb.StringVar(value="🟢 سبز نئونی")
        self.combo_accent = tb.Combobox(
            rv1, 
            values=list(THEME_ACCENTS.keys()), 
            textvariable=self.accent_theme_var, 
            state="readonly", 
            width=14
        )
        self.combo_accent.pack(side=LEFT)
        self.combo_accent.bind("<<ComboboxSelected>>", self._on_accent_changed)

        rv2 = tb.Frame(frame_visuals)
        rv2.pack(fill=X, pady=6)
        self.always_on_top_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            rv2, 
            text="📌 پنجره همیشه بالا باشد (Always On Top)", 
            variable=self.always_on_top_var, 
            command=self.toggle_topmost,
            bootstyle="info-square-toggle"
        ).pack(anchor="w")

        # --- ستون چپ: 3. مدت زمان کلیک ---
        frame_duration = tb.Labelframe(col_left, text=" ⏱️ مدت زمان کلیک (توقف خودکار) ", padding=12, bootstyle=PRIMARY)
        frame_duration.pack(fill=X, pady=(0, 10))

        self.auto_duration_mode = tb.StringVar(value="unlimited")
        tb.Radiobutton(frame_duration, text="♾️ کلیک نامحدود (توقف دستی)", variable=self.auto_duration_mode, value="unlimited", bootstyle=PRIMARY).pack(anchor="w", pady=2)

        rd2 = tb.Frame(frame_duration)
        rd2.pack(fill=X, pady=2)
        tb.Radiobutton(rd2, text="⏱️ توقف خودکار پس از: ", variable=self.auto_duration_mode, value="limited", bootstyle=PRIMARY).pack(side=LEFT)
        self.auto_duration_val = tb.StringVar(value="10")
        tb.Entry(rd2, textvariable=self.auto_duration_val, width=5, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT, padx=5)
        tb.Label(rd2, text="ثانیه").pack(side=LEFT)

        # --- ستون راست: 1. زمان شروع کلیک ---
        frame_start_time = tb.Labelframe(col_right, text=" ⏰ زمان شروع کلیک ", padding=12, bootstyle=PRIMARY)
        frame_start_time.pack(fill=X, pady=(0, 10))

        self.auto_start_mode = tb.StringVar(value="instant")
        tb.Radiobutton(frame_start_time, text="⚡ شروع فوری (مستقیم با زدن کلید یا دکمه)", variable=self.auto_start_mode, value="instant", bootstyle=PRIMARY).pack(anchor="w", pady=2)

        rt2 = tb.Frame(frame_start_time)
        rt2.pack(fill=X, pady=2)
        tb.Radiobutton(rt2, text="⏰ شروع در ساعت مشخص: ", variable=self.auto_start_mode, value="scheduled", bootstyle=PRIMARY).pack(side=LEFT)

        now_plus_1m = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.auto_hour_var = tb.StringVar(value=now_plus_1m.strftime("%H"))
        self.auto_min_var = tb.StringVar(value=now_plus_1m.strftime("%M"))
        self.auto_sec_var = tb.StringVar(value=now_plus_1m.strftime("%S"))

        tb.Entry(rt2, textvariable=self.auto_hour_var, width=3, justify="center", font=(self.font_family, 9, "bold")).pack(side=LEFT)
        tb.Label(rt2, text=":").pack(side=LEFT, padx=1)
        tb.Entry(rt2, textvariable=self.auto_min_var, width=3, justify="center", font=(self.font_family, 9, "bold")).pack(side=LEFT)
        tb.Label(rt2, text=":").pack(side=LEFT, padx=1)
        tb.Entry(rt2, textvariable=self.auto_sec_var, width=3, justify="center", font=(self.font_family, 9, "bold")).pack(side=LEFT)

        # --- ستون راست: 2. کلید میانبر ---
        frame_hotkey = tb.Labelframe(col_right, text=" ⌨️ انتخاب کلید میانبر ", padding=12, bootstyle=INFO)
        frame_hotkey.pack(fill=X, pady=(0, 10))

        rhk = tb.Frame(frame_hotkey)
        rhk.pack(fill=X)
        tb.Label(rhk, text="کلید شروع/توقف:").pack(side=LEFT, padx=(0, 10))
        self.auto_hotkey_var = tb.StringVar(value="F6")
        self.combo_hotkey = tb.Combobox(rhk, values=list(HOTKEY_MAP.keys()), textvariable=self.auto_hotkey_var, state="readonly", width=8)
        self.combo_hotkey.pack(side=LEFT)
        self.combo_hotkey.bind("<<ComboboxSelected>>", self._on_hotkey_changed)

        # --- ستون راست: 3. موقعیت کلیک ---
        frame_pos = tb.Labelframe(col_right, text=" 📍 موقعیت کلیک موس ", padding=12, bootstyle=PRIMARY)
        frame_pos.pack(fill=X, pady=(0, 10))

        self.auto_pos_mode = tb.StringVar(value="current")
        tb.Radiobutton(frame_pos, text="موقعیت فعلی نشانگر موس", variable=self.auto_pos_mode, value="current", bootstyle=PRIMARY).pack(anchor="w", pady=2)

        rc = tb.Frame(frame_pos)
        rc.pack(fill=X, pady=2)
        tb.Radiobutton(rc, text="مختصات ثابت", variable=self.auto_pos_mode, value="custom", bootstyle=PRIMARY).pack(side=LEFT)

        tb.Label(rc, text="X:").pack(side=LEFT, padx=(10, 2))
        self.auto_x_var = tb.StringVar(value="0")
        tb.Entry(rc, textvariable=self.auto_x_var, width=5, justify="center").pack(side=LEFT, padx=2)

        tb.Label(rc, text="Y:").pack(side=LEFT, padx=(6, 2))
        self.auto_y_var = tb.StringVar(value="0")
        tb.Entry(rc, textvariable=self.auto_y_var, width=5, justify="center").pack(side=LEFT, padx=2)

        tb.Button(rc, text="🎯 انتخاب", bootstyle=(INFO, OUTLINE), command=self.pick_auto_custom_pos).pack(side=LEFT, padx=10)

        # --- ستون راست: 4. کارت بزرگ اجرا و وضعیت نئونی ---
        frame_status = tb.Labelframe(col_right, text=" 📊 وضعیت و اجرای سریع ", padding=15, bootstyle=SUCCESS)
        frame_status.pack(fill=BOTH, expand=True)

        self.lbl_auto_status = tb.Label(frame_status, text="🔴 وضعیت: متوقف شده", font=(self.font_family, 14, "bold"), foreground="#FF5555")
        self.lbl_auto_status.pack(pady=5)

        self.lbl_auto_count = tb.Label(frame_status, text="تعداد کلیک‌ها: 0", font=(self.font_family, 12, "bold"), foreground=self.current_accent)
        self.lbl_auto_count.pack(pady=5)

        self.lbl_hotkey_tip = tb.Label(
            frame_status, 
            text="💡 برای شروع یا توقف کلیک دکمه F6 را بزنید.", 
            font=(self.font_family, 9), 
            foreground="#FFB86C"
        )
        self.lbl_hotkey_tip.pack(pady=5)

        self.btn_auto_toggle = tb.Button(
            frame_status, 
            text="▶ (F6) شروع کلیک پیوسته", 
            bootstyle=SUCCESS, 
            command=self.toggle_auto_clicker
        )
        self.btn_auto_toggle.pack(pady=10, fill=X, ipady=12)

    def _on_hotkey_changed(self, event=None):
        key = self.auto_hotkey_var.get()
        if self.auto_running:
            self.btn_auto_toggle.config(text=f"⏹ ({key}) توقف کلیک")
        else:
            self.btn_auto_toggle.config(text=f"▶ ({key}) شروع کلیک پیوسته")
        self.lbl_hotkey_tip.config(text=f"💡 برای شروع یا توقف کلیک دکمه {key} را بزنید.")

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
            messagebox.showerror("خطا", "لطفاً مقادیر ورودی را به عدد وارد کنید.")
            return

        key = self.auto_hotkey_var.get()
        self.auto_running = True
        self.btn_auto_toggle.config(text=f"⏹ ({key}) توقف کلیک", bootstyle=DANGER)
        self.lbl_auto_status.config(text="🟢 وضعیت: در حال اجرا...", foreground=self.current_accent)

        self._play_sound_feedback(True)
        threading.Thread(target=self._auto_click_loop, daemon=True).start()

    def stop_auto_clicker(self):
        key = self.auto_hotkey_var.get()
        self.auto_running = False
        self.btn_auto_toggle.config(text=f"▶ ({key}) شروع کلیک پیوسته", bootstyle=SUCCESS)
        self.lbl_auto_status.config(text="🔴 وضعیت: متوقف شده", foreground="#FF5555")

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
                    text=f"⏳ منتظر زمان شروع... ({t})", foreground="#FFB86C"
                ))
                time.sleep(0.2)

        if not self.auto_running:
            return

        self.root.after(0, lambda: self.lbl_auto_status.config(text="🟢 وضعیت: در حال کلیک...", foreground=self.current_accent))
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
        self.lbl_auto_count.config(text=f"تعداد کلیک‌ها: {self.auto_click_count}")
        self.lbl_total_clicks_bottom.config(text=f"مجموع کلیک‌ها: {self.auto_click_count}")

    def pick_auto_custom_pos(self):
        overlay = tb.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.4)
        overlay.config(cursor="crosshair")

        lbl = tb.Label(overlay, text="موس را روی نقطه مورد نظر برده و کلیک کنید\n(انصراف = Esc)", font=(self.font_family, 22, "bold"), bootstyle=INVERSE)
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
        self.lbl_timer_bottom.config(text=f"⏱️ زمان اجرا: {formatted_time}")
        self.root.after(1000, self.update_status_bar_loop)

    # ==========================================
    # تب زمان‌بندی نقاط
    # ==========================================
    def build_sched_tab(self):
        settings_frame = tb.Labelframe(self.sched_tab, text=" ⚙️ تنظیمات زمان و سرعت ", padding=15, bootstyle=INFO)
        settings_frame.pack(fill=X, pady=(0, 15))

        time_row = tb.Frame(settings_frame)
        time_row.pack(fill=X, pady=5)
        tb.Label(time_row, text="زمان شروع (ساعت:دقیقه:ثانیه):", font=(self.font_family, 10)).pack(side=LEFT, padx=(0, 10))

        now_plus_1m = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.hour_var = tb.StringVar(value=now_plus_1m.strftime("%H"))
        self.min_var = tb.StringVar(value=now_plus_1m.strftime("%M"))
        self.sec_var = tb.StringVar(value=now_plus_1m.strftime("%S"))

        tb.Entry(time_row, textvariable=self.hour_var, width=4, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)
        tb.Label(time_row, text=":", font=(self.font_family, 11, "bold")).pack(side=LEFT, padx=2)
        tb.Entry(time_row, textvariable=self.min_var, width=4, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)
        tb.Label(time_row, text=":", font=(self.font_family, 11, "bold")).pack(side=LEFT, padx=2)
        tb.Entry(time_row, textvariable=self.sec_var, width=4, justify="center", font=(self.font_family, 10, "bold")).pack(side=LEFT)

        delay_row = tb.Frame(settings_frame)
        delay_row.pack(fill=X, pady=10)
        tb.Label(delay_row, text="تاخیر بین کلیک‌ها (میلی‌ثانیه):", font=(self.font_family, 10)).pack(side=LEFT, padx=(0, 10))
        self.delay_var = tb.StringVar(value="100")
        tb.Entry(delay_row, textvariable=self.delay_var, width=8, justify="center", font=(self.font_family, 10)).pack(side=LEFT)

        points_container = tb.Labelframe(self.sched_tab, text=" 🎯 مختصات نقاط کلیک ", padding=10, bootstyle=PRIMARY)
        points_container.pack(fill=BOTH, expand=True)

        ctrl_frame = tb.Frame(points_container)
        ctrl_frame.pack(fill=X, pady=(0, 10))
        tb.Button(ctrl_frame, text="➕ افزودن نقطه", bootstyle=SUCCESS, command=self.add_point_row).pack(side=LEFT, padx=5)
        tb.Button(ctrl_frame, text="➖ حذف نقطه", bootstyle=DANGER, command=self.remove_point_row).pack(side=LEFT, padx=5)

        canvas_frame = tb.Frame(points_container)
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

        self.sched_status_label = tb.Label(self.sched_tab, text="وضعیت: آماده به کار", font=(self.font_family, 12, "bold"), bootstyle=PRIMARY)
        self.sched_status_label.pack(pady=10)

        btn_frame = tb.Frame(self.sched_tab)
        btn_frame.pack(fill=X, pady=5)
        self.sched_start_btn = tb.Button(btn_frame, text="▶ شروع زمان‌بندی", bootstyle=(SUCCESS, OUTLINE), command=self.start_sched_timer)
        self.sched_start_btn.pack(side=LEFT, expand=True, padx=5, fill=X)
        self.sched_stop_btn = tb.Button(btn_frame, text="⏹ توقف", bootstyle=(DANGER, OUTLINE), command=self.stop_sched_timer, state=DISABLED)
        self.sched_stop_btn.pack(side=LEFT, expand=True, padx=5, fill=X)

    def add_point_row(self):
        idx = len(self.points_data)
        row_frame = tb.Frame(self.scrollable_frame)
        row_frame.pack(fill=X, pady=4, padx=5)

        tb.Label(row_frame, text=f"نقطه {idx+1}: X=", font=(self.font_family, 9)).pack(side=LEFT)
        x_var = tb.StringVar(value="0")
        tb.Entry(row_frame, textvariable=x_var, width=6, justify="center", font=(self.font_family, 9)).pack(side=LEFT, padx=5)

        tb.Label(row_frame, text="Y=", font=(self.font_family, 9)).pack(side=LEFT)
        y_var = tb.StringVar(value="0")
        tb.Entry(row_frame, textvariable=y_var, width=6, justify="center", font=(self.font_family, 9)).pack(side=LEFT, padx=5)

        tb.Button(row_frame, text="🎯 انتخاب", bootstyle=(INFO, OUTLINE), command=lambda i=idx: self.start_mouse_selection(i)).pack(side=RIGHT, padx=10)
        self.points_data.append({"frame": row_frame, "x_var": x_var, "y_var": y_var})

    def remove_point_row(self):
        if len(self.points_data) > 0:
            last = self.points_data.pop()
            last["frame"].destroy()

    def start_mouse_selection(self, index):
        overlay = tb.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.4)
        overlay.config(cursor="crosshair")

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

    def build_help_tab(self):
        help_text = """🎉 به Auto Clicker Pro خوش آمدید!

⚡ امکانات جدید این نسخه:
• پنجره دائماً شناور (Always On Top) جهت مشاهده وضعیت بدون Alt+Tab
• تغییر زنده تم نئونی بین رنگ‌های سبز نئونی، آبی سایبرپانک و بنفش گیمینگ
• چیدمان ۲ ستونه مدرن با فونت بومی وزیرمتن (Vazirmatn)
• موتور کلیک مستقیم لایه پایین ویندوز (Win32 SendInput) با سرعت فوق‌العاده بالا
• امکان تعیین زمان‌بندی توقف خودکار (مثلاً توقف کلیک بعد از ۱۰ ثانیه)
• امکان شروع کلیک پیوسته رأس ساعت مشخص (ساعت:دقیقه:ثانیه)
• کلید میانبر سفارشی و سراسری در کل ویندوز (F1 تا F12، Insert و ...)
• سیستم بازخورد صوتی (Audio Feedback) و مینی‌مایز به سینی ویندوز (System Tray)
        """
        tb.Label(self.help_tab, text=help_text, justify=RIGHT, font=(self.font_family, 10), wraplength=520).pack(padx=15, pady=15, anchor="ne")


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = AutoClickerProApp(root)
    root.mainloop()