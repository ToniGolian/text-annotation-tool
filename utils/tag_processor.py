import re
from typing import List, Dict

from utils.interfaces import ITagProcessor


class TagProcessor(ITagProcessor):
    """
    Handles the transformation of tag objects to strings and vice versa,
    and performs string operations on the document text.
    """

    def tags_to_strings(self, tags: List[Dict]) -> List[str]:
        """
        Converts tag objects into their string representations.

        Args:
            tags (List[Dict]): A list of tag dictionaries.

        Returns:
            List[str]: A list of string representations of the tags.
        """
        # TODO: Implement logic for tag-to-string conversion
        return [f"<tag name='{tag['name']}' color='{tag['color']}'>" for tag in tags]

    def insert_tag_into_text(self, text: str, tag_data: Dict) -> str:
        """
        Inserts a single tag as a string into the specified text.

        Args:
            text (str): The document text where the tag should be inserted.
            tag_data (Dict): A dictionary containing the tag data to insert. Expected keys:
                - "position" (int): The index in the text where the tag should be inserted.
                - "text" (str): The text content of the tag.
                - "tag_type" (str): The type of the tag.
                - "attributes" (List[Tuple[str, str]]): A list of attribute name-value pairs for the tag.

        Returns:
            str: The updated text with the tag inserted at the specified position.

        Raises:
            ValueError: If the text at the specified position does not match tag_data["text"].
        """
        position = tag_data["position"]
        tag_text = tag_data["text"]
        tag_type = tag_data["tag_type"]
        attributes = tag_data.get("attributes", [])

        # Validate if the text at the position matches the tag text
        if text[position:position + len(tag_text)] != tag_text:
            raise ValueError(
                f"Text at position {position} does not match the provided tag text.")

        # Construct the opening tag with attributes
        attributes_str = " ".join(
            f'{key}="{value}"' for key, value in attributes)
        opening_tag = f"<{tag_type} {attributes_str}>" if attributes else f"<{tag_type}>"

        # Construct the full tag
        full_tag = f"{opening_tag}{tag_text}</{tag_type}>"

        # Replace the original text with the tag at the specified position
        updated_text = text[:position] + full_tag + \
            text[position + len(tag_text):]

        return updated_text

    def update_id(self, text: str, position: int, new_id: int) -> str:
        """
        Updates the ID attribute of a tag at the specified position in the text using regex.

        Args:
            text (str): The full document text containing the tag.
            position (int): The position in the text where the tag starts.
            new_id (int): The new ID to replace the existing ID.

        Returns:
            str: The updated text with the new ID.

        Raises:
            ValueError: If no valid ID attribute is found at the specified position.
        """
        # Define a regex pattern to match a tag with an attribute ending in 'id' and a numeric value in quotes
        pattern = r'<[^>]*\b(\w*id)="(\d+)"[^>]*>'

        # Use regex to find the tag starting at or after the given position
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
        Extracts tag information from the text.

        Args:
            text (str): The document text.

        Returns:
            List[Dict]: A list of extracted tag dictionaries.
        """
        # TODO: Implement logic to parse text and extract tags
        return []
