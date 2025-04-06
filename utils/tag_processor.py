import re
from typing import List, Dict

from controller.interfaces import IController
from model.interfaces import ITagModel
from utils.interfaces import ITagProcessor


class TagProcessor(ITagProcessor):
    """
    Handles the transformation of tag objects to strings and vice versa,
    and performs string operations on the document text.
    """

    def __init__(self, controller: IController):
        self._controller: IController = controller

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

    def update_tag(self, text: str, tag: ITagModel) -> str:
        """
        Updates a tag in the text at its specified position by replacing it with the new tag representation.

        This method locates an existing tag in the text at the given position using regex and replaces it with
        the new string representation of the provided tag.

        Args:
            text (str): The full document text containing the tag.
            tag (ITagModel): The updated tag instance that should replace the existing one.

        Returns:
            str: The updated text with the modified tag.

        Raises:
            ValueError: If no valid tag is found at the specified position.
        """
        # Get the tag position in the text
        position = tag.get_position()

        # Regex pattern to find an XML-like tag at the given position
        pattern = r'<\w+\s*[^>]*>.*?</\w+>'

        # Attempt to find a tag starting at or after the given position
        match = re.search(pattern, text[position:])
        if not match:
            raise ValueError(
                f"No valid tag found at the specified position {position}.")

        # Replace the old tag with the new tag string representation
        start_index = position + match.start(0)
        end_index = position + match.end(0)
        updated_text = text[:start_index] + str(tag) + text[end_index:]

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
                - "attributes" (Dict[str, str]): A dictionary mapping attribute names to their values.
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

            id_name = self._controller.get_id_name(tag_type)

            # Parse attributes into a dictionary
            attributes = dict(attribute_pattern.findall(attributes_raw))
            attributes["id"] = attributes.pop(id_name)

            # Construct tag_data
            tag_data = {
                "tag_type": tag_type,
                "attributes": attributes,
                "position": start_position,
                "text": content.strip(),
                "id_name": id_name
            }
            tags.append(tag_data)
        return tags

    def delete_all_tags_from_text(self, text: str) -> str:
        """
        Removes all tags from the given text, replacing them with their enclosed content.

        This method identifies and removes XML-like tags from the text, ensuring that only the content
        between the opening and closing tags remains.

        Args:
            text (str): The input text containing tags.

        Returns:
            str: The text with all tags removed, keeping only the inner content.
        """
        tag_pattern = re.compile(
            r'<(?P<tag_type>\w+)\s*(?P<attributes>[^>]*)>(?P<content>.*?)</\1>',
            re.DOTALL
        )

        return re.sub(tag_pattern, lambda match: match.group("content"), text)

    def remove_ids_from_tags(self, text: str) -> str:
        """
        Removes ID and IDREF attributes from all tags in the given text.

        Args:
            text (str): The input text containing tags.

        Returns:
            str: The text with the tags where ID and IDREF attributes have been removed.
        """
        # Regex pattern to extract tag type, attributes, and content
        tag_pattern = re.compile(
            r'<(?P<tag_type>\w+)\s*(?P<attributes>[^>]*)>(?P<content>.*?)</\1>',
            re.DOTALL
        )
        attribute_pattern = re.compile(r'(?P<key>\w+)="(?P<value>[^"]*)"')

        # Process each tag match
        def clean_tag(match):
            tag_type = match.group("tag_type")
            attributes_raw = match.group("attributes")
            content = match.group("content")

            # Retrieve the attribute names to be removed
            idrefs = self._controller.get_id_refs(tag_type)

            # Parse attributes and remove ID and IDREF attributes
            attributes = attribute_pattern.findall(attributes_raw)
            cleaned_attributes = [
                f'{key}="{value}"' for key, value in attributes if key not in idrefs
            ]

            # Construct the cleaned tag
            cleaned_tag = f'<{tag_type} {" ".join(cleaned_attributes)}>{content}</{tag_type}>'

            return cleaned_tag

        # Substitute tags in the text with cleaned versions
        cleaned_text = tag_pattern.sub(clean_tag, text)

        return cleaned_text
