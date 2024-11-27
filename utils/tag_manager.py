from typing import Dict, List
import uuid
from model.interfaces import IDocumentModel, ITagModel


class TagManager:
    """
    A class responsible for managing tags, including adding, editing,
    retrieving, and deleting tags for a specific document.
    """

    def __init__(self, document: IDocumentModel) -> None:
        """
        Initializes the TagManager with an internal tag list and a reference to the document.

        Args:
            document (IDocumentModel): The document associated with this TagManager.
        """
        self._document = document  # Reference to the associated document
        self._tags: Dict[str, ITagModel] = {}  # Internal storage for tags
        self._load_tags_from_document()  # Load existing tags from the document

    def _load_tags_from_document(self) -> None:
        """
        Loads existing tags from the associated document into the TagManager.
        """
        # TODO: Implement the logic to extract tags from the document model
        # and populate self._tags. Ensure consistency with the ITagModel type.
        existing_tags = self._document.get_existing_tags()  # Placeholder for actual method
        for tag in existing_tags:
            # Use getter to access the UUID of each tag
            self._tags[tag.get_uuid()] = tag

    def _generate_unique_id(self) -> str:
        """
        Generates a globally unique identifier (UUID).

        Returns:
            str: The newly generated unique ID as a string.
        """
        return str(uuid.uuid4())

    def add_tag(self, tag_data: ITagModel) -> str:
        """
        Adds a new tag and returns its unique UUID.

        Args:
            tag_data (ITagModel): The data for the tag to be added.

        Returns:
            str: The unique UUID of the newly added tag.
        """
        # Generate a unique UUID for the tag
        tag_uuid = self._generate_unique_id()

        # TODO: Validate the tag_data if needed to ensure it conforms to ITagModel
        self._tags[tag_uuid] = tag_data

        # TODO: Update the document model with the new tag if required
        self._document.add_tag(tag_data)

        return tag_uuid

    def edit_tag(self, tag_uuid: str, tag_data: ITagModel) -> None:
        """
        Edits an existing tag identified by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to edit.
            tag_data (ITagModel): The new data for the tag.
        """
        if tag_uuid in self._tags:
            # TODO: Perform validation if needed before updating
            self._tags[tag_uuid] = tag_data

            # TODO: Synchronize the changes with the document model
            self._document.update_tag(tag_data)
        else:
            raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def delete_tag(self, tag_uuid: str) -> None:
        """
        Deletes a tag identified by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to delete.
        """
        if tag_uuid in self._tags:
            # TODO: Remove the tag from the document model if required
            self._document.remove_tag(tag_uuid)

            del self._tags[tag_uuid]
        else:
            raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def get_tag(self, tag_uuid: str) -> ITagModel:
        """
        Retrieves the data of a tag by its unique UUID.

        Args:
            tag_uuid (str): The unique UUID of the tag to retrieve.

        Returns:
            ITagModel: The data associated with the tag.
        """
        if tag_uuid in self._tags:
            return self._tags[tag_uuid]
        else:
            raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

    def get_all_tags(self) -> List[ITagModel]:
        """
        Returns a list of all tags managed by this TagManager.

        Returns:
            List[ITagModel]: A list of all tag data.
        """
        return list(self._tags.values())
