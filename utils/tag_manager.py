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
        self._tag_processor: ITagProcessor = tag_processor

    def _extract_tags_from_document(self, target_model: IDocumentModel) -> None:
        """
        Extracts tags from the document text and stores them in the target model.

        This method processes the document text, identifies tag structures, and 
        creates corresponding `TagModel` objects. The extracted tags are then 
        assigned to the target model in a sorted order.

        Args:
            target_model (IDocumentModel): The document model containing the text 
                                           from which tags will be extracted.
        """

        # Get the document's text
        document_text = target_model.get_text()

        # Use the TagProcessor to extract tag data
        extracted_tag_data = self._tag_processor.extract_tags_from_text(
            document_text)

        tags = []
        # Convert each tag_data dictionary into a TagModel object
        for tag_data in extracted_tag_data:
            # Assign a unique UUID to the tag_data
            tag_uuid = self._generate_unique_id()
            tag_data["uuid"] = tag_uuid

            # Create a TagModel instance using the tag_data
            tag = TagModel(**tag_data)

            # Add the TagModel to the internal list
            tags.append(tag)

        # Ensure the tags are sorted by position
        tags.sort(key=lambda tag: tag.get_position())

        target_model.set_tags(tags)

    def _generate_unique_id(self) -> str:
        """
        Generates a globally unique identifier (UUID).

        Returns:
            str: The newly generated unique ID as a string.
        """
        return str(uuid.uuid4())

    def add_tag(self, tag_data: Dict, target_model: IDocumentModel) -> str:
        """
        Adds a new tag to the document and updates the model accordingly.

        This method creates a new tag with a unique UUID, inserts it into the 
        correct position within the document model, updates tag positions, 
        and modifies the document text to reflect the change.

        Args:
            tag_data (Dict): The data defining the tag attributes.
            target_model (IDocumentModel): The document model where the tag is added.

        Returns:
            str: The UUID of the newly created tag.
        """
        # Generate a unique UUID for the tag
        tag_uuid = self._generate_unique_id()
        tag_data["uuid"] = tag_uuid
        new_tag = TagModel(**tag_data)

        # Get tags from current model
        tags = target_model.get_tags()
        # Insert the tag into the sorted position
        for index, tag in enumerate(tags):
            if new_tag.get_position() < tag.get_position():
                tags.insert(index, new_tag)
                break
        else:
            tags.append(new_tag)
        target_model.set_tags(tags)

        # Get the current document text
        text = target_model.get_text()

        # Insert the new tag into the text
        updated_text = self._tag_processor.insert_tag_into_text(text, new_tag)
        offset = len(str(new_tag))-len(str(new_tag.get_text()))
        self._update_positions(
            start_position=new_tag.get_position(), offset=offset, target_model=target_model)

        # Update IDs and adjust text
        updated_text = self._update_ids(
            new_tag=new_tag, target_model=target_model, text=updated_text)

        # Apply final text update after all modifications
        target_model.set_text(updated_text)

        return tag_uuid

    def edit_tag(self, tag_uuid: str, tag_data: Dict, target_model: IDocumentModel) -> None:
        """
        Updates an existing tag with new data and applies the changes to the model.

        This method replaces the tag identified by `tag_uuid` with updated attributes, 
        modifies the document text accordingly, and ensures the positions and IDs 
        of all tags remain consistent.

        Args:
            tag_uuid (str): The UUID of the tag to be modified.
            tag_data (Dict): The new attributes and values for the tag.
            target_model (IDocumentModel): The document model containing the tag.

        Raises:
            ValueError: If the tag with the given UUID does not exist.
        """
        # Get tags from current model
        tags = target_model.get_tags()
        for index, tag in enumerate(tags):
            if tag.get_uuid() == tag_uuid:
                old_tag = tags[index]
                updated_tag = TagModel(**tag_data)
                tags[index] = updated_tag
                target_model.set_tags(tags)

                # Get the current document text
                text = target_model.get_text()

                # Remove the old tag from the text
                text = self._tag_processor.delete_tag_from_text(old_tag, text)

                # Insert the updated tag into the text
                text = self._tag_processor.insert_tag_into_text(
                    text, updated_tag)

                # Update positions of subsequent tags
                offset = len(updated_tag)-len(old_tag)
                self._update_positions(
                    updated_tag.get_position(), offset=offset, target_model=target_model)

                # Update IDs and adjust text
                text = self._update_ids(updated_tag, text)

                # Apply final text update after all modifications
                target_model.set_text(text)
                return

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def delete_tag(self, tag_uuid: str, target_model: IDocumentModel) -> None:
        """
        Removes a tag from the document and updates the model.

        This method locates the tag with the specified UUID, deletes it from 
        the document model, adjusts tag positions, and ensures correct ID sequencing.

        Args:
            tag_uuid (str): The UUID of the tag to be removed.
            target_model (IDocumentModel): The document model containing the tag.

        Raises:
            ValueError: If the tag with the given UUID does not exist.
        """
        # Get tags from current model
        tags = target_model.get_tags()
        for index, tag in enumerate(tags):
            if tag.get_uuid() == tag_uuid:
                del tags[index]
                target_model.set_tags(tags)

                # Get the current document text
                text = target_model.get_text()

                # Remove the tag from the text
                text = self._tag_processor.delete_tag_from_text(tag, text)

                # Update positions of subsequent tags
                offset = len(str(tag.get_text()))-len(str(tag))
                self._update_positions(
                    start_position=tag.get_position(), offset=offset, target_model=target_model)

                # Update IDs and adjust text
                text = self._update_ids(
                    new_tag=tag, text=text, target_model=target_model)

                # Apply final text update after all modifications
                target_model.set_text(text)
                return

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def _update_ids(self, new_tag: ITagModel, target_model: IDocumentModel, text: str, offset: int = 0) -> str:
        """
        Updates tag IDs sequentially and adjusts positions in the text.

        Ensures all tags of the same type as `new_tag` are renumbered sequentially, 
        modifying the document text accordingly. Position offsets are updated 
        dynamically to maintain text integrity.

        Args:
            new_tag (ITagModel): The tag that triggered the ID update.
            target_model (IDocumentModel): The document model containing the tags.
            text (str): The document text to be updated.
            offset (int): The initial position adjustment factor.

        Returns:
            str: The updated document text reflecting the new tag IDs.
        """
        # Get tags from current model
        tags = target_model.get_tags()
        tag_type = new_tag.get_tag_type()
        current_id = 1

        for tag in tags:
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

        target_model.set_tags(tags)
        return text

    def _update_positions(self, start_position: int, offset: int, target_model: IDocumentModel) -> None:
        """
        Adjusts the positions of tags after modifications in the document.

        This method updates the position of all tags occurring after the given 
        `start_position`, ensuring they shift appropriately based on the applied `offset`.

        Args:
            start_position (int): The position from which updates should be applied.
            offset (int): The number of characters by which to shift subsequent tags.
            target_model (IDocumentModel): The document model containing the tags.
        """
        # Get tags from current model
        tags = target_model.get_tags()
        for tag in tags:
            tag_position = tag.get_position()
            if tag_position > start_position:
                tag.set_position(tag_position + offset)
        target_model.set_tags(tags)

    def get_tag_data(self, tag_uuid: str, target_model: IDocumentModel) -> Dict:
        """
        Retrieves the details of a tag by its UUID.

        Args:
            tag_uuid (str): The UUID of the tag to retrieve.
            target_model (IDocumentModel): The document model containing the tag.

        Returns:
            Dict: The attributes and metadata of the specified tag.

        Raises:
            ValueError: If the tag with the given UUID does not exist.
        """
        # Get tags from current model
        tags = target_model.get_tags()
        for tag in tags:
            if tag.get_uuid() == tag_uuid:
                return {
                    "uuid": tag.get_uuid(),
                    "tag_type": tag.get_tag_type(),
                    "attributes": tag.get_attributes(),
                    "position": tag.get_position()
                }

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def get_all_tags(self, target_model: IDocumentModel) -> List[Dict]:
        """
        Retrieves all tags in the document model.

        Args:
            target_model (IDocumentModel): The document model from which tags are retrieved.

        Returns:
            List[Dict]: A list of dictionaries, each containing data about a tag.
        """
        return [
            {
                "uuid": tag.get_uuid(),
                "tag_type": tag.get_tag_type(),
                "attributes": tag.get_attributes(),
                "position": tag.get_position()
            }
            for tag in target_model.get_tags()
        ]

    def get_highlight_data(self, target_model: IDocumentModel) -> List[Tuple[str, int, int]]:
        """
        Retrieves highlight data for tagged elements in the document.

        Constructs a list of tuples containing tag type, start position, and 
        end position to facilitate text highlighting.

        Args:
            target_model (IDocumentModel): The document model containing the tags.

        Returns:
            List[Tuple[str, int, int]]: A list of tuples where:
                - The first element (str) is the tag type.
                - The second element (int) is the start position of the tag.
                - The third element (int) is the end position of the tag.
        """
        return [(tag.get_tag_type(), tag.get_position(), tag.get_position()+len(str(tag))) for tag in target_model.get_tags()]
