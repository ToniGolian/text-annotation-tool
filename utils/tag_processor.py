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
            tag_data (Dict): A dictionary containing the tag data to insert.

        Returns:
            str: The updated text with the tag inserted at the specified position.
        """
        # TODO: Implement logic to insert tags into the text
        for tag in tag_data:
            text = text.replace(
                tag["target"], f"<{tag['name']}>{tag['target']}</{tag['name']}>")
        return text

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
