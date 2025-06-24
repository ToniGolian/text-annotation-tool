import os
from commands.add_tag_command import AddTagCommand
from commands.adopt_annotation_command import AdoptAnnotationCommand
from commands.delete_tag_command import DeleteTagCommand
from commands.edit_tag_command import EditTagCommand
from enums.failure_reasons import FailureReason
from controller.interfaces import IController
from commands.interfaces import ICommand
from enums.search_types import SearchType
from input_output.file_handler import FileHandler
from model.annotation_document_model import AnnotationDocumentModel
from model.interfaces import IComparisonModel, IConfigurationModel, IDocumentModel, ISearchModel, ISelectionModel
from model.tag_model import TagModel
from model.undo_redo_model import UndoRedoModel
from observer.interfaces import IPublisher, IObserver, IPublisher, IObserver
from typing import Callable, Dict, List, Optional, Tuple
from utils.color_manager import ColorManager
from utils.comparison_manager import ComparisonManager
from utils.configuration_manager import ConfigurationManager
from utils.list_manager import ListManager
from utils.path_manager import PathManager
from utils.pdf_extraction_manager import PDFExtractionManager
from utils.search_manager import SearchManager
from utils.search_model_manager import SearchModelManager
from utils.settings_manager import SettingsManager
from utils.suggestion_manager import SuggestionManager
from utils.tag_manager import TagManager
from utils.tag_processor import TagProcessor
from view.interfaces import IComparisonView, IView
import tkinter.messagebox as mbox


