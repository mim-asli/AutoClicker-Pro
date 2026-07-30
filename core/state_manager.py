# core/state_manager.py

from enum import Enum, auto

class AppState(Enum):
    IDLE = auto()
    AUTO_CLICKING = auto()
    SCHEDULER_WAITING = auto()
    SCHEDULER_CLICKING = auto()

class StateManager:
    """مدیریت مرکز وضعیت برنامه (State Machine) جهت جلوگیری از تداخل تردهای موازی"""
    def __init__(self):
        self._state = AppState.IDLE

    def get_state(self):
        return self._state

    def is_idle(self):
        return self._state == AppState.IDLE

    def set_state(self, new_state: AppState):
        self._state = new_state