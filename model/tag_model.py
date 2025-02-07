from typing import Dict, List, Tuple
from model.interfaces import ITagModel


class TagModel(ITagModel):
    """
    Represents a tag model with a specific UUID, type, attributes, and position.

    This class encapsulates the details of a tag, including its unique identifier (UUID),
    type, associated attributes, and its position within a sequence or structure.

    Attributes:
        uuid (str): A globally unique identifier for the tag.
        tag_type (str): The type of the tag, describing its category or functionality.
        attributes (Dict[str, any]): A dictionary containing key-value pairs that define
                                     additional properties of the tag.
        position (int): The position of the tag in a sequence or structure.
    """

    def __init__(self, uuid: str, tag_type: str, attributes: List[Tuple[str, str]], position: int, text: str):
        """
        Initializes a TagModel instance with a specific UUID, type, attributes, position, and text.

        Args:
            uuid (str): A globally unique identifier for the tag.
            tag_type (str): The type of the tag, describing its category or functionality.
            attributes (List[Tuple[str, str]]): A list of key-value pairs representing the tag's attributes.
            position (int): The position of the tag in a sequence or structure.
            text (str): The selected text associated with the tag.
        """
        super().__init__()
        self._uuid = uuid
        self._tag_type = tag_type
        self._attributes = {key: value for key, value in attributes}
        self._position = position
        self._text = text

    def get_uuid(self) -> str:
        """
        Gets the globally unique identifier (UUID) of the tag.

        Returns:
            str: The UUID of the tag.
        """
        return self._uuid

    def set_uuid(self, uuid: str) -> None:
        """
        Sets the globally unique identifier (UUID) of the tag.

        Args:
            uuid (str): The new UUID for the tag.
        """
        self._uuid = uuid

    def get_attributes(self, keys: List[str] = None) -> Dict[str, str]:
        """
        Retrieves attributes based on the provided keys or returns the entire attributes dictionary.

        Args:
            keys (Optional[List[str]]): A list of keys to filter the attributes. 
                                        If None, the entire dictionary is returned.

        Returns:
            Dict[str, str]: A dictionary containing the requested key-value pairs or the entire attributes dictionary.
        """
        return self._attributes if keys is None else {key: self._attributes[key] for key in keys if key in self._attributes}

    def set_attributes(self, new_attributes: List[Tuple[str, str]]) -> None:
        """
        Updates the attributes dictionary with the provided list of key-value pairs.

        Existing keys will be updated with new values, and new keys will be added.

        Args:
            new_attributes (List[Tuple[str, str]]): A list of key-value pairs to merge into the attributes dictionary.
        """
        self._attributes.update({key: value for key, value in new_attributes})

    def get_tag_type(self) -> str:
        """
        Gets the type of the tag.

        Returns:
            str: The type of the tag.
        """
        return self._tag_type

    def set_tag_type(self, tag_type: str) -> None:
        """
        Sets the type of the tag.

        Args:
            tag_type (str): The new type of the tag.
        """
        self._tag_type = tag_type

    def get_position(self) -> int:
        """
        Gets the position of the tag.

        Returns:
            int: The position of the tag.
        """
        return self._position

    def set_position(self, position: int) -> None:
        """
        Sets the position of the tag.

        Args:
            position (int): The new position of the tag.
        """
        self._position = position

    def get_text(self) -> str:
        """
        Gets the text associated with the tag.

        Returns:
            str: The text associated with the tag.
        """
        return self._text

    def set_text(self, text: str) -> None:
        """
        Sets the text associated with the tag.

        Args:
            text (str): The new text to associate with the tag.
        """
        self._text = text

    def get_id(self) -> str:
        """
        Gets the ID of the tag from the attributes.

        Returns:
            str: The ID of the tag if it exists in the attributes, otherwise None.
        """
        return self._attributes.get("id")

    def set_id(self, new_id: str) -> None:
        """
        Sets the ID of the tag in the attributes.

        Args:
            new_id (str): The new ID to set for the tag.
        """
        self._attributes["id"] = new_id

    def __str__(self) -> str:
        """
        Returns a string representation of the tag as it would appear in the text.

        The string includes the tag type, all attributes, and the associated text.

        Returns:
            str: A string representation of the tag in the format:
                <tag_type attr1="value1" attr2="value2">text</tag_type>
        """
        attributes_str = " ".join(
            f'{key}="{value}"' for key, value in self._attributes.items())
        return f'<{self._tag_type} {attributes_str}>{self._text}</{self._tag_type}>'
