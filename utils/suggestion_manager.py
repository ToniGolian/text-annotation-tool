from typing import Dict, List
from controller.interfaces import IController
from input_output.file_handler import FileHandler
from model.interfaces import IAnnotableDocumentModel


class SuggestionManager:
    """
    Manages attribute suggestions for annotations based on selected text and document context.

    This class retrieves predefined attribute suggestions from a configuration file
    and dynamically generates ID suggestions based on existing annotations in the document.

    Attributes:
        _file_handler (FileHandler): Handles file reading and writing operations.
        _attribute_suggestions (dict): Stores predefined attribute suggestions loaded from file.
    """

    def __init__(self, controller: IController, file_handler: FileHandler):
        """
        Initializes the SuggestionManager with a file handler and loads attribute suggestions.

        Args:
            file_handler (FileHandler): An instance responsible for handling file operations.
        """
        self._file_handler = file_handler
        self._controller = controller
        self._attribute_suggestions = self._file_handler.read_file(
            "project_suggestions")

    def get_suggestions(self, selected_text: str, document_model: IAnnotableDocumentModel) -> Dict:
        """
        Retrieves attribute and ID suggestions based on the selected text and document model.

        This method first calculates ID suggestions and initializes a dictionary structure.
        If predefined attribute suggestions exist for the selected text, they are added.

        Args:
            selected_text (str): The text selected for annotation.
            document_model (IAnnotableDocumentModel): The document model containing annotation data.

        Returns:
            Dict: A dictionary containing ID and attribute suggestions for relevant tag types.
        """
        tag_types = self._controller.get_tag_types()
        id_suggestions = self._calc_id_suggstions(document_model, tag_types)

        suggestions = {}
        for tag_type in tag_types:
            attribute_suggestions_for_type = self._attribute_suggestions[tag_type]
            suggestion = {"id": id_suggestions[tag_type]}
            if selected_text in attribute_suggestions_for_type:
                suggestion.update(
                    attribute_suggestions_for_type[selected_text])
            suggestions[tag_type] = suggestion
        # todo regexsuggestions
        return suggestions

    def _calc_id_suggstions(self, document_model: IAnnotableDocumentModel, tag_types: List[str]) -> Dict[str, str]:
        """
        Computes ID suggestions based on existing annotations in the document model.

        This method iterates over the existing tags in the document and generates unique
        numeric ID suggestions for each tag type.

        Args:
            document_model (IAnnotableDocumentModel): The document model containing annotation data.

        Returns:
            Dict[str, int]: A dictionary mapping tag types to their next available numeric ID.
        """
        id_suggestions = {tag_type: 1 for tag_type in tag_types}

        tags = document_model.get_tags()
        for tag in tags:
            tag_type = tag.get_tag_type()
            id_suggestions[tag_type] = id_suggestions.get(tag_type, 1) + 1

        id_prefixes = self._controller.get_id_prefixes()
        id_suggestions = {
            key: f"{id_prefixes[key]}{value}"for key, value in id_suggestions.items()}
        return id_suggestions

    # todo implement add suggestion
