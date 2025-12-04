"""Timer constants and enums.

Defines timer status, phases, and related constants.
"""

from enum import Enum


class TimerStatus(str, Enum):
    """Timer status enumeration.

    Attributes:
        IDLE: Timer not started
        RUNNING: Timer actively counting down
        PAUSED: Timer paused by user
        COMPLETED: Timer finished current phase
    """

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class TimerPhase(str, Enum):
    """Timer phase enumeration.

    Attributes:
        WORK: Focus/work phase (default 25 minutes)
        BREAK: Rest/break phase (default 5 minutes)
    """

    WORK = "work"
    BREAK = "break"


# Default timer durations (in seconds)
DEFAULT_WORK_DURATION = 25 * 60  # 25 minutes
DEFAULT_BREAK_DURATION = 5 * 60  # 5 minutes

# Timer limits (in minutes)
MIN_WORK_DURATION = 1
MAX_WORK_DURATION = 60
MIN_BREAK_DURATION = 1
MAX_BREAK_DURATION = 30

# Room limits
MAX_PARTICIPANTS_PER_ROOM = 50
MIN_ROOM_NAME_LENGTH = 3
MAX_ROOM_NAME_LENGTH = 50
