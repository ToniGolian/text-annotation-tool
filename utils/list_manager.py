from input_output.interfaces import IFileHandler
from utils.interfaces import IListManager


class ListManager(IListManager):
    def __init__(self, file_handler: IFileHandler):
        """
        Initializes the ListManager with a file handler for file operations.

        Args:
            file_handler (IFileHandler): An instance of a file handler to manage file reading and writing operations.
        """
        self._file_handler = file_handler

    def get_abbreviations(self, languages: list[str]) -> set[str]:
        """
        Loads abbreviations for the specified languages from a JSON file and combines them into a single set.

        Args:
            languages (list[str]): A list of language keys to fetch abbreviations for.

        Returns:
            set[str]: A set containing all abbreviations for the specified languages.

        Raises:
            KeyError: If any of the provided keys are missing in the JSON file.
        """
        # todo get file path from config
        file_path = "app_data/abbreviations.json"
        abbreviations = set()

        # Use the file handler to read the file
        data = self._file_handler.read_file(file_path)

        # Combine abbreviations for all specified languages
        for language in languages:
            if language in data:
                abbreviations.update(data[language])
            else:
                raise KeyError(
                    f"The key '{language}' is missing in the JSON file '{file_path}'.")

        return abbreviations
