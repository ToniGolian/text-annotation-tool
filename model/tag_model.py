from typing import Any, Dict, List, Tuple
from model.interfaces import ITagModel


class TagModel(ITagModel):
    """
    Represents a tag model with attributes stored in a dictionary.

    This class encapsulates a tag's details, including its unique identifier (UUID),
    type, attributes, position, text, ID string, and referenced attributes.

    Attributes:
        _tag_data (Dict[str, Any]): A dictionary containing all tag-related data.
    """

    def __init__(self, tag_data: Dict[str, Any]):
        """
        Initializes a TagModel instance using a dictionary containing all necessary data.

        Args:
            tag_data (Dict[str, Any]): A dictionary containing:
                - "tag_type" (str): The type of the tag.
                - "attributes" (Dict[str, str]): A dictionary of attribute name-value pairs.
                - "position" (int): The position of the tag.
                - "text" (str): The content enclosed within the tag.
                - "uuid" (str): The unique identifier for the tag.
                - "id_name" (str): The name of the ID attribute of the tag.
                - "references" (Dict[str, ITagModel]): A dictionary mapping attribute names to referenced tags.
        """
        super().__init__()
        self._tag_data = tag_data
        self._incoming_references_count = 0

    def increment_reference_count(self) -> None:
        """
        Increments the count of incoming references to this tag.

        This method should be called whenever another tag starts referencing this tag.
        """
        self._incoming_references_count += 1

    def decrement_reference_count(self) -> None:
        """
        Decrements the count of incoming references to this tag.

        This method should be called whenever a referencing tag is removed.
        It ensures that the reference count never goes below zero.

        Raises:
            ValueError: If an attempt is made to decrement the reference count below zero.
        """
        if self._incoming_references_count - 1 < 0:
            raise ValueError(
                "Cannot decrement reference count below zero. This tag is not referenced by any other tag.")

        self._incoming_references_count -= 1

    def is_deletion_prohibited(self) -> bool:
        """
        Determines whether the tag is protected from deletion due to incoming references.

        Returns:
            bool: True if the tag has incoming references and cannot be deleted, False otherwise.
        """
        return self._incoming_references_count > 0

    def get_uuid(self) -> str:
        """
        Retrieves the UUID of the tag.

        Returns:
            str: The unique identifier of the tag.
        """
        return self._tag_data.get("uuid", "")

    def set_uuid(self, uuid: str) -> None:
        """
        Sets the UUID of the tag.

        Args:
            uuid (str): The new UUID to assign to the tag.
        """
        self._tag_data["uuid"] = uuid

    def get_attributes(self, keys: List[str] = None) -> Dict[str, str]:
        """
        Retrieves attributes based on the provided keys or returns all attributes.

        Args:
            keys (Optional[List[str]]): A list of attribute keys to retrieve.
                                        If None, all attributes are returned.

        Returns:
            Dict[str, str]: A dictionary containing the requested attributes or all attributes.
        """
        attributes = self._tag_data.get("attributes", {})
        return attributes if keys is None else {key: attributes[key] for key in keys if key in attributes}

    def set_attributes(self, new_attributes: List[Tuple[str, str]]) -> None:
        """
        Updates the attributes dictionary with the provided key-value pairs.

        Args:
            new_attributes (List[Tuple[str, str]]): A list of key-value pairs to update in the attributes dictionary.
        """
        self._tag_data["attributes"].update(
            {key: value for key, value in new_attributes})

    def get_tag_type(self) -> str:
        """
        Retrieves the type of the tag.

        Returns:
            str: The type of the tag.
        """
        return self._tag_data.get("tag_type", "")

    def set_tag_type(self, tag_type: str) -> None:
        """
        Sets the type of the tag.

        Args:
            tag_type (str): The new tag type to set.
        """
        self._tag_data["tag_type"] = tag_type

    def get_position(self) -> int:
        """
        Retrieves the position of the tag.

        Returns:
            int: The position of the tag in the text.
        """
        return self._tag_data.get("position", 0)

    def set_position(self, position: int) -> None:
        """
        Sets the position of the tag.

        Args:
            position (int): The new position of the tag in the text.
        """
        self._tag_data["position"] = position

    def get_text(self) -> str:
        """
        Retrieves the text associated with the tag.

        Returns:
            str: The text associated with the tag.
        """
        return self._tag_data.get("text", "")

    def set_text(self, text: str) -> None:
        """
        Sets the text associated with the tag.

        Args:
            text (str): The new text to associate with the tag.
        """
        self._tag_data["text"] = text

    def get_id(self) -> str:
        """
        Retrieves the ID of the tag from the attributes.

        Returns:
            str: The ID of the tag, if present in the attributes. Otherwise, an empty string.
        """
        return self._tag_data.get("attributes", {}).get("id", "")

    def set_id(self, new_id: str) -> None:
        """
        Sets the ID of the tag in the attributes.

        Args:
            new_id (str): The new ID to set for the tag.
        """
        self._tag_data["attributes"]["id"] = new_id

    def get_id_name(self) -> str:
        """
        Retrieves the name of the ID attribute of the tag.

        Returns:
            str: The name of the ID attribute.
        """
        return self._tag_data.get("id_name", "")

    def set_id_name(self, new_id_name: str) -> None:
        """
        Sets the name of the ID attribute of the tag.

        Args:
            new_id_name (str): The new ID attribute name.
        """
        self._tag_data["id_name"] = new_id_name

    def get_references(self) -> Dict[str, ITagModel]:
        """
        Retrieves the mapping of ID reference attributes to their corresponding tag UUIDs.

        Returns:
            Dict[str, str]: A dictionary mapping attribute names to referenced tag UUIDs.
        """
        return self._tag_data.get("references", {})

    def set_references(self, references: Dict[str, str]) -> None:
        """
        Sets the mapping of ID reference attributes to their corresponding tag UUIDs.

        Args:
            references (Dict[str, str]): A dictionary mapping attribute names to referenced tag UUIDs.
        """
        self._tag_data["references"] = references

    def get_tag_data(self) -> Dict[str, Any]:
        """
        Retrieves the tag data as a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "tag_type" (str): The type of the tag.
                - "attributes" (Dict[str, str]): A dictionary of attribute name-value pairs.
                - "position" (int): The position of the tag in the text.
                - "text" (str): The content enclosed within the tag.
                - "uuid" (str): The unique identifier for the tag.
                - "id_name" (str): The name of the ID attribute.
                - "references" (Dict[str, ITagModel]): A dictionary mapping attribute names to referenced tags.
        """
        return self._tag_data

    def __str__(self) -> str:
        """
        Returns a string representation of the tag as it would appear in the text.

        The string includes the tag type, all attributes, and the associated text.

        Returns:
            str: A string representation of the tag in the format:
                <tag_type attr1="value1" attr2="value2">text</tag_type>
        """
        attributes = self._tag_data.get("attributes", {})
        attributes_str = (
            f'{self._tag_data["id_name"]}="{attributes["id"]}"'if "id" in attributes else "")
        attributes_str += " ".join(f'{key}="{value}"' for key,
                                   value in attributes.items() if key != "id")

        return f'<{self._tag_data["tag_type"]} {attributes_str}>{self._tag_data["text"]}</{self._tag_data["tag_type"]}>'
