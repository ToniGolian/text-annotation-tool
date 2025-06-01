from input_output.interfaces import IFileHandler
from utils.interfaces import IListManager, ISettingsManager


class ListManager(IListManager):
    def __init__(self, file_handler: IFileHandler, settings_manager: ISettingsManager):
        """
        Initializes the ListManager with a file handler for file operations and a settings manager.

        Args:
            file_handler (IFileHandler): An instance of a file handler to manage file reading and writing operations.
            settings_manager (ISettingsManager): An instance of a settings manager to manage the application settings.
        """
        self._file_handler = file_handler
        self._settings_manager = settings_manager

    def get_abbreviations(self) -> set[str]:
        """
        Loads abbreviations for the specified languages from a JSON file and combines them into a single set.

        Returns:
            set[str]: A set containing all abbreviations for the specified languages.

        Raises:
            KeyError: If any of the provided keys are missing in the JSON file.
        """
        languages = self._settings_manager.get_current_languages()
        abbreviations_data = self._file_handler.read_file(
            "project_abbreviations")
        abbreviations = set()

        # Combine abbreviations for all specified languages
        for language in languages:
            if language in abbreviations_data:
                abbreviations.update(abbreviations_data[language])
            else:
                raise KeyError(
                    f"The key '{language}' is missing")

        return abbreviations
