from typing import Dict, List
from observer.interfaces import IPublisher


class GlobalSettingsModel(IPublisher):
    """
    A model for storing and managing global settings such as default folders,
    available alignment options, and the currently selected alignment option.
    """

    def __init__(self) -> None:
        """
        Initializes the global settings with empty defaults.
        """
        super().__init__()
        self._default_folders: Dict[str, str] = {}
        self._available_align_options: List[str] = []
        self._align_option: str = ""

    def set_default_folders(self, folders: Dict[str, str]) -> None:
        """
        Sets the dictionary of default folders.

        Args:
            folders (Dict[str, str]): A dictionary mapping keys to folder paths.
        """
        self._default_folders = folders
        self._notify_observers()

    def set_available_align_options(self, options: List[str]) -> None:
        """
        Sets the list of available alignment options.

        Args:
            options (List[str]): A list of strings representing alignment modes.
        """
        self._available_align_options = options
        self._notify_observers()

    def set_align_option(self, option: str) -> None:
        """
        Sets the currently selected alignment option.

        Args:
            option (str): The chosen alignment option.
        """
        self._align_option = option
        self._notify_observers()

    def get_state(self) -> Dict[str, object]:
        """
        Returns the current state of the global settings.

        Returns:
            Dict[str, object]: A dictionary containing default folders, available alignment options,
                               and the current alignment option.
        """
        return {
            "default_folders": self._default_folders,
            "available_align_options": self._available_align_options,
            "align_option": self._align_option
        }

    def set_state(self, state: Dict[str, object]) -> None:
        """
        Updates the internal state based on a provided dictionary.

        Args:
            state (Dict[str, object]): Dictionary containing one or more of the state keys.
        """
        self._default_folders = state.get("default_folders", {})
        self._available_align_options = state.get(
            "available_align_options", [])
        self._align_option = state.get("align_option", "")
        self._notify_observers()
