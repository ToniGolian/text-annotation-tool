import re
from typing import List, Dict

from model.interfaces import ITagModel
from utils.interfaces import ITagProcessor


class TagProcessor(ITagProcessor):
    """
    Handles the transformation of tag objects to strings and vice versa,
    and performs string operations on the document text.
    """

    def tag_data_to_string(self, tag_data: Dict) -> str:
        """
        Converts tag object into it's string representation.

        Args:
            tag_data (Dict): A dictionary containing the tag data to insert. Expected keys:
                - "position" (int): The index in the text where the tag should be inserted.
                - "text" (str): The text content of the tag.
                - "tag_type" (str): The type of the tag.
                - "attributes" (List[Tuple[str, str]]): A list of attribute name-value pairs for the tag.

        Returns:
            str: The string representation of the tag.
        """
        tag_text = tag_data["text"]
        tag_type = tag_data["tag_type"]
        attributes = tag_data.get("attributes", [])

        # Construct the opening tag with attributes
        attributes_str = " ".join(
            f'{key}="{value}"' for key, value in attributes)
        opening_tag = f"<{tag_type} {attributes_str}>" if attributes else f"<{tag_type}>"

        # Construct the full tag
        full_tag = f"{opening_tag}{tag_text}</{tag_type}>"
        return full_tag

    def insert_tag_into_text(self, text: str, tag_model: ITagModel) -> str:
        """
        Inserts a single tag as a string into the specified text using an ITagModel instance.

        Args:
            text (str): The document text where the tag should be inserted.
            tag_model (ITagModel): An instance of ITagModel containing the tag data to insert.
                Required properties:
                    - position (int): The index in the text where the tag should be inserted.
                    - text (str): The text content of the tag.
                    - tag_type (str): The type of the tag.
                    - attributes (Dict[str, str]): A dictionary of attribute name-value pairs for the tag.

        Returns:
            str: The updated text with the tag inserted at the specified position.

        Raises:
            ValueError: If the text at the specified position does not match the tag's text.
        """
        position = tag_model.get_position()
        tag_text = tag_model.get_text()

        # Validate if the text at the position matches the tag text
        if text[position:position + len(tag_text)] != tag_text:
            raise ValueError(
                f"Text at position {position} does not match the provided tag text.")

        # Convert the tag to a string representation
        full_tag = str(tag_model)

        # Replace the original text with the tag at the specified position
        updated_text = text[:position] + full_tag + \
            text[position + len(tag_text):]

        return updated_text

    def delete_tag_from_text(self, tag: ITagModel, text: str) -> str:
        """
        Removes a tag from the specified text based on the provided ITagModel instance.

        Args:
            tag (ITagModel): An instance of ITagModel representing the tag to remove.
            text (str): The document text containing the tag.

        Returns:
            str: The updated text with the specified tag removed.

        Raises:
            ValueError: If the specified tag is not found in the text.
        """
        tag_str = str(tag)  # Convert the tag to its string representation
        position = tag.get_position()

        # Validate if the tag exists at the expected position
        if text[position:position + len(tag_str)] != tag_str:
            raise ValueError(
                f"Tag not found at the specified position: {position}")

        # Remove the tag from the text
        updated_text = text[:position] + \
            tag.get_text() + text[position + len(tag_str):]

        return updated_text

    #!bug here

    def update_id(self, text: str, position: int, new_id: str) -> str:
        """
        Updates the ID attribute of a tag at the specified position in the text using regex.

        Args:
            text (str): The full document text containing the tag.
            position (int): The position in the text where the tag starts.
            new_id (str): The new ID to replace the existing ID.

        Returns:
            str: The updated text with the new ID.

        Raises:
            ValueError: If no valid ID attribute is found at the specified position.
        """
        # Define a regex pattern to match a tag with an attribute ending in 'id' and a numeric value in quotes
        pattern = r'<[^>]*\b(\w*id)="(\w*\d+)"[^>]*>'
        # Now, attempt to match from position onwards
        match = re.search(pattern, text[position:])
        if not match:
            raise ValueError(
                "No valid ID attribute found at the specified position.")

        # Extract the full match, the key (e.g., 'tid'), and the current value
        full_match = match.group(0)
        key = match.group(1)
        current_value = match.group(2)

        # Replace the current value with the new ID
        updated_tag = full_match.replace(
            f'{key}="{current_value}"', f'{key}="{new_id}"')

        # Replace the old tag in the text
        start_index = position + match.start(0)
        end_index = position + match.end(0)
        updated_text = text[:start_index] + updated_tag + text[end_index:]

        return updated_text

    def extract_tags_from_text(self, text: str) -> List[Dict]:
        """
        Extracts all tags from the given text and returns them as a list of dictionaries.

        This method identifies tags in the text based on their XML-like structure, including their type,
        attributes, position, and content. It parses the tag type, attributes, and the inner text of each
        tag, while also recording the start position of each tag in the text.

        Args:
            text (str): The input text containing tags.

        Returns:
            List[Dict]: A list of dictionaries where each dictionary represents a tag with the following keys:
                - "tag_type" (str): The type of the tag (e.g., "TIMEX3").
                - "attributes" (List[Tuple[str, str]]): A list of key-value pairs for the tag's attributes.
                - "position" (int): The starting position of the tag in the text.
                - "text" (str): The content enclosed within the tag.
        """
        tag_pattern = re.compile(
            r'<(?P<tag_type>\w+)\s*(?P<attributes>[^>]*)>(?P<content>.*?)</\1>',
            re.DOTALL
        )
        attribute_pattern = re.compile(r'(?P<key>\w+)="(?P<value>[^"]*)"')

        tags = []
        for match in tag_pattern.finditer(text):
            tag_type = match.group("tag_type")
            attributes_raw = match.group("attributes")
            content = match.group("content")
            start_position = match.start()

            # Parse attributes
            attributes = attribute_pattern.findall(attributes_raw)

            # Construct tag_data
            tag_data = {
                "tag_type": tag_type,
                "attributes": attributes,
                "position": start_position,
                "text": content.strip(),
            }
            tags.append(tag_data)

        return tags
