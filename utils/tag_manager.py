from typing import Dict, List, Tuple
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
        self._document_model: IDocumentModel = None
        self._tag_processor: ITagProcessor = tag_processor
        self._tags: List[TagModel] = []

    def _extract_tags_from_document(self) -> None:
        """
        Initializes the TagManager's internal tag list by extracting tag data
        from the associated document text and creating TagModel objects for each tag.
        """
        # Get the document's text
        document_text = self._document_model.get_text()

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

    # def add_tag(self, tag_data: Dict) -> str:
    #     """
    #     Adds a new tag and returns its unique UUID.

    #     Args:
    #         tag_data (Dict): The data for the tag to be added.

    #     Returns:
    #         str: The unique UUID of the newly added tag.
    #     """
    #     # Generate a unique UUID for the tag
    #     tag_uuid = self._generate_unique_id()
    #     tag_data["uuid"] = tag_uuid
    #     new_tag = TagModel(**tag_data)

    #     # Insert the tag directly into the sorted position
    #     for index, tag in enumerate(self._tags):
    #         if new_tag.get_position() < tag.get_position():
    #             self._tags.insert(index, new_tag)
    #             break
    #     else:
    #         # If no earlier position is found, append at the end
    #         self._tags.append(new_tag)

    #     # Insert the tag into the text using the TagProcessor
    #     text = self._document_model.get_text()
    #     updated_text = self._tag_processor.insert_tag_into_text(text, new_tag)
    #     self._document_model.set_text(updated_text)

    #     self._update_ids(new_tag)
    #     return tag_uuid

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

        # Insert the tag into the sorted position
        for index, tag in enumerate(self._tags):
            if new_tag.get_position() < tag.get_position():
                self._tags.insert(index, new_tag)
                break
        else:
            self._tags.append(new_tag)

        # Get the current document text
        text = self._document_model.get_text()

        # Insert the new tag into the text
        updated_text = self._tag_processor.insert_tag_into_text(text, new_tag)
        offset = len(str(new_tag))-len(str(new_tag.get_text()))
        self._update_positions(
            start_position=new_tag.get_position(), offset=offset)

        # Update IDs and adjust text
        updated_text = self._update_ids(new_tag, updated_text)

        # Apply final text update after all modifications
        self._document_model.set_text(updated_text)

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
                old_tag = self._tags[index]
                updated_tag = TagModel(**tag_data)
                self._tags[index] = updated_tag

                # Get the current document text
                text = self._document_model.get_text()

                # Remove the old tag from the text
                text = self._tag_processor.delete_tag_from_text(old_tag, text)

                # Insert the updated tag into the text
                text = self._tag_processor.insert_tag_into_text(
                    text, updated_tag)

                # Update positions of subsequent tags
                offset = len(updated_tag)-len(old_tag)
                self._update_positions(
                    updated_tag.get_position(), offset=offset)

                # Update IDs and adjust text
                text = self._update_ids(updated_tag, text)

                # Apply final text update after all modifications
                self._document_model.set_text(text)
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

                # Get the current document text
                text = self._document_model.get_text()

                # Remove the tag from the text
                text = self._tag_processor.delete_tag_from_text(tag, text)

                # Update positions of subsequent tags
                offset = len(str(tag.get_text()))-len(str(tag))
                self._update_positions(
                    start_position=tag.get_position(), offset=offset)

                # Update IDs and adjust text
                text = self._update_ids(tag, text)

                # Apply final text update after all modifications
                self._document_model.set_text(text)
                return

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def _update_ids(self, new_tag: ITagModel, text: str, offset: int = 0) -> str:
        """
        Updates the IDs of all tags of the same type as the provided tag,
        ensuring they are sequentially numbered starting from 1.
        Adjusts the positions based on the length difference between old and new IDs.

        Args:
            updated_tag (ITagModel): The tag that triggered the update.
            text (str): The document text being updated.
            offset (int): The initial offset to adjust positions. Default is 0.

        Returns:
            str: The updated document text with correct tag IDs.
        """
        tag_type = new_tag.get_tag_type()
        current_id = 1

        for tag in self._tags:
            # Adjust the position with the current offset
            tag.set_position(tag.get_position() + offset)

            if tag.get_tag_type() == tag_type:
                old_id = tag.get_id() or "0"  # Default to "0" if no ID exists
                new_id = str(current_id)  # Generate the new sequential ID

                # Update the tag's ID in the model
                tag.set_id(new_id)

                # Notify the tag processor about the ID update in the text
                text = self._tag_processor.update_id(
                    text=text, position=tag.get_position(), new_id=int(new_id)
                )

                # Adjust the offset based on the length difference between old and new ID
                offset += len(new_id) - len(old_id)

                current_id += 1

        return text  # Return the final updated text

    def _update_positions(self, start_position: int, offset: int) -> None:
        """
        Updates the positions of tags following the given tag in the document.

        If only `new_tag` is provided, it is assumed that a new tag was inserted, 
        causing subsequent tags to shift forward based on the length of the inserted tag.

        If `old_tag` is also provided, it is assumed that an existing tag was edited, 
        and subsequent tags are adjusted based on the difference in length between 
        the old and new tag representations.

        Args:
            new_tag (ITagModel): The new or updated tag whose insertion/editing affects positions.
            old_tag (ITagModel, optional): The previous state of the tag before modification. 
                                        Defaults to None, indicating a newly inserted tag.
        """
        for tag in self._tags:
            tag_position = tag.get_position()
            if tag_position > start_position:
                tag.set_position(tag_position + offset)

    # def _update_ids(self, updated_tag: ITagModel, offset: int = 0) -> None:
    #     """
    #     Updates the IDs of all tags of the same type as the provided tag,
    #     ensuring they are sequentially numbered starting from 1.
    #     Adjusts the positions based on the length difference between old and new IDs.

    #     Args:
    #         updated_tag (ITagModel): The tag that triggered the update.
    #         offset (int): The initial offset to adjust positions. Default is 0.
    #     """
    #     tag_type = updated_tag.get_tag_type()
    #     text = self._document_model.get_text()
    #     current_id = 1

    #     for tag in self._tags:
    #         # Adjust the position with the current offset
    #         tag.set_position(tag.get_position() + offset)

    #         if tag.get_tag_type() == tag_type:
    #             old_id = tag.get_id() or "0"  # Get the old ID, default to "0" if none exists
    #             new_id = str(current_id)  # Generate the new sequential ID

    #             # Update the tag's ID in the model
    #             tag.set_id(new_id)

    #             # Notify the tag processor about the ID update in the text
    #             text = self._tag_processor.update_id(
    #                 text=text, position=tag.get_position(), new_id=int(new_id)
    #             )

    #             # Calculate the length difference between old and new ID
    #             old_id_length = len(str(old_id))
    #             new_id_length = len(new_id)
    #             length_difference = new_id_length - old_id_length

    #             # Adjust the offset based on the length difference
    #             offset += length_difference

    #             current_id += 1

    #     # Update the document's text after processing all tags
    #     self._document_model.set_text(text)

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
        self._document_model = document
        self._tags.clear()
        self._extract_tags_from_document()

    def get_highlight_data(self) -> List[Tuple[str, int, int]]:
        """
        Retrieves highlight data for tagged elements in the document.

        This method constructs a list of tuples representing the highlight information 
        for each tag in the document. Each tuple consists of the tag type and its position 
        in the text.

        Returns:
            List[Tuple[str, int, int]]: A list of tuples where:
                - The first element (str) is the tag type.
                - The second element (int) is the start position of the tag in the text.
                - The third element (int) is the end position of the tag in the text, 
                  calculated as the start position plus the length of the tag's string representation.
        """

        return [(tag.get_tag_type(), tag.get_position(), tag.get_position()+len(str(tag))) for tag in self._tags]
