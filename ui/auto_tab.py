# ui/auto_tab.py

import time
import random
import datetime
import threading
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from core.click_engine import win32_fast_click, high_precision_sleep
from core.sound_manager import play_sound_feedback
from core.validator import validate_interval, validate_duration, validate_coordinate
from core.hotkey_manager import HOTKEY_MAP

def create_auto_tab(app, parent):
    grid_frame = tb.Frame(parent)
    grid_frame.pack(fill=BOTH, expand=True)

    col_left = tb.Frame(grid_frame)
    col_left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6))

    col_right = tb.Frame(grid_frame)
    col_right.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 0))

    # --- تنظیمات دکمه و سرعت ---
    app.frame_config = tb.Labelframe(col_left, text=app.t("frame_config"), padding=12, bootstyle=PRIMARY)
    app.frame_config.pack(fill=X, pady=(0, 10))

    r1 = tb.Frame(app.frame_config)
    r1.pack(fill=X, pady=4)
    app.lbl_btn_mouse = tb.Label(r1, text=app.t("btn_mouse"))
    app.lbl_btn_mouse.pack(side=LEFT, padx=(0, 5))
    app.auto_btn_var = tb.StringVar(value="left")
    tb.Combobox(r1, values=["left", "right", "middle"], textvariable=app.auto_btn_var, state="readonly", width=8).pack(side=LEFT, padx=(0, 15))

    app.lbl_click_type = tb.Label(r1, text=app.t("click_type"))
    app.lbl_click_type.pack(side=LEFT, padx=(0, 5))
    app.auto_type_var = tb.StringVar(value="Single")
    tb.Combobox(r1, values=["Single", "Double"], textvariable=app.auto_type_var, state="readonly", width=8).pack(side=LEFT)

    r2 = tb.Frame(app.frame_config)
    r2.pack(fill=X, pady=6)
    app.lbl_interval = tb.Label(r2, text=app.t("interval_ms"))
    app.lbl_interval.pack(side=LEFT, padx=(0, 5))
    app.auto_interval_var = tb.StringVar(value="100")
    tb.Entry(r2, textvariable=app.auto_interval_var, width=7, justify="center", font=(app.font_family, 10, "bold")).pack(side=LEFT)
    
    app.lbl_interval_hint = tb.Label(r2, text=app.t("interval_hint"), font=(app.font_family, 8), foreground=app.text_muted)
    app.lbl_interval_hint.pack(side=LEFT, padx=5)

    app.auto_jitter_var = tb.BooleanVar(value=False)
    app.chk_jitter = tb.Checkbutton(app.frame_config, text=app.t("jitter"), variable=app.auto_jitter_var, bootstyle="success-square-toggle")
    app.chk_jitter.pack(anchor="w", pady=(6, 2))

    app.auto_sound_var = tb.BooleanVar(value=True)
    app.chk_sound = tb.Checkbutton(app.frame_config, text=app.t("sound"), variable=app.auto_sound_var, bootstyle="success-square-toggle")
    app.chk_sound.pack(anchor="w", pady=2)

    # --- مدت زمان کلیک ---
    app.frame_duration = tb.Labelframe(col_left, text=app.t("duration_title"), padding=12, bootstyle=PRIMARY)
    app.frame_duration.pack(fill=X, pady=(0, 10))

    app.auto_duration_mode = tb.StringVar(value="unlimited")
    app.radio_dur1 = tb.Radiobutton(app.frame_duration, text=app.t("unlimited"), variable=app.auto_duration_mode, value="unlimited", bootstyle=PRIMARY)
    app.radio_dur1.pack(anchor="w", pady=2)

    rd2 = tb.Frame(app.frame_duration)
    rd2.pack(fill=X, pady=2)
    app.radio_dur2 = tb.Radiobutton(rd2, text=app.t("auto_stop_after"), variable=app.auto_duration_mode, value="limited", bootstyle=PRIMARY)
    app.radio_dur2.pack(side=LEFT)
    app.auto_duration_val = tb.StringVar(value="10")
    tb.Entry(rd2, textvariable=app.auto_duration_val, width=5, justify="center", font=(app.font_family, 10, "bold")).pack(side=LEFT, padx=5)
    app.lbl_sec = tb.Label(rd2, text=app.t("seconds"))
    app.lbl_sec.pack(side=LEFT)

    # --- زمان شروع ---
    app.frame_start_time = tb.Labelframe(col_left, text=app.t("start_time_title"), padding=12, bootstyle=PRIMARY)
    app.frame_start_time.pack(fill=X, pady=(0, 10))

    app.auto_start_mode = tb.StringVar(value="instant")
    app.radio_time1 = tb.Radiobutton(app.frame_start_time, text=app.t("start_instant"), variable=app.auto_start_mode, value="instant", bootstyle=PRIMARY)
    app.radio_time1.pack(anchor="w", pady=2)

    rt2 = tb.Frame(app.frame_start_time)
    rt2.pack(fill=X, pady=2)
    app.radio_time2 = tb.Radiobutton(rt2, text=app.t("start_scheduled"), variable=app.auto_start_mode, value="scheduled", bootstyle=PRIMARY)
    app.radio_time2.pack(side=LEFT)

    now_plus_1m = datetime.datetime.now() + datetime.timedelta(minutes=1)
    app.auto_hour_var = tb.StringVar(value=now_plus_1m.strftime("%H"))
    app.auto_min_var = tb.StringVar(value=now_plus_1m.strftime("%M"))
    app.auto_sec_var = tb.StringVar(value=now_plus_1m.strftime("%S"))

    tb.Entry(rt2, textvariable=app.auto_hour_var, width=3, justify="center", font=(app.font_family, 9, "bold")).pack(side=LEFT)
    tb.Label(rt2, text=":").pack(side=LEFT, padx=1)
    tb.Entry(rt2, textvariable=app.auto_min_var, width=3, justify="center", font=(app.font_family, 9, "bold")).pack(side=LEFT)
    tb.Label(rt2, text=":").pack(side=LEFT, padx=1)
    tb.Entry(rt2, textvariable=app.auto_sec_var, width=3, justify="center", font=(app.font_family, 9, "bold")).pack(side=LEFT)

    # --- موقعیت کلیک ---
    app.frame_pos = tb.Labelframe(col_left, text=app.t("pos_title"), padding=12, bootstyle=PRIMARY)
    app.frame_pos.pack(fill=X, pady=(0, 10))

    app.auto_pos_mode = tb.StringVar(value="current")
    app.radio_pos1 = tb.Radiobutton(app.frame_pos, text=app.t("pos_current"), variable=app.auto_pos_mode, value="current", bootstyle=PRIMARY)
    app.radio_pos1.pack(anchor="w", pady=2)

    rc = tb.Frame(app.frame_pos)
    rc.pack(fill=X, pady=2)
    app.radio_pos2 = tb.Radiobutton(rc, text=app.t("pos_fixed"), variable=app.auto_pos_mode, value="custom", bootstyle=PRIMARY)
    app.radio_pos2.pack(side=LEFT)

    tb.Label(rc, text="X:").pack(side=LEFT, padx=(6, 2))
    app.auto_x_var = tb.StringVar(value="0")
    tb.Entry(rc, textvariable=app.auto_x_var, width=5, justify="center").pack(side=LEFT, padx=2)

    tb.Label(rc, text="Y:").pack(side=LEFT, padx=(6, 2))
    app.auto_y_var = tb.StringVar(value="0")
    tb.Entry(rc, textvariable=app.auto_y_var, width=5, justify="center").pack(side=LEFT, padx=2)

    app.btn_pick_pos = tb.Button(rc, text=app.t("select_pos"), bootstyle=(INFO, OUTLINE), command=app.pick_auto_custom_pos, width=10)
    app.btn_pick_pos.pack(side=LEFT, padx=6)

    # --- کارت وضعیت و اجرا ---
    app.frame_status = tb.Labelframe(col_right, text=app.t("status_title"), padding=20, bootstyle=SUCCESS)
    app.frame_status.pack(fill=BOTH, expand=True)

    app.lbl_auto_status = tb.Label(app.frame_status, text=app.t("status_stopped"), font=(app.font_family, 15, "bold"), foreground="#FF5555")
    app.lbl_auto_status.pack(pady=10)

    app.lbl_auto_count = tb.Label(app.frame_status, text=app.t("click_count") + "0", font=(app.font_family, 13, "bold"), foreground=app.current_accent)
    app.lbl_auto_count.pack(pady=10)

    app.lbl_hotkey_tip = tb.Label(app.frame_status, text=app.t("hotkey_tip").format(key="F6"), font=(app.font_family, 10), foreground="#FFB86C")
    app.lbl_hotkey_tip.pack(pady=10)

    app.btn_auto_toggle = tb.Button(app.frame_status, text=app.t("btn_start").format(key="F6"), bootstyle=SUCCESS, command=app.toggle_auto_clicker)
    app.btn_auto_toggle.pack(pady=20, fill=X, ipady=15)