from enum import Enum, auto


class GameSignal(Enum):
    """State machine control signals"""
    STAY = auto()
    START_GAME = auto()
    PAUSE_GAME = auto()
    UNPAUSE_GAME = auto()
    GO_TO_MENU = auto()
    NEXT_LEVEL = auto()
    RESTART_LEVEL = auto()
    END_LEVEL = auto()
