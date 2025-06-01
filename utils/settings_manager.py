from typing import List

from input_output.file_handler import FileHandler


class SettingsManager:
    """
    Manages application settings, including current and available languages.
    """

    def __init__(self, file_handler: FileHandler) -> None:
        """
        Initializes the SettingsManager, loading file paths and settings.
        """
        self._filehandler = file_handler

    def get_current_languages(self) -> List[str]:
        """
        Retrieves the current languages from the settings file.

        Returns:
            List[str]: A list of current languages.
        """
        settings = self._filehandler.read_file(
            "settings_folder", extension="languages.json")
        return settings.get("current_languages", [])

    def set_current_languages(self, current_languages: List[str]) -> None:
        """
        Updates the current languages in the settings file. 
        Also adds any new languages from the provided list to the available languages.

        Args:
            current_languages (List[str]): A list of new current languages.
        """
        settings = self._filehandler.read_file(
            "default_path_settings", extension="languages.json")

        # Update the current languages
        settings["current_languages"] = current_languages

        # Ensure all current languages are in available languages
        available_languages = settings.get("available_languages", [])
        for language in current_languages:
            if language not in available_languages:
                available_languages.append(language)

        settings["available_languages"] = available_languages

        # Save the updated settings
        self._filehandler.write_file(
            "default_path_settings", settings, extension="languages.json")

    def get_available_languages(self) -> List[str]:
        """
        Retrieves the available languages from the settings file.

        Returns:
            List[str]: A list of available languages.
        """
        settings = self._filehandler.read_file(
            "default_path_settings", extension="languages.json")
        return settings.get("available_languages", [])

    def set_available_languages(self, additional_languages: List[str]) -> None:
        """
        Adds new languages to the available languages in the settings file.
        Ensures no duplicates are added.

        Args:
            additional_languages (List[str]): A list of new languages to add to available languages.
        """
        settings = self._filehandler.read_file(
            "default_path_settings", extension="languages.json")

        # Get the current available languages
        available_languages = set(settings.get("available_languages", []))
        # Add new languages without duplication
        available_languages.update(additional_languages)

        settings["available_languages"] = list(available_languages)

        # Save the updated settings
        self._filehandler.write_file(
            "default_path_settings", settings, extension="languages.json")

    def delete_available_languages(self, languages_to_remove: List[str]) -> None:
        """
        Removes the specified languages from the available languages in the settings file.

        Args:
            languages_to_remove (List[str]): A list of languages to be removed.
        """
        settings = self._filehandler.read_file(
            "default_path_settings", extension="languages.json")

        # Filter out the languages to be removed
        available_languages = settings.get("available_languages", [])
        updated_languages = [
            lang for lang in available_languages if lang not in languages_to_remove]

        settings["available_languages"] = updated_languages

        # Save the updated settings
        self._filehandler.write_file(
            "default_path_settings", settings, extension="languages.json")
