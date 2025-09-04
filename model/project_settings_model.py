from typing import Dict
from observer.interfaces import IPublisher


class ProjectSettingsModel(IPublisher):
    """
    A model for managing project-specific settings such as color scheme, language,
    search normalization, and highlighting behavior.
    """

    def __init__(self) -> None:
        """
        Initializes the project settings with default values.
        """
        super().__init__()
        self._project_name: str = ""
        self._color_scheme: str = ""
        self._search_normalization: Dict[str, str] = {}
        self._are_all_search_results_highlighted: bool = False
        self._current_language: str = ""

    def set_project_name(self, name: str) -> None:
        """
        Sets the project name.

        Args:
            name (str): The name of the project.
        """
        self._project_name = name
        self.notify_observers()

    def set_color_scheme(self, scheme: str) -> None:
        """
        Sets the color scheme used in the project.

        Args:
            scheme (str): The name of the color scheme.
        """
        self._color_scheme = scheme
        self.notify_observers()

    def set_search_normalization(self, normalization: Dict[str, str]) -> None:
        """
        Sets the search normalization settings.

        Args:
            normalization (Dict[str, str]): A dictionary of normalization rules.
        """
        self._search_normalization = normalization
        self.notify_observers()

    def set_are_all_search_results_highlighted(self, value: bool) -> None:
        """
        Sets whether all search results are highlighted.

        Args:
            value (bool): True to highlight all results, False otherwise.
        """
        self._are_all_search_results_highlighted = value
        self.notify_observers()

    def set_current_language(self, language: str) -> None:
        """
        Sets the current language of the project.

        Args:
            language (str): The selected language code or name.
        """
        self._current_language = language
        self.notify_observers()

    def get_state(self) -> Dict[str, object]:
        """
        Returns the current state of the project settings.

        Returns:
            Dict[str, object]: A dictionary containing all project settings.
        """
        return {
            "project_name": self._project_name,
            "color_scheme": self._color_scheme,
            "search_normalization": self._search_normalization,
            "are_all_search_results_highlighted": self._are_all_search_results_highlighted,
            "current_language": self._current_language
        }

    def set_state(self, state: Dict[str, object]) -> None:
        """
        Updates the internal state based on a provided dictionary.

        Args:
            state (Dict[str, object]): Dictionary containing one or more project setting keys.
        """
        self._project_name = state.get("project_name", "")
        self._color_scheme = state.get("color_scheme", "")
        self._search_normalization = state.get("search_normalization", {})
        self._are_all_search_results_highlighted = state.get(
            "are_all_search_results_highlighted", False)
        self._current_language = state.get("current_language", "")
        self.notify_observers()
