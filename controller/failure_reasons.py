from enum import Enum, auto


class FailureReason(Enum):
    TAG_IS_REFERENCED = auto()
    COMPARISON_MODE_REF_NOT_ALLOWED = auto()
