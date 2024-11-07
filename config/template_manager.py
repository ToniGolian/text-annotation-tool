import os
from typing import List, Dict
from io.file_handler import FileHandler


class TemplateManager:
    """
    Manages loading and storing of tag templates from JSON files.

    Attributes:
        _path (str): Path to the directory containing JSON files with tag templates.
        _templates (List[Dict]): List of dictionaries loaded from the JSON files.
        _file_handler (FileHandler): Instance of FileHandler to manage file operations.
    """

    def __init__(self, path: str = "/app_data/tag_templates") -> None:
        """
        Initializes the TemplateManager with a given path and loads JSON templates.

        Args:
            path (str): The path to the directory where tag templates are stored.
        """
        self._path: str = path
        self._templates: List[Dict] = []
        self._file_handler = FileHandler()
        self._load_templates()

    def _load_templates(self) -> None:
        """
        Loads all JSON files in the specified directory, reads them, and appends the resulting dictionaries to the templates list.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            ValueError: If a JSON file is invalid or cannot be parsed.
        """
        if not os.path.exists(self._path):
            raise FileNotFoundError(f"The path '{self._path}' does not exist.")

        for filename in os.listdir(self._path):
            if filename.endswith(".json"):
                file_path = os.path.join(self._path, filename)
                try:
                    template_data = self._file_handler.read_file(file_path)
                    self._templates.append(template_data)
                except ValueError as e:
                    raise ValueError(
                        f"Error parsing JSON in file '{file_path}': {e}")

    def get_template(self, tag_type: str) -> Dict:
        """
        Retrieves the template dictionary for a given tag type.

        Args:
            tag_type (str): The type of tag for which to retrieve the template.

        Returns:
            dict: The template dictionary for the specified tag type, or an empty dictionary if the tag type is not found.
        """
        for template in self._templates:
            if template.get("type") == tag_type:
                return template
        return {}

    def reload_templates(self) -> None:
        """
        Clears and reloads all templates from the JSON files.
        """
        self._templates.clear()
        self._load_templates()

    def get_path(self) -> str:
        """
        Returns the path to the directory where tag templates are stored.

        Returns:
            str: The current path to the tag template directory.
        """
        return self._path

    def set_path(self, new_path: str) -> None:
        """
        Sets a new path to the directory where tag templates are stored and reloads the templates.

        Args:
            new_path (str): The new path to set.
        """
        self._path = new_path
        self.reload_templates()
