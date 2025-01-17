from typing import List, Dict
from abc import ABC, abstractmethod
from typing import Dict, List

from model.interfaces import ITagModel


class IListManager(ABC):
    @abstractmethod
    def get_abbreviations(self) -> set[str]:
        """
        Loads abbreviations
        """


class ISettingsManager(ABC):
    """
    Interface for a settings manager that handles application settings, 
    including managing current and available languages.
    """

    @abstractmethod
    def get_current_languages(self) -> List[str]:
        """
        Retrieves the current languages from the settings.

        Returns:
            List[str]: A list of current languages.
        """
        pass

    @abstractmethod
    def set_current_languages(self, current_languages: List[str]) -> None:
        """
        Updates the current languages in the settings and ensures they are also available.

        Args:
            current_languages (List[str]): A list of new current languages.
        """
        pass

    @abstractmethod
    def get_available_languages(self) -> List[str]:
        """
        Retrieves the available languages from the settings.

        Returns:
            List[str]: A list of available languages.
        """
        pass

    @abstractmethod
    def set_available_languages(self, additional_languages: List[str]) -> None:
        """
        Adds new languages to the available languages list.

        Args:
            additional_languages (List[str]): A list of languages to add.
        """
        pass

    @abstractmethod
    def delete_available_languages(self, languages_to_remove: List[str]) -> None:
        """
        Removes specified languages from the available languages list.

        Args:
            languages_to_remove (List[str]): A list of languages to remove.
        """
        pass


class ITagManager(ABC):
    @abstractmethod
    def add_tag(self, tag_data: dict) -> None:
        """
        Simulates adding a tag by appending it to the tags list and updating the text.
        """

    @abstractmethod
    def edit_tag(self, tag_id: str, tag_data: dict) -> None:
        """
        Simulates editing a tag by updating the corresponding tag in the tags list.
        """
    @abstractmethod
    def delete_tag(self, tag_id: str) -> None:
        """
        Simulates deleting a tag by removing it from the tags list.
        """

    @abstractmethod
    def get_tag_data(self, tag_uuid: str) -> ITagModel:
        """
        Retrieves the data of a tag by its unique UUID.
        """


class ITagProcessor(ABC):
    """
    Interface for a processor that handles tag-to-string transformations
    and performs text operations involving tags.
    """

    @abstractmethod
    def tags_to_strings(self, tags: List[Dict]) -> List[str]:
        """
        Converts tag objects into their string representations.

        Args:
            tags (List[Dict]): A list of tag dictionaries.

        Returns:
            List[str]: A list of string representations of the tags.
        """
        pass

    @abstractmethod
    def insert_tag_into_text(self, text: str, tag_data: Dict) -> str:
        """
        Inserts a single tag as a string into the specified text.

        Args:
            text (str): The document text where the tag should be inserted.
            tag_data (Dict): A dictionary containing the tag data to insert.

        Returns:
            str: The updated text with the tag inserted at the specified position.
        """
        pass

    @abstractmethod
    def extract_tags_from_text(self, text: str) -> List[Dict]:
        """
        Extracts tag information from the text.

        Args:
            text (str): The document text.

        Returns:
            List[Dict]: A list of extracted tag dictionaries.
        """
        pass
