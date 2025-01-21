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

        print(f"{text[position:position + len(tag_text)]=}")
        print(f"{tag_text=}")

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
