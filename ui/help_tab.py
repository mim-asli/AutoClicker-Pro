# ui/help_tab.py

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from utils.translations import THEME_ACCENTS_FA, THEME_ACCENTS_EN
from core.hotkey_manager import HOTKEY_MAP

def create_general_settings_tab(app, parent):
    grid_frame = tb.Frame(parent)
    grid_frame.pack(fill=BOTH, expand=True)

    col1 = tb.Frame(grid_frame)
    col1.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6))

    col2 = tb.Frame(grid_frame)
    col2.pack(side=RIGHT, fill=BOTH, expand=True, padx=(6, 0))

    # کادر ۱: ظاهر، زبان و شناورسازی
    app.frame_visuals = tb.Labelframe(col1, text=app.t("frame_visuals"), padding=12, bootstyle=INFO)
    app.frame_visuals.pack(fill=X, pady=(0, 10))

    rv_lang = tb.Frame(app.frame_visuals)
    rv_lang.pack(fill=X, pady=3)
    app.lbl_lang_select = tb.Label(rv_lang, text=app.t("lang_select"))
    app.lbl_lang_select.pack(side=LEFT, padx=(0, 8))
    app.lang_var = tb.StringVar(value="🇮🇷 فارسی (Persian)")
    app.combo_lang = tb.Combobox(rv_lang, values=["🇮🇷 فارسی (Persian)", "🇬🇧 English"], textvariable=app.lang_var, state="readonly", width=16)
    app.combo_lang.pack(side=LEFT)
    app.combo_lang.bind("<<ComboboxSelected>>", app._on_language_changed)

    rv0 = tb.Frame(app.frame_visuals)
    rv0.pack(fill=X, pady=5)
    app.lbl_theme_mode = tb.Label(rv0, text=app.t("theme_mode"))
    app.lbl_theme_mode.pack(side=LEFT, padx=(0, 8))
    app.mode_theme_var = tb.StringVar(value="🌙 تاریک (Dark)")
    app.combo_mode = tb.Combobox(rv0, values=["🌙 تاریک (Dark)", "☀️ روشن (Light)"], textvariable=app.mode_theme_var, state="readonly", width=14)
    app.combo_mode.pack(side=LEFT)
    app.combo_mode.bind("<<ComboboxSelected>>", app._on_mode_theme_changed)

    rv1 = tb.Frame(app.frame_visuals)
    rv1.pack(fill=X, pady=5)
    app.lbl_accent_color = tb.Label(rv1, text=app.t("accent_color"))
    app.lbl_accent_color.pack(side=LEFT, padx=(0, 8))
    app.accent_theme_var = tb.StringVar(value="🟢 سبز نئونی")
    app.combo_accent = tb.Combobox(rv1, values=list(THEME_ACCENTS_FA.keys()), textvariable=app.accent_theme_var, state="readonly", width=14)
    app.combo_accent.pack(side=LEFT)
    app.combo_accent.bind("<<ComboboxSelected>>", app._on_accent_changed)

    rv2 = tb.Frame(app.frame_visuals)
    rv2.pack(fill=X, pady=5)
    app.always_on_top_var = tb.BooleanVar(value=False)
    app.chk_topmost = tb.Checkbutton(rv2, text=app.t("always_top"), variable=app.always_on_top_var, command=app.toggle_topmost, bootstyle="info-square-toggle")
    app.chk_topmost.pack(anchor="w")

    # کادر ۲: کلید میانبر
    app.frame_hotkey = tb.Labelframe(col1, text=app.t("hotkey_title"), padding=12, bootstyle=INFO)
    app.frame_hotkey.pack(fill=X, pady=(0, 10))

    rhk = tb.Frame(app.frame_hotkey)
    rhk.pack(fill=X)
    app.lbl_hk = tb.Label(rhk, text=app.t("hotkey_lbl"))
    app.lbl_hk.pack(side=LEFT, padx=(0, 10))
    app.auto_hotkey_var = tb.StringVar(value="F6")
    app.combo_hotkey = tb.Combobox(rhk, values=list(HOTKEY_MAP.keys()), textvariable=app.auto_hotkey_var, state="readonly", width=8)
    app.combo_hotkey.pack(side=LEFT)
    app.combo_hotkey.bind("<<ComboboxSelected>>", app._on_hotkey_changed)

    # کادر ۳: راهنما
    card_q = tb.Labelframe(col2, text=" 🚀 Guide & Features ", padding=12, bootstyle=PRIMARY)
    card_q.pack(fill=BOTH, expand=True)

    app.lbl_help_q_title = tb.Label(card_q, text=app.t("help_quick_title"), font=(app.font_family, 11, "bold"))
    app.lbl_help_q_title.pack(anchor="w", pady=(0, 5))

    app.lbl_help_q1 = tb.Label(card_q, text=app.t("help_quick_1"), font=(app.font_family, 10))
    app.lbl_help_q1.pack(anchor="w", pady=2)

    app.lbl_help_q2 = tb.Label(card_q, text=app.t("help_quick_2"), font=(app.font_family, 10))
    app.lbl_help_q2.pack(anchor="w", pady=2)

    app.lbl_help_q3 = tb.Label(card_q, text=app.t("help_quick_3"), font=(app.font_family, 10))
    app.lbl_help_q3.pack(anchor="w", pady=(2, 10))

    app.lbl_help_f_title = tb.Label(card_q, text=app.t("help_features_title"), font=(app.font_family, 11, "bold"))
    app.lbl_help_f_title.pack(anchor="w", pady=(5, 5))

    app.lbl_help_f1 = tb.Label(card_q, text=app.t("help_feat_1"), font=(app.font_family, 10))
    app.lbl_help_f1.pack(anchor="w", pady=2)

    app.lbl_help_f2 = tb.Label(card_q, text=app.t("help_feat_2"), font=(app.font_family, 10))
    app.lbl_help_f2.pack(anchor="w", pady=2)

    app.lbl_help_f3 = tb.Label(card_q, text=app.t("help_feat_3"), font=(app.font_family, 10))
    app.lbl_help_f3.pack(anchor="w", pady=2)

    app.lbl_help_f4 = tb.Label(card_q, text=app.t("help_feat_4"), font=(app.font_family, 10))
    app.lbl_help_f4.pack(anchor="w", pady=2)