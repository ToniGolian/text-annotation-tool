from typing import Dict, List
import uuid
from model.interfaces import IDocumentModel
from model.tag_model import TagModel
from utils.interfaces import ITagStringProcessor


class TagManager:
    """
    A class responsible for managing tags, including adding, editing,
    retrieving, and deleting tags for a specific document.
    """

    def __init__(self, document: IDocumentModel, tag_processor: ITagStringProcessor) -> None:
        """
        Initializes the TagManager with an internal tag list, a reference to the document,
        and a TagStringProcessor.

        Args:
            document (IDocumentModel): The document associated with this TagManager.
            tag_processor (ITagStringProcessor): The processor for handling string transformations
                                                 and text manipulation for tags.
        """
        self._document = document
        self._tag_processor = tag_processor
        self._tags: Dict[str, Dict] = {}
        self._extract_tags_from_document()

    def _extract_tags_from_document(self) -> None:
        """
        Initializes the TagManager's internal tag list by extracting tag data 
        from the associated document text and creating TagModel objects for each tag.
        """
        # Get the document's text
        document_text = self._document.get_text()

        # Use the TagStringProcessor to extract tag data (without UUIDs)
        extracted_tag_data = self._tag_processor.extract_tags_from_text(
            document_text)

        # Convert each tag_data dictionary into a TagModel object
        for tag_data in extracted_tag_data:
            # Assign a unique UUID to the tag_data
            tag_uuid = self._generate_unique_id()
            tag_data["uuid"] = tag_uuid

            # Create a TagModel instance using the tag_data
            tag = TagModel(**tag_data)

            # Add the TagModel to the internal dictionary
            self._tags[tag_uuid] = tag

    def _generate_unique_id(self) -> str:
        """
        Generates a globally unique identifier (UUID).

        Returns:
            str: The newly generated unique ID as a string.
        """
        return str(uuid.uuid4())

    def add_tag(self, tag_data: Dict) -> str:
        """
        Adds a new tag and returns its unique UUID.

        Args:
            tag_data (Dict): The data for the tag to be added.

        Returns:
            str: The unique UUID of the newly added tag.
        """
        # Generate a unique UUID for the tag
        tag_uuid = self._generate_unique_id()
        tag_data["uuid"] = tag_uuid
        self._tags[tag_uuid] = TagModel(**tag_data)

        # Insert the tag into the text using the TagStringProcessor
        text = self._document.get_text()
        # TODO change logic
        updated_text = self._tag_processor.insert_tags_into_text(text, [
                                                                 tag_data])
        self._document.set_text(updated_text)

        return tag_uuid

    def edit_tag(self, tag_uuid: str, tag_data: Dict) -> None:
        """
        Edits an existing tag identified by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to edit.
            tag_data (Dict): The new data for the tag.
        """
        if tag_uuid in self._tags:
            tag_data["uuid"] = tag_uuid  # Ensure UUID consistency
            self._tags[tag_uuid] = tag_data

            # Update the tag in the text using the TagStringProcessor
            text = self._document.get_text()
            updated_text = self._tag_processor.insert_tag_into_text(
                text, tag_data)
            self._document.set_text(updated_text)

        else:
            raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def delete_tag(self, tag_uuid: str) -> None:
        """
        Deletes a tag identified by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to delete.
        """
        if tag_uuid in self._tags:
            # Remove the tag from the text using the TagStringProcessor
            text = self._document.get_text()
            updated_text = self._tag_processor.insert_tags_into_text(text, [])
            self._document.set_text(updated_text)

            del self._tags[tag_uuid]
        else:
            raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def get_tag_data(self, tag_uuid: str) -> Dict:
        """
        Retrieves the data of a tag by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to retrieve.

        Returns:
            Dict: The data associated with the tag.
        """
        if tag_uuid in self._tags:
            return self._tags[tag_uuid]
        else:
            raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def get_all_tags(self) -> List[Dict]:
        """
        Returns a list of all tags managed by this TagManager.

        Returns:
            List[Dict]: A list of all tag data in dictionary format.
        """
        return list(self._tags.values())
