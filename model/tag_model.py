from typing import Dict, List
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

    def __init__(self, uuid: str, tag_type: str, attributes: Dict, position: int):
        """
        Initializes a TagModel instance with a specific UUID, type, attributes, and position.

        Args:
            uuid (str): A globally unique identifier for the tag.
            tag_type (str): The type of the tag, describing its category or functionality.
            attributes (Dict[str, any]): A dictionary containing key-value pairs that define
                                         additional properties of the tag.
            position (int): The position of the tag in a sequence or structure.
        """
        super().__init__()
        self._uuid = uuid
        self._tag_type = tag_type
        self._attributes = attributes
        self._position = position

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

    def get_attributes(self, keys: List[str] = None) -> Dict[str, any]:
        """
        Retrieves attributes based on the provided keys or returns the entire attributes dictionary.

        Args:
            keys (Optional[List[str]]): A list of keys to filter the attributes. 
                                        If None, the entire dictionary is returned.

        Returns:
            Dict[str, any]: A dictionary containing the requested key-value pairs or the entire attributes dictionary.
        """
        return self._attributes if keys is None else {key: self._attributes[key] for key in keys if key in self._attributes}

    def set_attributes(self, new_attributes: Dict[str, any]) -> None:
        """
        Updates the attributes dictionary with the provided dictionary.

        Existing keys will be updated with new values, and new keys will be added.

        Args:
            new_attributes (Dict[str, any]): A dictionary containing key-value pairs to merge into the attributes dictionary.
        """
        self._attributes.update(new_attributes)

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
