# main.py

import os
import sys
import time
import ctypes
import random
import datetime
import threading
from PIL import Image, ImageTk
import ttkbootstrap as tb
from tkinter import DISABLED, LEFT, NORMAL, RIGHT, X, messagebox

if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

from utils.font_loader import register_vazirmatn_font
from utils.translations import TRANSLATIONS, THEME_ACCENTS_FA, THEME_ACCENTS_EN
from core.click_engine import win32_fast_click, high_precision_sleep
from core.hotkey_manager import EventHotkeyManager
from core.sound_manager import play_sound_feedback
from core.validator import validate_interval, validate_duration, validate_coordinate
from core.state_manager import StateManager, AppState
from ui.main_window import build_main_window_layout

register_vazirmatn_font()

try:
    import pystray
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


class AutoClickerProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker Pro")
        self.root.geometry("1060x840")
        self.root.minsize(960, 680)

        self.state_mgr = StateManager()

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
        self.auto_stop_event = threading.Event()
        self.auto_click_count = 0

        self.sched_running = False
        self.sched_stop_event = threading.Event()
        self.points_data = []
        self.tray_icon = None

        self.start_app_time = time.time()
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        build_main_window_layout(self)

        for _ in range(8):
            self.add_point_row()

        # اجرای کالبک Hotkey در ترد اصلی Tkinter برای Thread-Safety کامل
        self.hotkey_mgr = EventHotkeyManager(
            callback=lambda: self.root.after(0, self.toggle_auto_clicker)
        )
        self.hotkey_mgr.start("F6")

        self.update_status_bar_loop()

    def t(self, key):
        return TRANSLATIONS.get(self.current_lang, {}).get(key, key)

    def setup_vazir_theme(self):
        style = tb.Style()
        for s in [
            ".", "TLabel", "TButton", "TEntry", "TRadiobutton",
            "TCheckbutton", "TCombobox", "TLabelframe.Label", "TLabelframe"
        ]:
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
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for icon_name in ["icon.ico", "icon.png"]:
            icon_path = os.path.join(base_dir, icon_name)
            if os.path.exists(icon_path):
                try:
                    self.icon_image_obj = Image.open(icon_path)
                    if icon_name.endswith(".ico"):
                        self.root.iconbitmap(icon_path)
                    else:
                        img = ImageTk.PhotoImage(self.icon_image_obj)
                        self.root.iconphoto(False, img)
                    break
                except Exception:
                    pass

    def minimize_to_tray(self):
        if not HAS_PYSTRAY:
            self.quit_app()
            return
        if self.tray_icon is not None:
            return

        self.root.withdraw()
        tray_img = (
            self.icon_image_obj
            if self.icon_image_obj
            else Image.new("RGB", (64, 64), color=(0, 255, 178))
        )
        hk_str = self.auto_hotkey_var.get()

        menu = pystray.Menu(
            pystray.MenuItem("Show Auto Clicker Pro", self.restore_from_tray, default=True),
            pystray.MenuItem(
                f"Start / Stop ({hk_str})",
                lambda icon, item: self.root.after(0, self.toggle_auto_clicker),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_app),
        )

        self.tray_icon = pystray.Icon("AutoClickerPro", tray_img, "Auto Clicker Pro", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        tray = self.tray_icon
        self.tray_icon = None
        if tray:
            try:
                tray.stop()
            except Exception:
                pass
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self, icon=None, item=None):
        self.auto_running = False
        self.sched_running = False
        self.auto_stop_event.set()
        self.sched_stop_event.set()
        self.hotkey_mgr.stop()

        tray = self.tray_icon
        self.tray_icon = None
        if tray:
            try:
                tray.stop()
            except Exception:
                pass

        self.root.after(0, self._destroy_root)

    def _destroy_root(self):
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

    def _on_language_changed(self, event=None):
        lang_str = self.lang_var.get()
        self.current_lang = "EN" if "English" in lang_str else "FA"

        accent_names = {
            "#00FFB2": ("🟢 سبز نئونی", "🟢 Neon Green"),
            "#00D2FF": ("🔵 آبی سایبرپانک", "🔵 Cyberpunk Blue"),
            "#C77DFF": ("🟣 بنفش گیمینگ", "🟣 Gaming Purple"),
        }
        fa_acc, en_acc = accent_names.get(
            self.current_accent, ("🟢 سبز نئونی", "🟢 Neon Green")
        )

        if self.current_lang == "EN":
            self.combo_mode.config(values=["🌙 Dark", "☀️ Light"])
            self.combo_accent.config(values=list(THEME_ACCENTS_EN.keys()))
            if "تاریک" in self.mode_theme_var.get():
                self.mode_theme_var.set("🌙 Dark")
            elif "روشن" in self.mode_theme_var.get():
                self.mode_theme_var.set("☀️ Light")
            self.accent_theme_var.set(en_acc)
        else:
            self.combo_mode.config(values=["🌙 تاریک (Dark)", "☀️ روشن (Light)"])
            self.combo_accent.config(values=list(THEME_ACCENTS_FA.keys()))
            if "Dark" in self.mode_theme_var.get():
                self.mode_theme_var.set("🌙 تاریک (Dark)")
            elif "Light" in self.mode_theme_var.get():
                self.mode_theme_var.set("☀️ روشن (Light)")
            self.accent_theme_var.set(fa_acc)

        self.notebook.tab(0, text=self.t("tab_auto"))
        self.notebook.tab(1, text=self.t("tab_sched"))
        self.notebook.tab(2, text=self.t("tab_help"))
        self.lbl_interval_hint.config(text=self.t("interval_hint"))

        for i, (t_key, d_key) in enumerate([
            ("f1_t", "f1_d"), ("f2_t", "f2_d"), ("f3_t", "f3_d"),
            ("f4_t", "f4_d"), ("f5_t", "f5_d"), ("f6_t", "f6_d"),
        ]):
            if i < len(self.feature_card_labels):
                self.feature_card_labels[i][0].config(text=self.t(t_key))
                self.feature_card_labels[i][1].config(text=self.t(d_key))

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

        self.frame_sched_cfg.config(text=self.t("sched_cfg_title"))
        self.lbl_sched_time.config(text=self.t("sched_time_lbl"))
        self.lbl_sched_delay.config(text=self.t("sched_delay_lbl"))
        self.frame_sched_pts.config(text=self.t("sched_pts_title"))
        self.btn_sched_add.config(text=self.t("sched_add_btn"))
        self.btn_sched_rem.config(text=self.t("sched_rem_btn"))
        if not self.sched_running:
            self.sched_status_label.config(text=self.t("sched_status_ready"))
        self.sched_start_btn.config(text=self.t("sched_start_btn"))
        self.sched_stop_btn.config(text=self.t("sched_stop_btn"))

        prefix = self.t("point_prefix")
        btn_txt = self.t("select_pos")
        for idx, p in enumerate(self.points_data):
            p["lbl_p"].config(text=f"{prefix}{idx+1}: X=")
            p["btn_pick"].config(text=btn_txt)

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
        self._on_accent_changed()

    def _on_accent_changed(self, event=None):
        selected_theme = self.accent_theme_var.get()
        new_color = (
            THEME_ACCENTS_EN.get(selected_theme)
            or THEME_ACCENTS_FA.get(selected_theme)
            or self.current_accent
        )
        self.current_accent = new_color

        for lbl in self.accent_labels:
            try:
                lbl.config(foreground=new_color)
            except Exception:
                pass

        style = tb.Style()
        try:
            for s in ["TLabelframe", "Primary.TLabelframe", "Info.TLabelframe", "Success.TLabelframe"]:
                style.configure(s, bordercolor=new_color, lightcolor=new_color, darkcolor=new_color)
                style.configure(f"{s}.Label", foreground=new_color)

            style.configure("Success.TButton", background=new_color, bordercolor=new_color, foreground="#000000")
            style.configure("Info.Outline.TButton", foreground=new_color, bordercolor=new_color)
        except Exception:
            pass

        if not self.auto_running:
            self.lbl_auto_count.config(foreground=new_color)
            self.btn_auto_toggle.config(bootstyle="success")

        self.lbl_ready.config(foreground=new_color)

    def toggle_topmost(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def _on_hotkey_changed(self, event=None):
        key = self.auto_hotkey_var.get()
        self.hotkey_mgr.update_key(key)
        if self.auto_running:
            self.btn_auto_toggle.config(text=self.t("btn_stop").format(key=key))
        else:
            self.btn_auto_toggle.config(text=self.t("btn_start").format(key=key))
        self.lbl_hotkey_tip.config(text=self.t("hotkey_tip").format(key=key))

    def toggle_auto_clicker(self):
        if self.auto_running:
            self.stop_auto_clicker()
        else:
            self.start_auto_clicker()

    def _parse_time_fields(self, h_var, m_var, s_var, ms_var=None):
        h = int(h_var.get())
        m = int(m_var.get())
        s = int(s_var.get())
        ms = int(ms_var.get().strip() or 0) if ms_var is not None else 0
        if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59 and 0 <= ms <= 999):
            raise ValueError("Invalid time range")
        now = datetime.datetime.now()
        target = now.replace(hour=h, minute=m, second=s, microsecond=ms * 1000)
        if target < now:
            target += datetime.timedelta(days=1)
        return target

    def start_auto_clicker(self):
        if not self.state_mgr.is_idle():
            msg = "Another process is already running!" if self.current_lang == "EN" else "یک فرآیند دیگر در حال اجراست!"
            messagebox.showwarning("Warning", msg)
            return

        target_time = None
        if self.auto_start_mode.get() == "scheduled":
            try:
                target_time = self._parse_time_fields(
                    self.auto_hour_var, self.auto_min_var, self.auto_sec_var
                )
            except ValueError:
                msg = (
                    "Please enter a valid start time (HH:MM:SS)."
                    if self.current_lang == "EN"
                    else "لطفاً زمان شروع معتبر (ساعت:دقیقه:ثانیه) وارد کنید."
                )
                messagebox.showwarning("Warning", msg)
                return

        self.auto_interval_sec = validate_interval(self.auto_interval_var.get()) / 1000.0
        self.validated_x = validate_coordinate(self.auto_x_var.get())
        self.validated_y = validate_coordinate(self.auto_y_var.get())
        self.validated_duration = validate_duration(self.auto_duration_val.get())

        key = self.auto_hotkey_var.get()
        self.auto_running = True
        self.auto_stop_event.clear()
        self.state_mgr.set_state(AppState.AUTO_CLICKING)

        self.btn_auto_toggle.config(text=self.t("btn_stop").format(key=key), bootstyle="danger")
        self.lbl_auto_status.config(text=self.t("status_running"), foreground=self.current_accent)

        play_sound_feedback(True, enabled=self.auto_sound_var.get())
        threading.Thread(
            target=self._auto_click_loop,
            args=(target_time,),
            daemon=True,
        ).start()

    def stop_auto_clicker(self):
        if not self.auto_running and self.state_mgr.get_state() != AppState.AUTO_CLICKING:
            return
        key = self.auto_hotkey_var.get()
        self.auto_running = False
        self.auto_stop_event.set()
        self.state_mgr.set_state(AppState.IDLE)

        self.btn_auto_toggle.config(text=self.t("btn_start").format(key=key), bootstyle="success")
        self.lbl_auto_status.config(text=self.t("status_stopped"), foreground="#FF5555")

        play_sound_feedback(False, enabled=self.auto_sound_var.get())

    def _auto_click_loop(self, target_time=None):
        if target_time is not None:
            while self.auto_running and not self.auto_stop_event.is_set():
                now = datetime.datetime.now()
                if now >= target_time:
                    break
                time_left = str(target_time - now).split(".")[0]
                self.root.after(
                    0,
                    lambda t=time_left: self.lbl_auto_status.config(
                        text=self.t("status_waiting") + f" ({t})", foreground="#FFB86C"
                    ),
                )
                if self.auto_stop_event.wait(0.2):
                    break

        if not self.auto_running or self.auto_stop_event.is_set():
            return

        self.root.after(
            0,
            lambda: self.lbl_auto_status.config(
                text=self.t("status_running"), foreground=self.current_accent
            ),
        )

        btn = self.auto_btn_var.get()
        click_type = self.auto_type_var.get()
        limited_duration = self.auto_duration_mode.get() == "limited"
        max_duration = self.validated_duration
        use_custom_pos = self.auto_pos_mode.get() == "custom"
        pos_x, pos_y = (self.validated_x, self.validated_y) if use_custom_pos else (None, None)
        use_jitter = self.auto_jitter_var.get()
        base_delay = self.auto_interval_sec

        click_start_time = time.time()
        last_ui_update = time.perf_counter()

        while self.auto_running and not self.auto_stop_event.is_set():
            if limited_duration and max_duration > 0:
                if (time.time() - click_start_time) >= max_duration:
                    self.root.after(0, self.stop_auto_clicker)
                    break

            win32_fast_click(button=btn, click_type=click_type, x=pos_x, y=pos_y)
            self.auto_click_count += 1

            now_perf = time.perf_counter()
            if (now_perf - last_ui_update) >= 0.05:
                last_ui_update = now_perf
                self.root.after(0, self._update_click_ui)

            delay = base_delay
            if use_jitter:
                delay = max(0.001, delay + random.uniform(-0.010, 0.010))

            high_precision_sleep(delay, stop_event=self.auto_stop_event)

        self.root.after(0, self._update_click_ui)

    def _update_click_ui(self):
        self.lbl_auto_count.config(text=self.t("click_count") + str(self.auto_click_count))
        self.lbl_total_clicks_bottom.config(text=self.t("total_clicks") + str(self.auto_click_count))

    def _open_position_picker(self, base_prompt, on_picked):
        user32 = ctypes.windll.user32
        vx = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        vy = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        vw = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        vh = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN

        if vw <= 0 or vh <= 0:
            vx, vy = 0, 0
            vw = self.root.winfo_screenwidth()
            vh = self.root.winfo_screenheight()

        overlay = tb.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.geometry(f"{vw}x{vh}+{vx}+{vy}")
        overlay.attributes("-alpha", 0.35)
        overlay.attributes("-topmost", True)
        overlay.config(cursor="crosshair")

        cx = (self.root.winfo_rootx() + self.root.winfo_width() // 2) - vx
        cy = (self.root.winfo_rooty() + self.root.winfo_height() // 2) - vy
        cx = max(180, min(vw - 180, cx))
        cy = max(80, min(vh - 80, cy))

        lbl = tb.Label(
            overlay,
            text=base_prompt,
            font=(self.font_family, 20, "bold"),
            bootstyle="inverse",
            justify="center",
            padding=16,
        )
        lbl.place(x=cx, y=cy, anchor="center")

        def cancel(e=None):
            try:
                overlay.grab_release()
            except Exception:
                pass
            if overlay.winfo_exists():
                overlay.destroy()

        def on_motion(e):
            lbl.config(text=f"{base_prompt}\nX: {e.x_root}  |  Y: {e.y_root}")

        def on_click(e):
            x, y = e.x_root, e.y_root
            cancel()
            on_picked(x, y)

        overlay.bind("<Motion>", on_motion)
        lbl.bind("<Motion>", on_motion)
        overlay.bind("<Button-1>", on_click)
        lbl.bind("<Button-1>", on_click)
        overlay.bind("<Escape>", cancel)
        overlay.bind("<Button-3>", cancel)
        lbl.bind("<Button-3>", cancel)

        overlay.update_idletasks()
        overlay.lift()
        overlay.focus_force()
        overlay.grab_set()

    def pick_auto_custom_pos(self):
        prompt = (
            "Move mouse & Left-Click to select\n(Esc or Right-Click = Cancel)"
            if self.current_lang == "EN"
            else "موس را روی نقطه ببر و کلیک چپ کن\n(Esc یا کلیک راست = انصراف)"
        )

        def on_picked(x, y):
            self.auto_x_var.set(str(x))
            self.auto_y_var.set(str(y))
            self.auto_pos_mode.set("custom")

        self._open_position_picker(prompt, on_picked)

    def update_status_bar_loop(self):
        elapsed = int(time.time() - self.start_app_time)
        formatted_time = str(datetime.timedelta(seconds=elapsed))
        self.lbl_timer_bottom.config(text=self.t("run_time") + formatted_time)
        self.root.after(1000, self.update_status_bar_loop)

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

        btn_pick = tb.Button(
            row_frame,
            text=self.t("select_pos"),
            bootstyle=("info", "outline"),
            command=lambda i=idx: self.start_mouse_selection(i),
        )
        btn_pick.pack(side=RIGHT, padx=10)

        self.points_data.append({
            "frame": row_frame,
            "lbl_p": lbl_p,
            "x_var": x_var,
            "y_var": y_var,
            "btn_pick": btn_pick,
        })

    def remove_point_row(self):
        if len(self.points_data) > 0:
            last = self.points_data.pop()
            last["frame"].destroy()

    def start_mouse_selection(self, index):
        prompt = (
            f"Point {index+1}: Left-Click to select\n(Esc or Right-Click = Cancel)"
            if self.current_lang == "EN"
            else f"موس را روی نقطه {index+1} ببر و کلیک چپ کن\n(Esc یا کلیک راست = انصراف)"
        )

        def on_picked(x, y):
            if index < len(self.points_data):
                self.points_data[index]["x_var"].set(str(x))
                self.points_data[index]["y_var"].set(str(y))

        self._open_position_picker(prompt, on_picked)

    def start_sched_timer(self):
        if not self.state_mgr.is_idle():
            msg = "Another clicker process is running!" if self.current_lang == "EN" else "یک فرآیند دیگر در حال اجراست!"
            messagebox.showwarning("Warning", msg)
            return

        if not self.points_data:
            msg = "Please add at least one point!" if self.current_lang == "EN" else "لطفاً حداقل یک نقطه اضافه کنید!"
            messagebox.showwarning("Warning", msg)
            return

        try:
            target = self._parse_time_fields(
                self.hour_var, self.min_var, self.sec_var, self.ms_var
            )
        except ValueError:
            msg = (
                "Please enter a valid start time (HH:MM:SS.ms, ms: 0-999)."
                if self.current_lang == "EN"
                else "لطفاً زمان شروع معتبر (ساعت:دقیقه:ثانیه و میلی‌ثانیه ۰ تا ۹۹۹) وارد کنید."
            )
            messagebox.showwarning("Warning", msg)
            return

        points_snapshot = [
            (
                validate_coordinate(p["x_var"].get()),
                validate_coordinate(p["y_var"].get()),
            )
            for p in self.points_data
        ]
        delay_sec = validate_interval(self.delay_var.get()) / 1000.0

        self.sched_running = True
        self.sched_stop_event.clear()
        self.state_mgr.set_state(AppState.SCHEDULER_WAITING)

        self.sched_start_btn.config(state=DISABLED)
        self.sched_stop_btn.config(state=NORMAL)
        play_sound_feedback(True, enabled=self.auto_sound_var.get())

        threading.Thread(
            target=self._sched_wait_and_click,
            args=(target, points_snapshot, delay_sec),
            daemon=True,
        ).start()

    def stop_sched_timer(self):
        if not self.sched_running:
            return
        self.sched_running = False
        self.sched_stop_event.set()
        self.state_mgr.set_state(AppState.IDLE)

        self.sched_start_btn.config(state=NORMAL)
        self.sched_stop_btn.config(state=DISABLED)
        self.sched_status_label.config(text=self.t("status_stopped"), foreground="#FF5555")
        play_sound_feedback(False, enabled=self.auto_sound_var.get())

    def _sched_wait_and_click(self, target, points_snapshot, delay_sec):
        while self.sched_running and not self.sched_stop_event.is_set():
            now = datetime.datetime.now()
            remaining = (target - now).total_seconds()
            if remaining <= 0:
                break

            if remaining <= 0.25:
                if remaining > 0.025:
                    if self.sched_stop_event.wait(remaining - 0.020):
                        break
                while self.sched_running and not self.sched_stop_event.is_set():
                    if datetime.datetime.now() >= target:
                        break
                break

            time_left = str(target - now).split(".")[0]
            self.root.after(
                0,
                lambda t=time_left: self.sched_status_label.config(
                    text=self.t("status_waiting") + f" ({t})", foreground="#FFB86C"
                ),
            )
            wait_step = min(0.2, remaining - 0.15)
            if wait_step > 0 and self.sched_stop_event.wait(wait_step):
                break

        if self.sched_running and not self.sched_stop_event.is_set():
            self.state_mgr.set_state(AppState.SCHEDULER_CLICKING)
            if delay_sec >= 0.05:
                self.root.after(
                    0,
                    lambda: self.sched_status_label.config(
                        text=self.t("status_running"), foreground=self.current_accent
                    ),
                )
            for idx, (x_val, y_val) in enumerate(points_snapshot):
                if not self.sched_running or self.sched_stop_event.is_set():
                    break
                win32_fast_click(x=x_val, y=y_val)
                self.auto_click_count += 1
                if delay_sec >= 0.05:
                    self.root.after(0, self._update_click_ui)
                if idx < len(points_snapshot) - 1:
                    high_precision_sleep(delay_sec, stop_event=self.sched_stop_event)

            self.root.after(0, self._update_click_ui)

        was_cancelled = self.sched_stop_event.is_set()
        self.sched_running = False
        self.state_mgr.set_state(AppState.IDLE)
        self.root.after(0, lambda: self._finish_sched_ui(was_cancelled))

    def _finish_sched_ui(self, was_cancelled):
        self.sched_start_btn.config(state=NORMAL)
        self.sched_stop_btn.config(state=DISABLED)
        if not was_cancelled:
            self.sched_status_label.config(
                text=self.t("sched_status_ready"), foreground=self.current_accent
            )
            play_sound_feedback(False, enabled=self.auto_sound_var.get())


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = AutoClickerProApp(root)
    root.mainloop()