from enum import Enum, auto


class PillState(Enum):
    """Pill overlay states following the state machine.

    States flow: IDLE → RECORDING → TRANSCRIBING → PROCESSING → DONE → IDLE
    This is a one-way cycle. No skipping states. No back transitions
    except the DONE → IDLE auto-dismiss.
    """

    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    PROCESSING = auto()
    DONE = auto()
    ERROR = auto()
