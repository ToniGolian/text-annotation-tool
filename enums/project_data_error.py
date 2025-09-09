from enum import Enum, auto


class ProjectDataError(Enum):
    EMPTY_PROJECT_NAME = auto()
    EMPTY_SELECTED_TAGS = auto()
    EMPTY_TAG_GROUP_FILE_NAME = auto()
    EMPTY_TAG_GROUPS = auto()
    DUPLICATE_PROJECT_NAME = auto()
