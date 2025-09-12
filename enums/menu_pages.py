
from enum import Enum, auto


class MenuPage(Enum):
    NEW_PROJECT = auto()
    EDIT_PROJECT = auto()
    PROJECT_SETTINGS = auto()
    GLOBAL_SETTINGS = auto()
    NEW_TAG = auto()
    EDIT_TAG = auto()
    HELP = auto()
    ABOUT = auto()


class MenuSubpage(Enum):
    PROJECT_NAME = auto()
    PROJECT_TAGS = auto()
    PROJECT_TAG_GROUPS = auto()
    EDIT_NAME = auto()
    EDIT_TAGS = auto()
    EDIT_TAG_GROUPS = auto()
