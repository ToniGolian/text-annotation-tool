from hashlib import md5
import re
from typing import Dict, List, Tuple
import uuid
from controller.interfaces import IController
from model.interfaces import IDocumentModel, ITagModel
from model.tag_model import TagModel
from utils.interfaces import ITagProcessor


class TagManager:
    """
    A class responsible for managing tags, including adding, editing,
    retrieving, and deleting tags for a specific document.
    """

    def __init__(self, controller: IController, tag_processor: ITagProcessor) -> None:
        """
        Initializes the TagManager with a tag processor and a controller reference.

        This class manages tags within a document, allowing for their processing,
        transformation, and interaction with the application via the controller.

        Args:
            tag_processor (ITagProcessor): The processor responsible for handling 
                                            string transformations and text manipulation for tags.
            controller (IController): The application controller that manages interactions 
                                    and state updates related to tags.
        """
        self._tag_processor: ITagProcessor = tag_processor
        self._controller: IController = controller

    def extract_tags_from_document(self, target_model: IDocumentModel) -> None:
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
            tag = TagModel(tag_data)

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
        tag_data.setdefault("uuid", self._generate_unique_id())

        # Set references to the referred objects
        tag_data["references"] = self._resolve_references(
            references=tag_data["references"], target_model=target_model)

        new_tag = TagModel(tag_data)
        tags = target_model.get_tags()
        for index, tag in enumerate(tags):
            if new_tag.get_position() < tag.get_position():
                tags.insert(index, new_tag)
                break
        else:
            tags.append(new_tag)
        target_model.set_tags(tags)

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

        return tag_data["uuid"]

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

        tag_data.setdefault("uuid", tag_uuid)
        self.delete_tag(tag_uuid=tag_uuid, target_model=target_model)
        self.add_tag(tag_data=tag_data, target_model=target_model)
        return

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
                for _, reference in tag.get_references().items():
                    reference.decrement_reference_count()
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

    def _update_ids(self, new_tag: ITagModel, target_model: IDocumentModel, text: str) -> str:
        """
        Updates tag IDs sequentially and adjusts positions in the text.

        Ensures all tags of the same type as `new_tag` are renumbered sequentially, 
        modifying the document text accordingly. Position offsets are updated 
        dynamically to maintain text integrity.

        Args:
            new_tag (ITagModel): The tag that triggered the ID update.
            target_model (IDocumentModel): The document model containing the tags.
            text (str): The document text to be updated.

        Returns:
            str: The updated document text reflecting the new tag IDs.
        """
        # Get tags from current model
        tags = target_model.get_tags()
        tag_type = new_tag.get_tag_type()

        # Udate IDs sequentially
        current_id = 1
        offset = 0
        for tag in tags:
            # Adjust the position with the current offset
            tag.set_position(tag.get_position() + offset)

            if tag.get_tag_type() == tag_type:
                old_id = tag.get_id() or "0"  # Default to "0" if no ID exists
                # Generate the new sequential ID
                new_id = str(current_id)
                # adjust prefix
                match = re.match(r"([a-zA-Z]+)(\d+)", old_id)
                if match:
                    prefix, _ = match.groups()
                    new_id = prefix+new_id

                tag.set_id(new_id)

                # Notify processor about change
                text = self._tag_processor.update_tag(text, tag)

                offset += len(new_id) - len(old_id)
                current_id += 1

        # Update reference IDs
        offset = 0
        for tag in tags:
            # update position
            tag.set_position(tag.get_position()+offset)
            if not (references := tag.get_references()):
                continue
            attributes = tag.get_attributes()
            for attribute_name, old_ref_id in attributes.items():
                if attribute_name in references:
                    new_ref_id = references[attribute_name].get_id()
                    attributes[attribute_name] = new_ref_id
                    offset += len(new_ref_id)-len(old_ref_id)
                    # Notify processor about change
            text = self._tag_processor.update_tag(text, tag)

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

    def _resolve_references(self, references: Dict[str, str], target_model: IDocumentModel) -> Dict[str, str]:
        """
        Resolves reference IDs in the provided dictionary by replacing them with the corresponding UUIDs.

        This method iterates over the tags in the given document model and replaces the values in 
        the `references` dictionary with the corresponding UUIDs of the matching tags.

        Args:
            references (Dict[str, str]): A dictionary where keys are reference names and values are tag IDs.
            target_model (IDocumentModel): The document model containing the tags.

        Returns:
            Dict[str, str]: The updated dictionary with reference values replaced by the corresponding UUIDs.
        """
        tags = target_model.get_tags()
        reference_ids = set(references.values())

        for tag in tags:
            tag_id = tag.get_id()
            if tag_id in reference_ids:
                for key, value in references.items():
                    if value == tag_id:
                        references[key] = tag
                        tag.increment_reference_count()
        return references

    def is_deletion_prohibited(self, uuid: str, target_model: IDocumentModel) -> bool:
        """
        Checks whether a tag is protected from deletion due to existing references.

        This method retrieves the tag associated with the given UUID from the document model
        and checks if it is currently referenced by other tags. If the tag has incoming references,
        it cannot be deleted.

        Args:
            uuid (str): The unique identifier of the tag to check.
            target_model (IDocumentModel): The document model containing the tag.

        Returns:
            bool: True if the tag cannot be deleted due to references, False otherwise.

        Raises:
            ValueError: If no tag with the given UUID exists in the document model.
        """
        tags = target_model.get_tags()

        for tag in tags:
            if tag.get_uuid() == uuid:
                return tag.is_deletion_prohibited()

        raise ValueError(f"Tag with UUID {uuid} does not exist.")

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
                return tag.get_tag_data()

        raise ValueError(f"Tag with UUID {tag_uuid} does not exist.")

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

    def get_uuid_from_id(self, tag_id: str, target_model: IDocumentModel) -> str:
        """
        Returns the UUID of a tag with the given ID.

        Args:
            tag_id (str): The ID of the tag.
            target_model (IDocumentModel): The document model containing the tag.

        Returns:
            str: The UUID of the tag.

        Raises:
            ValueError: If no tag with the specified ID exists.
        """
        tags = target_model.get_tags()
        for tag in tags:
            if tag.get_id() == tag_id:
                return tag.get_uuid()
        raise ValueError(f"No tag found with ID '{tag_id}'.")

    def set_meta_tags(self, tag_strings: Dict[str, str], target_model: IDocumentModel) -> None:
        """
        Sets the meta tags for the given document model based on the provided tag strings.

        Args:
            tag_strings (Dict[str, str]): A dictionary where keys represent tag types and 
                values contain the corresponding tag strings.
            target_model (IDocumentModel): The document model to which the processed meta 
                tags will be assigned.
        """
        meta_tags = {}
        for tag_type, meta_tag_strings in tag_strings.items():
            tag_data = self._tag_processor.extract_tags_from_text(
                meta_tag_strings)
            tags = []
            for tag in tag_data:
                tags.append(TagModel(tag_data=tag))
            meta_tags[tag_type] = tags

        target_model.set_meta_tags(meta_tags)

    # TODO Complete reference resolving
    def insert_sentence(self, sentence: str, global_index: int, target_model: IDocumentModel) -> None:
        """
        Inserts a tagged sentence into the document model at the specified global index.

        This method calculates the correct insertion offset based on the global index of the
        sentence in the common text, extracts the tags from the sentence, and inserts each tag
        at the appropriate position in the model text.

        Args:
            sentence (str): The tagged sentence to be inserted.
            global_index (int): The global index of the sentence in the common text.
            target_model (IDocumentModel): The target document model to be updated.
        """
        # Get required data from the model
        sentences = target_model.get_common_text()
        separator = "\n\n"

        # Compute character offset in the full text
        offset = sum(len(sentence) + len(separator)
                     for sentence in sentences[:global_index])

        # Extract tag data from sentence
        extracted_tag_data = self._tag_processor.extract_tags_from_text(
            sentence)

        for tag_data in extracted_tag_data:
            tag_data["position"] += offset
            tag_data["uuid"] = self._generate_unique_id()
            tag_data["references"] = self._resolve_references(
                tag_data.get("references", {}), target_model)
            self.add_tag(tag_data=tag_data, target_model=target_model)

    # * dont need that mapping
    # def build_global_uuid_mapping(self, documents: List[List[str]], merged_document: IDocumentModel) -> Dict:
    #     documents_tags = []
    #     for document in documents:
    #         documents_tags.append(document.get_tags())
    #     merged_tags = merged_document.get_tags()
    #     for index,common_sentence in enumerate(merged_document):
    #         sentences=[document[index] for document in documents]

    def _find_equivalent_tags(
        self,
        sentences: List[str],
        common_sentence: str,
        documents_tags: List[List[ITagModel]],
        merged_tags: List[ITagModel]
    ) -> None:
        """
        Identifies and marks equivalent tags across different annotator sentence versions.

        For each sentence variant, this method determines which tags are semantically and 
        structurally equivalent by comparing tag type, text content, attributes (excluding ID), 
        reference names, and relative position in the sentence. All tags determined to be 
        equivalent are grouped by a tag hash.

        Tags are considered equivalent if:
            - The sentence is present in the merged version (implying all annotators agreed).
            - Their tag content and structure match as described above.

        Side effects:
            - Each local tag receives a tag hash.
            - For each tag in the global document-level tag structure (`documents_tags`), the 
              method sets a list of `equivalent_uuids` referencing all tags considered equivalent 
              (including its own).
        """
        tags_common_sentence = self._tag_processor.extract_tags_from_text(
            common_sentence)
        tags_sentences = [self._tag_processor.extract_tags_from_text(
            sentence) for sentence in sentences]

        if tags_common_sentence:  # all tags are equivalent
            for index in range(len(tags_common_sentence)):
                equivalent_uuids = []

                # Collect UUIDs from all annotator versions and the merged sentence
                all_tags = tags_sentences + [tags_common_sentence]
                all_documents = documents_tags + [merged_tags]

                for version_index, tags in enumerate(all_tags):
                    tag_id = tags[index].get_id()
                    for tag in all_documents[version_index]:
                        if tag.get_id() == tag_id:
                            equivalent_uuids.append(tag.get_uuid())
                            break

                # Set equivalent UUIDs on all corresponding tag objects
                for version_index, tags in enumerate(all_tags):
                    tag_id = tags[index].get_id()
                    for tag in all_documents[version_index]:
                        if tag.get_id() == tag_id:
                            tag.set_equivalent_uuids(equivalent_uuids)
                            break
            return

        # Map from hash signature to list of equivalent UUIDs
        equivalence_map = {}

        for annotator_index, tags in enumerate(tags_sentences):
            sentence = sentences[annotator_index]
            for tag in tags:
                tag_type = tag.get_tag_type()
                tag_text = tag.get_text()

                # Attributes without ID
                attributes = tag.get_attributes()
                attributes_filtered = {key: value for key,
                                       value in attributes.items() if key != "id"}

                # Reference attribute names
                reference_keys = list(tag.get_references().keys())

                # Calculate sentence-local position
                local_pos = tag.get_position()
                sentence_prefix = sentence[:local_pos]
                relative_position = len(
                    self._tag_processor.delete_all_tags_from_text(sentence_prefix))

                # Build signature list
                signature_components = [
                    tag_type,
                    tag_text,
                    str(sorted(attributes_filtered.items())),
                    str(sorted(reference_keys)),
                    str(relative_position)
                ]
                signature_string = "|".join(signature_components)
                tag_hash = md5(signature_string.encode("utf-8")).hexdigest()
                tag.set_tag_hash(tag_hash)

                equivalence_map.setdefault(tag_hash, []).append(tag.get_uuid())

        # Assign equivalent UUIDs to global document tags using local tag ID mapping
        for annotator_index, tags in enumerate(tags_sentences):
            for tag in tags:
                tag_hash = tag.get_tag_hash()
                tag_id = tag.get_id()
                equivalent_uuids = equivalence_map.get(tag_hash, [])

                # Find corresponding global tag in the same annotator document
                for global_tag in documents_tags[annotator_index]:
                    if global_tag.get_id() == tag_id:
                        global_tag.set_equivalent_uuids(equivalent_uuids)
                        break
