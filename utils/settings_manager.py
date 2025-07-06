
from input_output.file_handler import FileHandler


class SettingsManager:
    """
    Manages application settings, including current and available languages.
    """

    def __init__(self, file_handler: FileHandler) -> None:
        """
        Initializes the SettingsManager, loading file paths and settings.
        """
        self._file_handler = file_handler
        self._project_settings = self._file_handler.read_file(
            "project_settings")

    def are_all_search_results_highlighted(self) -> bool:
        """
        Checks if all search results are highlighted.

        Returns:
            bool: True if all search results are highlighted, False otherwise.
        """
        return self._project_settings.get("are_all_search_results_highlighted", True)

    def set_all_search_results_highlighted(self, highlighted: bool) -> None:
        """
        Sets the highlight state for all search results.

        Args:
            highlighted (bool): True to highlight all results, False to unhighlight.
        """
        self._project_settings["are_all_search_results_highlighted"] = highlighted

    def get_current_language(self) -> str:
        """
        Retrieves the current languages from the settings file.

        Returns:
            List[str]: A list of current languages.
        """
        return self._project_settings.get("current_languages", [])

    def set_current_language(self, current_language: str) -> None:
        """
        Sets the current language in the settings file.

        Args:
            current_language (str): The new current language to set.
        """
        self._project_settings["current_language"] = current_language

    def get_color_scheme(self) -> dict:
        """
        Retrieves the current color scheme from the settings file.

        Returns:
            dict: The current color scheme.
        """

        color_scheme_file_name = self._project_settings.get("color_scheme")
        return self._file_handler.read_file(
            "project_color_scheme_folder", color_scheme_file_name)

    def get_abbreviations(self) -> dict:
        """
        Retrieves the abbreviations for the current languages from the settings file.

        Returns:
            dict: A dictionary containing abbreviations for each language.
        """
        abbreviations = self._file_handler.read_file("project_abbreviations")
        current_language = self._project_settings.get("current_language", [])
        language_specific_abbreviations = abbreviations.get(current_language)
        if language_specific_abbreviations is None:
            raise KeyError(
                f"The key '{self._project_settings.get('current_language')}' is missing in the abbreviations file.")
        return language_specific_abbreviations

    def get_search_normalization(self) -> dict:
        """
        Retrieves the search normalization settings from the settings file.

        Returns:
            dict: The search normalization settings.
        """
        current_language = self._project_settings.get("current_language", [])
        search_normalization_rules = self._file_handler.read_file(
            "project_search_normalization")
        if not search_normalization_rules:
            raise KeyError(
                "The key 'project_search_normalization' is missing in the settings file.")
        search_normalization_rules["common_suffixes"] = search_normalization_rules.get(
            "common_suffixes", []).get(current_language, [])
        return search_normalization_rules
