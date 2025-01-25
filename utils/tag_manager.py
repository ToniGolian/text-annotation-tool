from typing import Dict, List
import uuid
from model.interfaces import IDocumentModel, ITagModel
from model.tag_model import TagModel
from utils.interfaces import ITagProcessor


class TagManager:
    """
    A class responsible for managing tags, including adding, editing,
    retrieving, and deleting tags for a specific document.
    """

    def __init__(self, tag_processor: ITagProcessor) -> None:
        """
        Initializes the TagManager with an internal tag list, a reference to the document,
        and a TagProcessor.

        Args:
            tag_processor (ITagProcessor): The processor for handling string transformations
                                           and text manipulation for tags.
        """
        self._document: IDocumentModel = None
        self._tag_processor: ITagProcessor = tag_processor
        self._tags: List[TagModel] = []

    def _extract_tags_from_document(self) -> None:
        """
        Initializes the TagManager's internal tag list by extracting tag data
        from the associated document text and creating TagModel objects for each tag.
        """
        # Get the document's text
        document_text = self._document.get_text()

        # Use the TagProcessor to extract tag data
        extracted_tag_data = self._tag_processor.extract_tags_from_text(
            document_text)

        # Convert each tag_data dictionary into a TagModel object
        for tag_data in extracted_tag_data:
            # Assign a unique UUID to the tag_data
            tag_uuid = self._generate_unique_id()
            tag_data["uuid"] = tag_uuid

            # Create a TagModel instance using the tag_data
            tag = TagModel(**tag_data)

            # Add the TagModel to the internal list
            self._tags.append(tag)

        # Ensure the tags are sorted by position
        self._tags.sort(key=lambda tag: tag.get_position())

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
        new_tag = TagModel(**tag_data)

        # Insert the tag directly into the sorted position
        for index, tag in enumerate(self._tags):
            if new_tag.get_position() < tag.get_position():
                self._tags.insert(index, new_tag)
                break
        else:
            # If no earlier position is found, append at the end
            self._tags.append(new_tag)

        # Insert the tag into the text using the TagProcessor
        text = self._document.get_text()
        updated_text = self._tag_processor.insert_tag_into_text(text, new_tag)
        self._document.set_text(updated_text)

        self._update_ids(new_tag)
        return tag_uuid

    def edit_tag(self, tag_uuid: str, tag_data: Dict) -> None:
        """
        Edits an existing tag identified by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to edit.
            tag_data (Dict): The new data for the tag.
        """
        for index, tag in enumerate(self._tags):
            if tag.get_uuid() == tag_uuid:
                updated_tag = TagModel(**tag_data)
                self._tags[index] = updated_tag

                # Remove tag in text
                self._tag_processor.delete_tag_from_text(uuid)
                # Update the tag in the text using the TagProcessor
                text = self._document.get_text()
                updated_text = self._tag_processor.insert_tag_into_text(
                    text, tag_data)
                self._document.set_text(updated_text)
                return

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def delete_tag(self, tag_uuid: str) -> None:
        """
        Deletes a tag identified by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to delete.
        """
        for index, tag in enumerate(self._tags):
            if tag.get_uuid() == tag_uuid:
                del self._tags[index]
                self._update_ids(tag)
                # Remove the tag from the text using the TagProcessor
                text = self._document.get_text()
                updated_text = self._tag_processor.delete_tag_from_text(
                    tag, text)
                self._document.set_text(updated_text)

                return

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def _update_ids(self, updated_tag: ITagModel, offset: int = 0) -> None:
        """
        Updates the IDs of all tags of the same type as the provided tag,
        ensuring they are sequentially numbered starting from 1.
        Adjusts the positions based on the length difference between old and new IDs.

        Args:
            updated_tag (ITagModel): The tag that triggered the update.
            offset (int): The initial offset to adjust positions. Default is 0.
        """
        tag_type = updated_tag.get_tag_type()
        text = self._document.get_text()
        current_id = 1

        for tag in self._tags:
            # Adjust the position with the current offset
            tag.set_position(tag.get_position() + offset)

            if tag.get_tag_type() == tag_type:
                old_id = tag.get_id() or "0"  # Get the old ID, default to "0" if none exists
                new_id = str(current_id)  # Generate the new sequential ID

                # Update the tag's ID in the model
                tag.set_id(new_id)

                # Notify the tag processor about the ID update in the text
                text = self._tag_processor.update_id(
                    text=text, position=tag.get_position(), new_id=int(new_id)
                )

                # Calculate the length difference between old and new ID
                old_id_length = len(str(old_id))
                new_id_length = len(new_id)
                length_difference = new_id_length - old_id_length

                # Adjust the offset based on the length difference
                offset += length_difference

                current_id += 1

        # Update the document's text after processing all tags
        self._document.set_text(text)

    def get_tag_data(self, tag_uuid: str) -> Dict:
        """
        Retrieves the data of a tag by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to retrieve.

        Returns:
            Dict: The data associated with the tag.
        """
        for tag in self._tags:
            if tag.get_uuid() == tag_uuid:
                return {
                    "uuid": tag.get_uuid(),
                    "tag_type": tag.get_tag_type(),
                    "attributes": tag.get_attributes(),
                    "position": tag.get_position()
                }

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def get_all_tags(self) -> List[Dict]:
        """
        Returns a list of all tags managed by this TagManager.

        Returns:
            List[Dict]: A list of all tag data in dictionary format.
        """
        return [
            {
                "uuid": tag.get_uuid(),
                "tag_type": tag.get_tag_type(),
                "attributes": tag.get_attributes(),
                "position": tag.get_position()
            }
            for tag in self._tags
        ]

    def set_document(self, document: IDocumentModel) -> None:
        """
        Associates a document with the TagManager and initializes the tag list.

        Args:
            document (IDocumentModel): The document to be managed by this TagManager.
        """
        self._document = document
        self._tags.clear()
        self._extract_tags_from_document()
