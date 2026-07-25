# core/sound_manager.py

import winsound
import threading

def play_sound_feedback(is_start, enabled=True):
    """پخش غیربلاک‌کننده صدای هشدار صوتی ویندوز"""
    if not enabled:
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