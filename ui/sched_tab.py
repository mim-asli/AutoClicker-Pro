# ui/sched_tab.py

import time
import datetime
import threading
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from core.click_engine import win32_fast_click

def create_sched_tab(app, parent):
    app.frame_sched_cfg = tb.Labelframe(parent, text=app.t("sched_cfg_title"), padding=15, bootstyle=INFO)
    app.frame_sched_cfg.pack(fill=X, pady=(0, 15))

    time_row = tb.Frame(app.frame_sched_cfg)
    time_row.pack(fill=X, pady=5)
    app.lbl_sched_time = tb.Label(time_row, text=app.t("sched_time_lbl"), font=(app.font_family, 10))
    app.lbl_sched_time.pack(side=LEFT, padx=(0, 10))

    now_plus_1m = datetime.datetime.now() + datetime.timedelta(minutes=1)
    app.hour_var = tb.StringVar(value=now_plus_1m.strftime("%H"))
    app.min_var = tb.StringVar(value=now_plus_1m.strftime("%M"))
    app.sec_var = tb.StringVar(value=now_plus_1m.strftime("%S"))

    tb.Entry(time_row, textvariable=app.hour_var, width=4, justify="center", font=(app.font_family, 10, "bold")).pack(side=LEFT)
    tb.Label(time_row, text=":", font=(app.font_family, 11, "bold")).pack(side=LEFT, padx=2)
    tb.Entry(time_row, textvariable=app.min_var, width=4, justify="center", font=(app.font_family, 10, "bold")).pack(side=LEFT)
    tb.Label(time_row, text=":", font=(app.font_family, 11, "bold")).pack(side=LEFT, padx=2)
    tb.Entry(time_row, textvariable=app.sec_var, width=4, justify="center", font=(app.font_family, 10, "bold")).pack(side=LEFT)

    delay_row = tb.Frame(app.frame_sched_cfg)
    delay_row.pack(fill=X, pady=10)
    app.lbl_sched_delay = tb.Label(delay_row, text=app.t("sched_delay_lbl"), font=(app.font_family, 10))
    app.lbl_sched_delay.pack(side=LEFT, padx=(0, 10))
    app.delay_var = tb.StringVar(value="100")
    tb.Entry(delay_row, textvariable=app.delay_var, width=8, justify="center", font=(app.font_family, 10)).pack(side=LEFT)

    app.frame_sched_pts = tb.Labelframe(parent, text=app.t("sched_pts_title"), padding=10, bootstyle=PRIMARY)
    app.frame_sched_pts.pack(fill=BOTH, expand=True)

    ctrl_frame = tb.Frame(app.frame_sched_pts)
    ctrl_frame.pack(fill=X, pady=(0, 10))
    app.btn_sched_add = tb.Button(ctrl_frame, text=app.t("sched_add_btn"), bootstyle=SUCCESS, command=app.add_point_row)
    app.btn_sched_add.pack(side=LEFT, padx=5)
    app.btn_sched_rem = tb.Button(ctrl_frame, text=app.t("sched_rem_btn"), bootstyle=DANGER, command=app.remove_point_row)
    app.btn_sched_rem.pack(side=LEFT, padx=5)

    canvas_frame = tb.Frame(app.frame_sched_pts)
    canvas_frame.pack(fill=BOTH, expand=True)

    app.canvas = tb.Canvas(canvas_frame, borderwidth=0, highlightthickness=0)
    app.scrollbar = tb.Scrollbar(canvas_frame, orient=VERTICAL, command=app.canvas.yview)
    app.scrollable_frame = tb.Frame(app.canvas)

    app.scrollable_frame.bind("<Configure>", lambda e: app.canvas.configure(scrollregion=app.canvas.bbox("all")))
    app.canvas_window = app.canvas.create_window((0, 0), window=app.scrollable_frame, anchor="nw")
    app.canvas.bind("<Configure>", lambda e: app.canvas.itemconfig(app.canvas_window, width=e.width))
    app.canvas.bind_all("<MouseWheel>", lambda e: app.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
    app.canvas.configure(yscrollcommand=app.scrollbar.set)
    app.canvas.pack(side=LEFT, fill=BOTH, expand=True)
    app.scrollbar.pack(side=RIGHT, fill=Y)

    app.sched_status_label = tb.Label(parent, text=app.t("sched_status_ready"), font=(app.font_family, 12, "bold"), bootstyle=PRIMARY)
    app.sched_status_label.pack(pady=10)

    btn_frame = tb.Frame(parent)
    btn_frame.pack(fill=X, pady=5)
    app.sched_start_btn = tb.Button(btn_frame, text=app.t("sched_start_btn"), bootstyle=(SUCCESS, OUTLINE), command=app.start_sched_timer)
    app.sched_start_btn.pack(side=LEFT, expand=True, padx=5, fill=X)
    app.sched_stop_btn = tb.Button(btn_frame, text=app.t("sched_stop_btn"), bootstyle=(DANGER, OUTLINE), command=app.stop_sched_timer, state=DISABLED)
    app.sched_stop_btn.pack(side=LEFT, expand=True, padx=5, fill=X)