# main.py

import os
import sys
import time
import random
import datetime
import threading
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

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

        # 👈 حل نقد ۵: اضافه کردن State Manager مرکزی
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
        self.auto_click_count = 0
        self.sched_running = False
        self.points_data = []

        self.start_app_time = time.time()
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        build_main_window_layout(self)

        for _ in range(8):
            self.add_point_row()

        # 👈 حل نقد ۲: راه اندازی RegisterHotKey رویدادمحور واقعی
        self.hotkey_mgr = EventHotkeyManager(callback=self.toggle_auto_clicker)
        self.hotkey_mgr.start("F6")

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
        tray_img = self.icon_image_obj if self.icon_image_obj else Image.new('RGB', (64, 64), color=(0, 255, 178))
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
        self.hotkey_mgr.stop()
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)

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

        self.notebook.tab(0, text=self.t("tab_auto"))
        self.notebook.tab(1, text=self.t("tab_sched"))
        self.notebook.tab(2, text=self.t("tab_help"))

        for i, (t_key, d_key) in enumerate([
            ("f1_t", "f1_d"), ("f2_t", "f2_d"), ("f3_t", "f3_d"),
            ("f4_t", "f4_d"), ("f5_t", "f5_d"), ("f6_t", "f6_d")
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

    def _on_accent_changed(self, event=None):
        selected_theme = self.accent_theme_var.get()
        new_color = THEME_ACCENTS_EN.get(selected_theme) or THEME_ACCENTS_FA.get(selected_theme, "#00FFB2")
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

    def start_auto_clicker(self):
        # 👈 حل نقد ۵: بررسی عدم تداخل با بخش زمان‌بندی توسط StateManager
        if not self.state_mgr.is_idle():
            messagebox.showwarning("Warning", "Another process is already running!")
            return

        # 👈 حل نقد ۴: ذخیره و استفاده مستقیم از خروجی‌های اعتبارسنجی
        self.auto_interval_sec = validate_interval(self.auto_interval_var.get()) / 1000.0
        self.validated_x = validate_coordinate(self.auto_x_var.get())
        self.validated_y = validate_coordinate(self.auto_y_var.get())
        self.validated_duration = validate_duration(self.auto_duration_val.get())

        key = self.auto_hotkey_var.get()
        self.auto_running = True
        self.state_mgr.set_state(AppState.AUTO_CLICKING)

        self.btn_auto_toggle.config(text=self.t("btn_stop").format(key=key), bootstyle=DANGER)
        self.lbl_auto_status.config(text=self.t("status_running"), foreground=self.current_accent)

        play_sound_feedback(True, enabled=self.auto_sound_var.get())
        threading.Thread(target=self._auto_click_loop, daemon=True).start()

    def stop_auto_clicker(self):
        key = self.auto_hotkey_var.get()
        self.auto_running = False
        self.state_mgr.set_state(AppState.IDLE)

        self.btn_auto_toggle.config(text=self.t("btn_start").format(key=key), bootstyle=SUCCESS)
        self.lbl_auto_status.config(text=self.t("status_stopped"), foreground="#FF5555")

        play_sound_feedback(False, enabled=self.auto_sound_var.get())

    def _auto_click_loop(self):
        if self.auto_start_mode.get() == "scheduled":
            try:
                h, m, s = int(self.auto_hour_var.get()), int(self.auto_min_var.get()), int(self.auto_sec_var.get())
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
            self.state_mgr.set_state(AppState.IDLE)
            return

        self.root.after(0, lambda: self.lbl_auto_status.config(text=self.t("status_running"), foreground=self.current_accent))
        btn = self.auto_btn_var.get()
        click_type = self.auto_type_var.get()

        click_start_time = time.time()
        max_duration = self.validated_duration
        loop_counter = 0

        while self.auto_running:
            if self.auto_duration_mode.get() == "limited" and max_duration > 0:
                if (time.time() - click_start_time) >= max_duration:
                    self.root.after(0, self.stop_auto_clicker)
                    break

            pos_x, pos_y = None, None
            if self.auto_pos_mode.get() == "custom":
                pos_x, pos_y = self.validated_x, self.validated_y

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
        if not self.state_mgr.is_idle():
            messagebox.showwarning("Warning", "Another clicker process is running!")
            return

        self.sched_running = True
        self.state_mgr.set_state(AppState.SCHEDULER_WAITING)

        self.sched_start_btn.config(state=DISABLED)
        self.sched_stop_btn.config(state=NORMAL)
        threading.Thread(target=self._sched_wait_and_click, daemon=True).start()

    def stop_sched_timer(self):
        self.sched_running = False
        self.state_mgr.set_state(AppState.IDLE)

        self.sched_start_btn.config(state=NORMAL)
        self.sched_stop_btn.config(state=DISABLED)

    def _sched_wait_and_click(self):
        now = datetime.datetime.now()
        h, m, s = int(self.hour_var.get()), int(self.min_var.get()), int(self.sec_var.get())
        target = now.replace(hour=h, minute=m, second=s, microsecond=0)
        if target < now: target += datetime.timedelta(days=1)

        while self.sched_running:
            if datetime.datetime.now() >= target:
                self.state_mgr.set_state(AppState.SCHEDULER_CLICKING)
                for p in self.points_data:
                    if not self.sched_running: break
                    x_val = validate_coordinate(p["x_var"].get())
                    y_val = validate_coordinate(p["y_var"].get())
                    win32_fast_click(x=x_val, y=y_val)
                    time.sleep(validate_interval(self.delay_var.get()) / 1000.0)
                break
            time.sleep(0.1)

        self.sched_running = False
        self.state_mgr.set_state(AppState.IDLE)
        self.root.after(0, lambda: self.sched_start_btn.config(state=NORMAL))


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = AutoClickerProApp(root)
    root.mainloop()