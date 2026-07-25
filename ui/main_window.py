# ui/main_window.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ui.auto_tab import create_auto_tab
from ui.sched_tab import create_sched_tab
from ui.help_tab import create_general_settings_tab

def build_main_window_layout(app):
    main_container = tb.Frame(app.root)
    main_container.pack(fill=BOTH, expand=True, padx=12, pady=12)

    left_panel = tb.Frame(main_container, width=280, padding=15)
    left_panel.pack(side=LEFT, fill=Y, padx=(0, 12))

    app.lbl_title_brand = tb.Label(left_panel, text="AUTO ⚡", font=(app.font_family, 26, "bold"), foreground=app.text_white)
    app.lbl_title_brand.pack(anchor="w")

    lbl_brand_accent = tb.Label(left_panel, text="CLICKER PRO", font=(app.font_family, 22, "bold"), foreground=app.current_accent)
    lbl_brand_accent.pack(anchor="w")
    app.accent_labels.append(lbl_brand_accent)

    app.lbl_sub_brand = tb.Label(left_panel, text=app.t("sub_title"), font=(app.font_family, 9), foreground=app.text_muted)
    app.lbl_sub_brand.pack(anchor="w", pady=(0, 20))

    app.feature_card_labels = []
    for i in range(1, 7):
        card = tb.Frame(left_panel, padding=10)
        card.pack(fill=X, pady=4)
        lbl_t = tb.Label(card, text=app.t(f"f{i}_t"), font=(app.font_family, 10, "bold"), foreground=app.current_accent)
        lbl_t.pack(anchor="w")
        app.accent_labels.append(lbl_t)

        lbl_d = tb.Label(card, text=app.t(f"f{i}_d"), font=(app.font_family, 8), foreground=app.text_muted)
        lbl_d.pack(anchor="w")
        app.feature_card_labels.append((lbl_t, lbl_d))

    right_panel = tb.Frame(main_container)
    right_panel.pack(side=RIGHT, fill=BOTH, expand=True)

    app.notebook = tb.Notebook(right_panel, bootstyle=PRIMARY)
    app.notebook.pack(fill=BOTH, expand=True)

    app.auto_tab = tb.Frame(app.notebook, padding=12)
    app.sched_tab = tb.Frame(app.notebook, padding=12)
    app.help_tab = tb.Frame(app.notebook, padding=12)

    app.notebook.add(app.auto_tab, text=app.t("tab_auto"))
    app.notebook.add(app.sched_tab, text=app.t("tab_sched"))
    app.notebook.add(app.help_tab, text=app.t("tab_help"))

    create_auto_tab(app, app.auto_tab)
    create_sched_tab(app, app.sched_tab)
    create_general_settings_tab(app, app.help_tab)

    status_bar = tb.Frame(right_panel, padding=(12, 6))
    status_bar.pack(fill=X, side=BOTTOM, pady=(8, 0))

    app.lbl_ready = tb.Label(status_bar, text=app.t("status_ready"), font=(app.font_family, 9, "bold"), foreground=app.current_accent)
    app.lbl_ready.pack(side=LEFT)

    app.lbl_total_clicks_bottom = tb.Label(status_bar, text=app.t("total_clicks") + "0", font=(app.font_family, 9, "bold"), foreground=app.text_white)
    app.lbl_total_clicks_bottom.pack(side=RIGHT, padx=15)

    app.lbl_timer_bottom = tb.Label(status_bar, text=app.t("run_time") + "00:00:00", font=(app.font_family, 9), foreground=app.text_muted)
    app.lbl_timer_bottom.pack(side=RIGHT)