class Controller(IController):
    def __init__(self, configuration_model: IConfigurationModel, preview_document_model: IPublisher = None, annotation_document_model: IPublisher = None, comparison_model: IComparisonModel = None, selection_model: IPublisher = None, appearance_model: IPublisher = None, highlight_model: IPublisher = None, annotation_mode_model: IPublisher = None) -> None:

        # dependencies
        self._path_manager = PathManager()
        self._file_handler = FileHandler(path_manager=self._path_manager)
        self._configuration_manager = ConfigurationManager(self._file_handler)
        self._suggestion_manager = SuggestionManager(self, self._file_handler)
        self._settings_manager = SettingsManager(self._file_handler)
        self._tag_processor = TagProcessor(self)
        self._tag_manager = TagManager(self, self._tag_processor)
        self._comparison_manager = ComparisonManager(self, self._tag_processor)
        self._list_manager = ListManager(
            self._file_handler, self._settings_manager)
        self._pdf_extraction_manager = PDFExtractionManager(
            list_manager=self._list_manager)
        self._search_manager = SearchManager(self._file_handler)
        self._search_model_manager = SearchModelManager(self._search_manager)
        self._color_manager = ColorManager(self._file_handler)

        # config
        # Load the source mapping once and store it in an instance variable
        self._source_mapping = self._file_handler.read_file(
            "source_mapping")

        # views
        self._comparison_view: IComparisonView = None
        self._views_to_finalize: List = []

        # state
        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observer_layout_map: Dict[IObserver, Dict] = {}

        self._configuration_model: IPublisher = configuration_model
        self._appearance_model: IPublisher = appearance_model
        self._extraction_document_model: IDocumentModel = preview_document_model
        self._annotation_document_model: IDocumentModel = annotation_document_model
        self._comparison_model: IComparisonModel = comparison_model
        self._selection_model: ISelectionModel = selection_model
        self._annotation_mode_model: IPublisher = annotation_mode_model
        self._highlight_model = highlight_model
        self._current_search_model: IPublisher = None

        # command pattern
        self._active_view_id = None  # Track the currently active view
        self._undo_redo_models: Dict[str, UndoRedoModel] = {}

        # maps view ids to document sources for save actions
        self._document_source_mapping = {"extraction": self._extraction_document_model,
                                         "annotation": self._annotation_document_model,
                                         "comparison": self._comparison_model}

    # command pattern

    def _execute_command(self, command: ICommand, caller_id: str) -> None:
        """
        Executes a command, adds it to the undo stack of the corresponding view,
        and clears the redo stack for that view.

        Args:
            command (ICommand): The command object to execute.
            caller_id (str): The unique identifier for the view initiating the command.
        """
        if caller_id in self._undo_redo_models:
            model = self._undo_redo_models[caller_id]
            model.execute_command(command)
            command.execute()

    def undo_command(self, caller_id: str = None) -> None:
        """
        Undoes the last command for the specified or active view by moving it from the undo stack
        to the redo stack and calling its undo method.

        Args:
            caller_id (str, optional): The unique identifier for the view requesting the undo.
                                       Defaults to the currently active view.
        """
        if not caller_id:
            caller_id = self._active_view_id
        if caller_id in self._undo_redo_models:
            model = self._undo_redo_models[caller_id]
            command = model.undo_command()
            if command:
                command.undo()

    def redo_command(self, caller_id: str = None) -> None:
        """
        Redoes the last undone command for the specified or active view by moving it from the redo stack
        to the undo stack and calling its redo method.

        Args:
            caller_id (str, optional): The unique identifier for the view requesting the redo.
                                       Defaults to the currently active view.
        """
        if not caller_id:
            caller_id = self._active_view_id
        if caller_id in self._undo_redo_models:
            model = self._undo_redo_models[caller_id]
            command = model.redo_command()
            if command:
                command.redo()

    # observer pattern

    def add_observer(self, observer: IObserver) -> None:
        """
        Registers an observer to all relevant publishers based on the predefined mapping.

        This method retrieves all publishers related to the observer and registers it
        dynamically by checking the keys in `source_keys`.

        Args:
            observer (IObserver): The observer to be added.

        Raises:
            KeyError: If no mapping exists for the given observer.
        """
        # Retrieve the full mapping for the observer (without specifying a publisher)
        observer_config = self._get_observer_config(observer)

        # Iterate through all publishers by extracting keys from `source_keys`
        for config in observer_config.values():
            finalize = config["finalize"]
            source_keys = config["source_keys"]

            # Extract publisher instances dynamically based on `source_keys`
            for publisher_key in source_keys.keys():
                # Convert the string key into the actual instance stored in the Controller
                publisher_instance = getattr(self, f"_{publisher_key}", None)

                if publisher_instance is None:
                    print(
                        f"INFO: Publisher '{publisher_key}' not yet available for observer '{observer.__class__.__name__}'")
                else:  # Register observer with the publisher
                    publisher_instance.add_observer(observer)

            # Add observer to finalize list if required
            if finalize:
                self._views_to_finalize.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        """
        Removes an observer from all relevant publishers and clears any associated mappings or registrations.

        This method dynamically retrieves all publishers related to the observer and removes the observer
        from them by resolving the publisher names via Controller attributes.

        Args:
            observer (IObserver): The observer to be removed.

        Raises:
            KeyError: If no mapping exists for the given observer or a publisher instance cannot be resolved.
        """
        # Retrieve the full mapping for the observer (without specifying a publisher)
        observer_config = self._get_observer_config(observer)

        # Iterate through all publishers by extracting keys from `source_keys`
        for config in observer_config.values():
            source_keys = config["source_keys"]

            for publisher_key in source_keys.keys():
                # Convert the string key into the actual instance stored in the Controller
                publisher_instance = getattr(self, f"_{publisher_key}", None)

                if publisher_instance is None:
                    raise KeyError(
                        f"Publisher instance '{publisher_key}' not found as an attribute in Controller "
                        f"for observer {observer.__class__.__name__}")

                # Remove observer from the publisher
                publisher_instance.remove_observer(observer)

        # If the observer was added to the finalize list, remove it
        if observer in self._views_to_finalize:
            self._views_to_finalize.remove(observer)

    def get_observer_state(self, observer: IObserver, publisher: IPublisher = None) -> dict:
        """
        Retrieves the updated state information for a specific observer and publisher.

        If a required data source (publisher) is not yet available, it is ignored temporarily,
        but the subscription remains valid and will be re-evaluated on the next update.

        Args:
            observer (IObserver): The observer requesting updated state information.
            publisher (IPublisher, optional): The publisher that triggered the update. Defaults to None.

        Returns:
            dict: The computed state information specific to the requesting observer.

        Raises:
            KeyError: If the provided observer is not registered.
        """
        mapping = self._get_observer_config(observer, publisher)

        state = {}

        if publisher:
            source_keys = mapping["source_keys"]

            for source_name, keys in source_keys.items():

                if observer.is_static_observer() or source_name not in mapping["source_keys"]:
                    source = getattr(self, f"_{source_name}", None)
                else:
                    source = publisher

                if source is not None:
                    for key in keys:
                        value = source.get_state().get(key)

                        if value is not None:
                            state[key] = value

        else:
            # Combine all keys from all publishers
            for publisher_mapping in mapping.values():
                for source_name, keys in publisher_mapping["source_keys"].items():
                    source = getattr(self, f"_{source_name}", None)
                    if source is not None:
                        for key in keys:
                            value = source.get_state().get(key)
                            if value is not None:
                                state[key] = value

        return state

    def _get_observer_config(self, observer: IObserver, publisher: IPublisher = None) -> Dict:
        """
        Retrieves the configuration for a given observer and optionally for a specific publisher.

        If the publisher is provided, the method filters the configuration further based on the publisher type.
        If no publisher is provided, it returns the entire mapping for all publishers related to the observer.

        Args:
            observer (IObserver): The observer requesting the configuration.
            publisher (IPublisher, optional): The publisher that triggered the update. Defaults to None.

        Returns:
            Dict: The configuration dictionary associated with the observer.
                If a publisher is provided, returns only that publisher's configuration.
                If no publisher is provided, returns the full mapping for all publishers.

        Raises:
            KeyError: If no configuration is found for the observer or the specific publisher.
        """
        # Use preloaded source mapping
        observer_name = observer.__class__.__name__

        # Step 1: Filter by Observer
        if observer_name not in self._source_mapping:
            raise KeyError(
                f"No configuration found for observer {observer_name}")

        observer_config = self._source_mapping[observer_name]

        # If no publisher is provided, return all mappings for the observer
        if publisher is None:
            return observer_config

        # Step 2: Filter by Publisher
        publisher_name = publisher.__class__.__name__

        if publisher_name not in observer_config:
            raise KeyError(
                f"No configuration found for observer {observer_name} and publisher {publisher_name}")

        return observer_config[publisher_name]

    # initialization

    def finalize_views(self) -> None:
        """
        Finalizes the initialization of all views that were previously
        not fully initialized.

        This method iterates over all registered views (observers) and
        triggers their `update` method to provide the necessary data
        for completing their initialization. It ensures that all views
        are in a fully operational state after this method is called.

        Note:
            This method assumes that all views requiring finalization
            have already been registered with the controller.
        """
        configuration = self._configuration_manager.load_configuration()
        self._configuration_model.set_configuration(
            configuration=configuration)
        for view in self._views_to_finalize:
            view.finalize_view()

    def register_view(self, view_id: str, view: IView = None) -> None:
        """
        Initializes an Undo/Redo model for a specific view.

        Args:
            view_id (str): The unique identifier for the view for which the
                           Undo/Redo model is being set up.
        """
        self._undo_redo_models[view_id] = UndoRedoModel()
        if view_id == "comparison":
            self._comparison_view = view

    # decorators
    def invalidate_search_models(method):
        """Decorator to invalidate search models before executing a method.
        This decorator ensures that all search models are invalidated before the method is executed,
        and the current search model is updated afterwards.
        """

        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._search_model_manager.invalidate_all()
            if not self._current_search_model:
                return result
            self._current_search_model = self._search_model_manager.update_model(
                self._current_search_model)
            # Jump to next search result if the calling method is perform_add_tag
            if method.__name__ == "perform_add_tag":
                self.perform_next_suggestion()
            return result
        return wrapper

    def with_highlight_update(method):
        """
        Decorator that ensures the highlight model is updated after the decorated method is executed.

        This is useful for controller methods that modify search or tag data which affects highlighting.

        Args:
            method (Callable): The method to wrap.

        Returns:
            Callable: The wrapped method that updates the highlight model after execution.
        """

        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            self._update_highlight_model()
            return result
        return wrapper

    # Perform methods
    @with_highlight_update
    def perform_manual_search(self, search_options: Dict, caller_id: str) -> None:
        """
        Initiates a manual search with the specified parameters.

        This method delegates the execution of a manual search to the search model manager,
        based on user-defined search options such as case sensitivity, whole word matching,
        and regular expressions. The corresponding document model is selected using the caller ID.

        Args:
            search_options (Dict): A dictionary of search parameters with the following keys:
                - 'search_term' (str): The term to search for in the document.
                - 'case_sensitive' (bool): Whether the search should be case-sensitive.
                - 'whole_word' (bool): Whether to match only whole words.
                - 'regex' (bool): Whether the search term should be treated as a regular expression.
            caller_id (str): The identifier of the view or component initiating the search,
                             used to select the appropriate document model.
        """
        # Load the current search model
        self._annotation_mode_model.set_manual_mode()
        document_model = self._comparison_model.get_raw_text_model(
        ) if caller_id == "comparison" else self._document_source_mapping[caller_id]
        self._current_search_model = self._search_model_manager.get_active_model(
            search_type=SearchType.MANUAL, document_model=document_model, options=search_options)
        self._current_search_model.next_result()

        # Update the selection model with the current search result
        self._current_search_to_selection()

    # @with_highlight_update
    # def perform_deactivate_manual_search_model(self) -> None:
    #     """
    #     Deactivates the currently active manual search model.
    #     """
    #     self._search_model_manager.deactivate_active_manual_search_model()

    @with_highlight_update
    def perform_start_db_search(self, tag_type: str, caller_id: str) -> None:
        """
        Starts the annotation mode for a specific tag type.

        This method initializes the annotation mode for the specified tag type,
        allowing the user to annotate text with tags of that type. It sets up
        the necessary state and prepares the view for annotation.

        Args:
            tag_type (str): The type of tag to start annotating.
        """
        self._annotation_mode_model.set_auto_mode()
        document_model = self._comparison_model.get_raw_text_model(
        ) if caller_id == "comparison" else self._document_source_mapping[caller_id]

        self._current_search_model = self._search_model_manager.get_active_model(
            tag_type=tag_type,
            search_type=SearchType.DB,
            document_model=document_model
        )
        self._current_search_model.next_result()
        # Update the selection model with the current search result
        self._current_search_to_selection()

    def _current_search_to_selection(self) -> None:
        """
        Updates the selection model with the current search result.

        Args:
            search_model (ISearchModel): The search model containing the current search result.
        """
        search_result = self._current_search_model.get_state().get(
            "current_search_result", None)
        current_selection = {
            "selected_text": search_result.term if search_result else "",
            "position": search_result.start if search_result else -1
        }
        self.perform_text_selected(current_selection)

    def perform_end_search(self) -> None:
        """
        Ends the annotation mode for a specific tag type.

        This method finalizes the auto annotation mode by switching to manual mode
        and deactivating the currently active search model.
        """
        self._annotation_mode_model.set_manual_mode()
        self._search_model_manager.deactivate_active_search_model()
        self._highlight_model.clear_search_highlights()
        self._current_search_model.previous_result()  # Reset to the last result
        self._current_search_model = None

    @with_highlight_update
    def perform_next_suggestion(self) -> None:
        """
        Moves to the next suggestion for the active search type.

        Raises:
            RuntimeError: If no model is active or the active model does not match the tag type.
        """
        if not self._current_search_model:
            raise RuntimeError("No search model is currently active.")
        self._current_search_model.next_result()
        self._current_search_to_selection()

    @with_highlight_update
    def perform_previous_suggestion(self) -> None:
        """
        Moves to the previous suggestion for the active search type.

        Raises:
            RuntimeError: If no model is active or the active model does not match the tag type.
        """
        if not self._current_search_model:
            raise RuntimeError("No search model is currently active.")
        self._current_search_model.previous_result()
        self._current_search_to_selection()

    @with_highlight_update
    def mark_wrong_db_suggestion(self, tag_type: str) -> None:
        """
        Marks the current suggestion as wrong for the specified tag type and deletes it from the search model.
        """
        # load the current suggestion from the search model
        wrong_suggestion = self._current_search_model.get_state().get(
            "current_search_result", None)
        # load wrong suggestions file
        wrong_suggestions = self._file_handler.read_file(
            "project_wrong_suggestions")
        # add current suggestion to wrong suggestions
        wrong_suggestions[tag_type].append(wrong_suggestion)
        # store updated wrong suggestions file
        self._file_handler.write_file(
            "project_wrong_suggestions", wrong_suggestions)
        # Clean up the current search model by deleting the current result
        self._current_search_model.delete_current_result()

    def perform_pdf_extraction(self, extraction_data: dict) -> None:
        """
        Extracts text from a PDF file and updates the preview document model.

        Constructs a basic document dictionary for extraction mode.

        Args:
            extraction_data (dict): A dictionary containing parameters for PDF extraction:
                - "pdf_path" (str): Path to the PDF file (required).
                - "page_margins" (str): Margins to apply to the pages (optional).
                - "page_ranges" (str): Specific page ranges to extract (optional).
        """
        extracted_text = self._pdf_extraction_manager.extract_document(
            extraction_data=extraction_data)
        pdf_path = extraction_data["pdf_path"]
        file_name = self._file_handler.derive_file_name(pdf_path)

        document = {
            "file_name": file_name,
            "file_path": pdf_path,
            "document_type": "extraction",
            "meta_tags": {},
            "text": extracted_text
        }

        self._extraction_document_model.set_document(document)

    def perform_text_adoption(self) -> None:
        """
        Adopts the current preview document's data into the annotation document model.

        Converts the extraction document into an annotation document, updates the path,
        and stores the result in the annotation model.
        """
        document = self._extraction_document_model.get_state()
        document["document_type"] = "annotation"

        file_name = self._file_handler.derive_file_name(
            document.get("file_path", "unnamed"))
        save_dir = self._file_handler.resolve_path(
            "default_extraction_save_folder")
        save_path = os.path.join(save_dir, f"{file_name}.json")
        document["file_path"] = save_path

        self._annotation_document_model.set_document(document)

        self.set_active_view("annotation")
        self.perform_save_as(save_path)
        self.perform_open_file([save_path])
        self._appearance_model.set_active_notebook_index(1)

    def perform_update_preview_text(self, text: str) -> None:
        """
        Updates the text content of the preview document model.

        This method sets the provided text as the new content of the preview document model,
        triggering updates to its observers.

        Args:
            text (str): The new text content to update in the preview document model.

        Updates:
            - The text in the preview document model is updated, and its observers are notified.
        """
        self._extraction_document_model.set_text(text)

    def perform_update_meta_tags(self, tag_strings: Dict[str, str]) -> None:
        """
        Updates multiple meta tags in the model.

        Args:
            tag_strings (Dict[str, str]): A dictionary where keys are meta tag types
                                          and values are their corresponding new values.

        This method updates the meta tags in the model, applying the provided
        key-value pairs to modify the current state of the metadata.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        self._tag_manager.set_meta_tags(tag_strings, target_model)

    @with_highlight_update
    @invalidate_search_models
    def perform_add_tag(self, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an AddTagCommand to add a new tag to the tag manager.

        This method augments the provided tag data with the appropriate ID attribute name
        based on the tag type, constructs a command object, and executes it via the
        undo/redo mechanism for the active document view.

        Args:
            tag_data (Dict): A dictionary containing the tag attributes. Must include:
                - "tag_type" (str): The type of the tag.
                - "attributes" (Dict[str, str]): The tag's attributes.
                - "position" (int): The position of the tag in the text.
                - "text" (str): The inner text of the tag.
                - "references" (Dict[str, str]): Optional reference attributes.
                - "equivalent_uuids" (List[str]): Optional UUID equivalence list.
                - "uuid" (str): Optional UUID (generated if missing).
            caller_id (str): The unique identifier of the view initiating the action.
        """

        target_model = self._document_source_mapping[self._active_view_id]
        tag_data["id_name"] = self._configuration_model.get_id_name(
            tag_data.get("tag_type"))
        command = AddTagCommand(
            self._tag_manager, tag_data, target_model=target_model, caller_id=caller_id)
        self._execute_command(command=command, caller_id=caller_id)

    @with_highlight_update
    @invalidate_search_models
    def perform_edit_tag(self, tag_id: str, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an EditTagCommand to modify an existing tag in the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be edited.
            tag_data (Dict): A dictionary containing the updated data for the tag.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        tag_data["id_name"] = self._configuration_model.get_id_name(
            tag_data.get("tag_type"))
        tag_uuid = self._tag_manager.get_uuid_from_id(tag_id, target_model)
        command = EditTagCommand(
            self._tag_manager, tag_uuid, tag_data, target_model)
        self._execute_command(command=command, caller_id=caller_id)

    @with_highlight_update
    @invalidate_search_models
    def perform_delete_tag(self, tag_id: str, caller_id: str) -> None:
        """
        Creates and executes a DeleteTagCommand to remove a tag from the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be deleted.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        tag_uuid = self._tag_manager.get_uuid_from_id(tag_id, target_model)

        # Check if the tag can be deleted before creating the command
        if self._tag_manager.is_deletion_prohibited(tag_uuid, target_model):
            self._handle_failure(FailureReason.TAG_IS_REFERENCED)
            return

        # Create and execute the delete command since deletion is allowed
        command = DeleteTagCommand(self._tag_manager, tag_uuid, target_model)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_text_selected(self, selection_data: Dict) -> None:
        """
        Updates the selection model with the newly selected text, its position, and suggested attributes.

        This method is triggered when text is selected in the view and updates
        the selection model to reflect the new selection, including possible attribute
        and ID suggestions based on the selected text and existing document data.

        Args:
            selection_data (Dict): A dictionary containing:
                - "selected_text" (str): The selected text.
                - "position" (int): The starting position of the selected text in the document.

        Updates:
            - The `selected_text`, `selected_position`, and `suggestions` attributes in the selection model.
            - `suggestions` contains attribute and ID recommendations based on the selected text
              and existing IDs in the document.
        """
        selected_text = selection_data["selected_text"]
        document_model = self._document_source_mapping[self._active_view_id]
        selection_data["suggestions"] = self._suggestion_manager.get_suggestions(
            selected_text, document_model)
        self._selection_model.set_selected_text_data(selection_data)

    @with_highlight_update
    @invalidate_search_models
    def perform_open_file(self, file_paths: List[str]) -> None:
        """
        Handles the process of opening files and updating the appropriate document model based on the active view.

        This method processes the provided file paths, determines the active view, and updates the corresponding
        document model with the file data. The behavior depends on the active view:
        - For the "extraction" view, the file path is set directly in the extraction document model.
        - For the "annotation" view, the file is read and loaded into the annotation document model.
        - For the "comparison" view, multiple files are processed if necessary, and the comparison document model is updated.

        Args:
            file_paths (List[str]): A list of file paths selected by the user.
                                    For single-file operations, only the first file is used.

        Behavior:
            - **Extraction View**: Updates the extraction document model with the file path.
            - **Annotation View**: Reads the file and updates the annotation document model with its content.
            - **Comparison View**: Processes multiple files if provided, or verifies if the document type is suitable
              for comparison, then updates the comparison document model.

        Notes:
            - If multiple file paths are provided in the "comparison" view, they are processed together.
            - If the document's type is not "comparison" in the "comparison" view, additional processing is performed.

        Raises:
            ValueError: If `file_paths` is empty or the active view ID is invalid.
        """
        # Reset old state
        self._reset_undo_redo()

        # load document
        file_path = file_paths[0]
        if self._active_view_id == "extraction":
            self._extraction_document_model.set_file_path(file_path=file_path)
            return

        documents = [self._file_handler.read_file(
            file_path=file_path) for file_path in file_paths]
        for document, path in zip(documents, file_paths):
            document["file_path"] = path

        if len(documents) == 1:
            document = documents[0]

        if self._active_view_id == "annotation":
            self._annotation_document_model.set_document(document)
            self._tag_manager.extract_tags_from_document(
                self._annotation_document_model)

        # Load stored comparison_model or set up a new one from multiple documents
        if self._active_view_id == "comparison":
            if documents[0]["document_type"] == "comparison":
                if len(documents) > 1:
                    raise ValueError(
                        "Too many files selected: Only one file path is allowed when loading a predefined comparison model.")
                self._load_comparison_model(document)
            else:
                self._setup_comparison_model(documents)

    def _setup_comparison_model(self, documents) -> None:
        self._appearance_model.set_num_comparison_displays(len(documents)+1)

        document_models = [AnnotationDocumentModel()]+[AnnotationDocumentModel(
            document) for document in documents]
        for document_model in document_models:
            self._tag_manager.extract_tags_from_document(document_model)
        self._comparison_model.set_documents(document_models)
        #! Don't change the order since the documents trigger the displaycreation
        comparison_displays = self._comparison_view.get_comparison_displays()
        self._comparison_model.register_comparison_displays(
            comparison_displays)

        comparison_data = self._comparison_manager.extract_comparison_data(
            document_models[1:])
        self._comparison_model.set_comparison_data(
            comparison_data)

    def _load_comparison_model(self, document: dict) -> None:
        """
        Reconstructs the comparison model from a previously saved comparison metadata file.

        This matches exactly the structure used in `perform_save_as` for comparison view.
        """
        # Step 0: Deregister old display observers
        # self._comparison_model.clear_all_observers()

        # Step 1: Load merged and source documents
        merged_document_data = self._file_handler.read_file(
            document["document_path"])
        source_documents_data = [self._file_handler.read_file(
            path) for path in document["source_paths"]]

        # Step 2: Build document models
        raw_model = AnnotationDocumentModel()
        annotator_models = [AnnotationDocumentModel(
            data) for data in source_documents_data]
        document_models = [raw_model] + annotator_models

        # Step 3: Extract tags from all source models (not raw)
        for model in document_models:
            self._tag_manager.extract_tags_from_document(model)

        # Step 4: Register documents in the comparison model
        self._comparison_model.set_documents(document_models)

        # Step 5: Register displays
        self._appearance_model.set_num_comparison_displays(
            len(document_models))
        displays = self._comparison_view.get_comparison_displays()
        self._comparison_model.register_comparison_displays(displays)

        # Step 6: Construct merged model from saved merged document file
        merged_model = AnnotationDocumentModel(merged_document_data)

        # Step 7: Prepare and set comparison data
        start_data = self._comparison_manager.get_start_data(sentence_index=document.get(
            "current_sentence_index", 0), comparison_sentences=document.get("comparison_sentencess"))
        comparison_data = {
            "merged_document": merged_model,
            "comparison_sentences": document["comparison_sentences"],
            "differing_to_global": document["differing_to_global"],
            "start_data": start_data,
        }
        self._comparison_model.set_comparison_data(comparison_data)

        # Step 8: Restore internal state
        self._comparison_model._current_index = document.get(
            "current_sentence_index", 0)
        self._comparison_model._adopted_flags = document.get(
            "adopted_flags", [False] * len(document["comparison_sentences"])
        )

    def extract_tags_from_document(self, documents) -> None:
        """
        Extracts tags for all given documents and stores them in their corresponding models.

        Args:
            documents (List[IDocumentModel]): A list of document models to extract tags from.
        """
        for document in documents:
            self._tag_manager.extract_tags_from_document(document)

    # todo remove
    def find_equivalent_tags(self, documents: List[IDocumentModel], merged_document: IDocumentModel) -> None:
        """
        Identifies and marks equivalent tags across multiple document versions.

        This method analyzes tags across all annotator documents and the merged document
        to determine equivalence based on structure and content. It updates each tag
        with a list of UUIDs representing all of its equivalent counterparts.

        Args:
            documents (List[IDocumentModel]): The annotator-specific document models.
            merged_document (IDocumentModel): The merged reference document.

        Side Effects:
            Each tag in the documents and the merged document will be updated via
            `set_equivalent_uuids()` to include the UUIDs of all semantically
            equivalent tags across versions.
        """
        documents_tags = [document.get_tags() for document in documents]
        merged_document_tags = merged_document.get_tags()
        separator = '\n\n'
        documents_sentences = [document.get_text().split(separator)
                               for document in documents]
        merged_sentences = merged_document.get_text().split(separator)

        for index, merged_sentence in enumerate(merged_sentences):
            sentences = [document_sentences[index]
                         for document_sentences in documents_sentences]
            self._tag_manager.find_equivalent_tags(
                sentences=sentences, common_sentence=merged_sentence, documents_tags=documents_tags, merged_tags=merged_document_tags)

    def perform_save_as(self, file_path: Optional[str] = None):
        """
        Saves the current document to the specified file path.

        For comparison views, saves the merged document into the annotation folder
        and the comparison metadata into the comparison folder.
        """
        data_source = self.get_save_as_config()["data_source"]
        document = data_source.get_state()

        if self._active_view_id == "comparison":
            # Construct merged file name and paths
            base_name = self._file_handler.derive_file_name(
                document["source_file_paths"][0])
            merged_file_name = f"{base_name}_merged.json"

            annotation_folder = self._file_handler.resolve_path(
                "default_annotation_save_folder")
            comparison_folder = self._file_handler.resolve_path(
                "default_comparison_save_folder")

            # Final full paths
            annotation_file_path = os.path.join(
                annotation_folder, merged_file_name)
            comparison_info_path = os.path.join(
                comparison_folder, f"{base_name}_comparison.json")

            # Prepare document for saving
            clean_document = {
                "file_path": annotation_file_path,
                "file_name": base_name + "_merged",
                "document_type": "annotation",
                "meta_tags": {
                    tag_type: [", ".join(str(tag) for tag in tags)]
                    for tag_type, tags in document.get("meta_tags", {}).items()
                },
                "text": document["text"]
            }

            # Save merged annotation document
            self._file_handler.write_file(file_path, clean_document)

            # Save comparison metadata
            comparison_info = {
                "document_type": "comparison",
                "source_paths": document["source_file_paths"],
                "document_path": file_path,
                "file_names": document.get("file_names", []),
                "num_sentences": document.get("num_sentences", 0),
                "current_sentence_index": document.get("current_sentence_index", 0),
                "comparison_sentences": document.get("comparison_sentences", []),
                "adopted_flags": document.get("adopted_flags", []),
                "differing_to_global": document.get("differing_to_global", []),
            }
            self._file_handler.write_file(
                comparison_info_path, comparison_info)

        else:
            # Normal annotation/extraction mode
            document["file_path"] = file_path
            document["file_name"] = self._file_handler.derive_file_name(
                file_path)
            document["document_type"] = self._active_view_id
            meta_tag_strings = {
                tag_type: [", ".join(str(tag) for tag in tags)]
                for tag_type, tags in document.get("meta_tags", {}).items()
            }
            document["meta_tags"] = meta_tag_strings
            document.pop("tags", None)

            self._file_handler.write_file(file_path, document)

    def perform_prev_sentence(self) -> None:
        """
        Moves the comparison model to the previous sentence and updates documents.
        """
        self._shift_and_update(self._comparison_model.previous_sentences)

    def perform_next_sentence(self) -> None:
        """
        Moves the comparison model to the next sentence and updates documents.
        """
        self._shift_and_update(self._comparison_model.next_sentences)

    def _shift_and_update(self, sentence_func: Callable[[], List[str]]) -> None:
        """
        Internal helper to shift the current sentence and update the documents.

        Args:
            sentence_func (Callable[[], List[str]]): Function to retrieve the target sentence(s).
        """
        sentences = sentence_func()
        tags = [[TagModel(tag_data) for tag_data in self._tag_processor.extract_tags_from_text(
            sentence)] for sentence in sentences]
        self._comparison_model.update_documents(sentences, tags)

    def perform_adopt_annotation(self, adoption_index: int) -> None:
        """
        Performs the adoption of an annotated sentence by creating and executing
        an AdoptAnnotationCommand using data provided by the comparison model.

        Args:
            adoption_index (int): Index of the annotator whose sentence is adopted.
        """
        adoption_data = self._comparison_model.get_adoption_data(
            adoption_index)

        # check if sentences is already adopted
        if adoption_data["is_adopted"]:
            self._handle_failure(FailureReason.IS_ALREADY_ADOPTED)
            comparison_state = self._comparison_model.get_adoption_data(
                adoption_index)
            current_index = self._comparison_model._current_index
            return

        # check if sentence contains references, since it is not possible to resolve references yet.
        adoption_sentence = adoption_data["sentence"]
        if self._tag_processor.is_sentence_unmergable(
                adoption_sentence):
            self._handle_failure(FailureReason.COMPARISON_MODE_REF_NOT_ALLOWED)
            return

        command = AdoptAnnotationCommand(
            tag_manager=self._tag_manager,
            tag_models=adoption_data["sentence_tags"],
            target_model=adoption_data["target_model"],
            comparison_model=self._comparison_model
        )
        self._execute_command(command=command, caller_id="comparison")
        self.perform_next_sentence()

    def perform_create_color_scheme(self, project: str, colorset_name: str = "viridis") -> None:
        # DEBUG
        self._color_manager.create_color_scheme(tag_keys=self._configuration_manager.load_configuration()['layout'][
            'tag_types'], colorset_name=colorset_name, project=project)

    # Helpers

    def _handle_failure(self, reason: FailureReason) -> None:
        """
        Handles a failed user action by showing an appropriate message box
        based on the provided FailureReason.

        Args:
            reason (FailureReason): The specific reason why the action failed.
                                    Determines the message shown to the user.

        Side Effects:
            Displays a warning or error dialog using tkinter.messagebox.

        """
        if reason == FailureReason.TAG_IS_REFERENCED:
            mbox.showerror("Action not allowed",
                           "This tag is still referenced and cannot be deleted.")
        elif reason == FailureReason.COMPARISON_MODE_REF_NOT_ALLOWED:
            mbox.showwarning("Action not allowed",
                             "Tags with references cannot be inserted in comparison mode.")
        elif reason == FailureReason.NESTED_TAGS:
            mbox.showwarning("Action not allowed",
                             "Tags can't be nested.")
        elif reason == FailureReason.IS_ALREADY_ADOPTED:
            mbox.showwarning("Action not allowed",
                             "These Sentence is already adopted.")
        # add more cases as needed

    def _reset_undo_redo(self) -> None:
        """
        Clears both the undo and redo stacks.

        This method resets the state by removing all stored undo and redo actions,
        effectively discarding any command history.
        """
        for undo_redo_model in self._undo_redo_models.values():
            undo_redo_model.reset()
# Getters/setters

    def get_selected_text_data(self) -> Dict:
        """
        Retrieves the currently selected text data from the selection model.

        This method accesses the selection model to fetch the current selected
        text and its starting position.

        Returns:
            Dict: A dictionary containing the selected text and its position with the following keys:
                - "text" (str): The currently selected text.
                - "position" (int): The starting position of the selected text in the document.
        """
        return self._selection_model.get_state()

    def get_active_view(self) -> str:
        """
        Returns the unique identifier of the currently active view.

        This method provides the view ID of the view that is currently focused
        and interacting with the user. It is used to ensure that actions such as
        undo and redo are applied to the correct view.

        Returns:
            str: The unique identifier of the active view.
        """
        return self._active_view_id

    def set_active_view(self, view_id: str) -> None:
        """
        Sets the active view for shortcut handling.

        Args:
            view_id (str): The unique identifier of the currently active view.
        """
        self._active_view_id = view_id

        index_mapping = {
            "extraction": 0,
            "annotation": 1,
            "comparison": 2
        }

        index = index_mapping.get(view_id)
        if index is not None:
            self._appearance_model.set_active_notebook_index(index)

    def get_open_file_config(self) -> dict:
        """
        Returns the configuration for the open file dialog.

        This method constructs the configuration based on the active view and
        determines the initial directory, file types, and dialog title.

        Returns:
            dict: A dictionary containing the configuration for the open file dialog.
                - "initial_dir" (str): The initial directory for the file dialog.
                - "filetypes" (list of tuples): The allowed file types.
                - "title" (str): The title of the dialog.
        """
        # Determine the file extension and default path based on the active view
        if self._active_view_id == "extraction":
            file_extension = "pdf"
        else:
            file_extension = "json"
        if self._active_view_id == "comparison":
            multiselect = True
        else:
            multiselect = False

        key = f"default_{self._active_view_id}_load_folder"
        initial_dir = self._file_handler.resolve_path(key)

        # Construct the dialog configuration
        return {
            "initial_dir": initial_dir,
            "filetypes": [(f"{file_extension.upper()} Files", f"*.{file_extension}"), ("All Files", "*.*")],
            "title": "Open File",
            "multiselect": multiselect
        }

    def get_save_as_config(self) -> dict:
        """
        Returns configuration for the save-as dialog and the associated data source.

        Includes dialog metadata used in the view and the current document model
        used by the controller to save the file content.

        Returns:
            dict: A dictionary with:
                - "initial_dir" (str): Start directory for the dialog.
                - "filetypes" (list of tuples): Allowed file types.
                - "defaultextension" (str): Default file extension.
                - "title" (str): Dialog window title.
                - "data_source" (IDocumentModel): The current model to be saved.
        """

        # Determine the file extension and default path based on the active view
        file_extension = "json"
        data_source = self._document_source_mapping[self._active_view_id]
        key = f"default_{self._active_view_id}_save_folder"
        initial_dir = self._file_handler.resolve_path(key)

        # Construct the dialog configuration
        return {
            "initial_dir": initial_dir,
            "filetypes": [(f"{file_extension.upper()} Files", f"*.{file_extension}"), ("All Files", "*.*")],
            "defaultextension": f".{file_extension}",
            "title": "Save File As",
            "data_source": data_source
        }

    def get_file_path(self) -> str:
        """
        Retrieves the file path from the current active data source.

        The method identifies the appropriate data source based on the active view ID
        and retrieves the file name associated with it.

        Returns:
            str: The file path of the current active data source.
        """
        data_source = self._document_source_mapping[self._active_view_id]
        return data_source.get_file_path()

    def get_highlight_data(self, target_model: IPublisher = None) -> List[Tuple[str, int, int]]:
        """
        Retrieves the highlight data for text annotation or search results.

        If the target model is an IDocumentModel, this method fetches annotation highlights.
        If the target model is an ISearchModel, it fetches search result highlights.

        Returns:
            List[Tuple[str, int, int]]: A list of tuples where:
                - The first element (str) is the highlight color.
                - The second element (int) is the start position in characters.
                - The third element (int) is the end position in characters.
        """

        if isinstance(target_model, IDocumentModel):
            color_scheme = self._configuration_model.get_color_scheme()["tags"]
            highlight_data = self._tag_manager.get_highlight_data(target_model)
            return [
                (color_scheme[tag], start, end) for tag, start, end in highlight_data
            ]
        # todo add search highlights

        elif isinstance(target_model, ISearchModel):
            current_search_color = self._configuration_model.get_color_scheme()[
                "current_search"]["background_color"]
            search_state = target_model.get_state()
            current_search_result = search_state.get(
                "current_search_result", None)
            highlight_data = [
                (current_search_color, current_search_result.start, current_search_result.end)]
            if self._configuration_model.are_all_search_results_highlighted():
                # If all search results should be highlighted, add them to the highlight data
                search_color = self._configuration_model.get_color_scheme()[
                    "search"]["background_color"]
                highlight_data += [(search_color, result.start, result.end)
                                   for result in search_state.get("results", []) if result != current_search_result]
            if self._active_view_id == "annotation":
                document_model = self._annotation_document_model
            if self._active_view_id == "comparison":
                document_model = self._comparison_model.get_raw_text_model()
            color_scheme = self._configuration_model.get_color_scheme()["tags"]
            tag_data = self._tag_manager.get_highlight_data(
                document_model)
            tag_highlights = [
                (color_scheme[tag], start, end) for tag, start, end in tag_data
            ]
            highlight_data += tag_highlights
            return highlight_data

        return []

    def _update_highlight_model(self) -> None:
        """
        Updates the highlight model with tag and search highlights based on the current active view.
        """
        color_scheme = self._configuration_model.get_color_scheme()["tags"]
        highlight_data = self._tag_manager.get_highlight_data(
            self._document_source_mapping[self._active_view_id])
        tag_highlights = [
            (color_scheme[tag], start, end) for tag, start, end in highlight_data
        ]
        self._highlight_model.add_tag_highlights(tag_highlights)

        if not self._current_search_model:
            return

        search_highlights = []

        current_search_color = self._configuration_model.get_color_scheme()[
            "current_search"]["background_color"]
        search_state = self._current_search_model.get_state()
        current_search_result = search_state.get(
            "current_search_result", None)

        if self._configuration_model.are_all_search_results_highlighted():
            search_color = self._configuration_model.get_color_scheme()[
                "search"]["background_color"]
            results = search_state.get("results", [])
            search_highlights += [
                (search_color, r.start, r.end)
                for r in results
                if r != current_search_result
            ]

        # Ensure current search result is always highlighted on top, with its specific color
        if current_search_result:
            search_highlights.append(
                (current_search_color, current_search_result.start,
                 current_search_result.end)
            )
        self._highlight_model.add_search_highlights(search_highlights)

    def get_tag_types(self) -> List[str]:
        """
        Retrieves all available tag types from the loaded template groups.

        This method iterates through the template groups and collects unique
        tag types used within the templates.

        Returns:
            List[str]: A list of unique tag types used in the current project.
        """
        return self._configuration_model.get_tag_types()

    def get_id_name(self, tag_type: str) -> str:
        """
        Retrieves the name of the ID attribute for a given tag type.

        This method returns the attribute name that serves as the unique identifier
        for a tag of the specified type.

        Args:
            tag_type (str): The type of the tag whose ID attribute name is requested.

        Returns:
            str: The name of the ID attribute for the given tag type. Returns an empty string
                 if no ID attribute is defined for the tag type.
        """
        return self._configuration_model.get_id_name(tag_type)

    def get_id_refs(self, tag_type: str) -> str:
        """
        Retrieves the ID references for a given tag type.

        This method returns the attribute name that serves as the unique identifier
        for a tag of the specified type.

        Args:
            tag_type (str): The type of the tag whose ID attribute name is requested.

        Returns:
            List[str]: A list of all attributes with an ID for the given tag type.
        """
        return self._configuration_model.get_id_refs(tag_type)

    def get_id_prefixes(self) -> Dict[str, str]:
        """
        Retrieves a dictionary, which maps the tag types to the id prefixes

        Returns:
            Dict[str,str]: A Dict which maps the tag types to the id prefixes.
        """
        return self._configuration_model.get_id_prefixes()

    def get_align_option(self) -> str:
        """
        Retrieves the alignment option from the default comparison settings.

        This method reads the comparison settings file and extracts the
        alignment option, which determines whether texts should be merged
        using "union" or "intersection".

        Returns:
            str: The alignment option, either "union" or "intersection".

        Raises:
            KeyError: If the "align_option" key is missing from the settings.
            FileNotFoundError: If the comparison settings file cannot be found.
        """
        key = "default_comparison_settings"
        comparison_settings_path = self._file_handler.resolve_path(key)
        comparison_settings = self._file_handler.read_file(
            comparison_settings_path)
        align_option = comparison_settings["align_option"]
        return align_option
