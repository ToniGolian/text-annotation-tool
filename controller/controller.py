from commands.add_tag_command import AddTagCommand
from commands.delete_tag_command import DeleteTagCommand
from commands.edit_tag_command import EditTagCommand
from controller.interfaces import IController
from commands.interfaces import ICommand
from input_output.file_handler import FileHandler
from model.interfaces import IComparisonModel, IConfigurationModel, IDocumentModel, ISelectionModel
from model.undo_redo_model import UndoRedoModel
from observer.interfaces import IPublisher, IObserver, IPublisher, IObserver
from typing import Dict, List, Tuple

from utils.list_manager import ListManager
from utils.pdf_extraction_manager import PDFExtractionManager
from utils.settings_manager import SettingsManager
from utils.suggestion_manager import SuggestionManager
from utils.tag_manager import TagManager
from utils.tag_processor import TagProcessor


class Controller(IController):
    def __init__(self, configuration_model: IConfigurationModel, preview_document_model: IPublisher = None, annotation_document_model: IPublisher = None, comparison_document_model: IPublisher = None, selection_model: IPublisher = None, comparison_model: IPublisher = None):

        # dependencies
        self._file_handler = FileHandler()
        self._suggestion_manager = SuggestionManager(self._file_handler)
        self._settings_manager = SettingsManager()
        self._tag_processor = TagProcessor()
        self._tag_manager = TagManager(self._tag_processor)
        self._list_manager = ListManager(
            self._file_handler, self._settings_manager)
        self._pdf_extraction_manager = PDFExtractionManager(
            list_manager=self._list_manager)

        # config
        # Load the source mapping once and store it in an instance variable
        # todo change hardcoded path
        self._source_mapping = self._file_handler.read_file(
            "app_data/source_mapping.json")

        # state
        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observer_layout_map: Dict[IObserver, Dict] = {}
        self._views_to_finalize: List = []

        self._configuration_model: IPublisher = configuration_model
        self._extraction_document_model: IDocumentModel = preview_document_model
        self._annotation_document_model: IDocumentModel = annotation_document_model
        self._comparison_document_model: IDocumentModel = comparison_document_model
        self._comparison_model: IComparisonModel = comparison_model
        self._selection_model: ISelectionModel = selection_model

        # command pattern
        self._active_view_id = None  # Track the currently active view
        self._undo_redo_models: Dict[str, UndoRedoModel] = {}

        # maps view ids to document sources for save actions
        self._document_source_mapping = {"extraction": self._extraction_document_model,
                                         "annotation": self._annotation_document_model,
                                         "comparison": self._comparison_document_model}

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
                    raise KeyError(
                        f"Publisher instance '{publisher_key}' not found as an attribute in Controller "
                        f"for observer {observer.__class__.__name__}")

                # Register observer with the publisher
                print(
                    f"DEBUG: Registering observer {observer.__class__.__name__} to publisher {publisher_instance.__class__.__name__}")
                # Assuming all publishers have this method
                publisher_instance.add_observer(observer)

            # Add observer to finalize list if required
            if finalize:
                self._views_to_finalize.append(observer)

    def remove_observer(self, observer: IObserver) -> None:
        """
        Removes an observer from all relevant publishers and clears any associated mappings or registrations.

        This method dynamically retrieves all publishers related to the observer and removes the observer
        without requiring a specific mapping type.

        Args:
            observer (IObserver): The observer to be removed.

        Raises:
            KeyError: If no mapping exists for the given observer.
        """
        # Retrieve the full mapping for the observer (without specifying a publisher)
        observer_config = self._get_observer_config(observer)

        # Iterate through all publishers by extracting keys from `source_keys`
        for config in observer_config.values():
            source_keys = config["source_keys"]

            # Extract publisher instances dynamically based on `source_keys`
            for publisher_instance in source_keys.keys():
                if publisher_instance is None:
                    raise KeyError(
                        f"Publisher instance not found for observer {observer.__class__.__name__}")

                # Remove observer from the publisher
                # Assuming all publishers have this method
                publisher_instance.remove_observer(observer)

        # If the observer was added to the finalize list, remove it
        if observer in self._views_to_finalize:
            self._views_to_finalize.remove(observer)

        print(f"Observer {type(observer).__name__} removed.")

    def get_observer_state(self, observer: IObserver, publisher: IPublisher) -> dict:
        """
        Retrieves the updated state information for a specific observer and publisher.

        This method accesses the relevant mapping to fetch the state processing logic
        associated with the given observer and publisher. It then retrieves the relevant
        data from the appropriate data source.

        Args:
            observer (IObserver): The observer requesting updated state information.
            publisher (IDataPublisher): The publisher that triggered the update.

        Returns:
            dict: The computed state information specific to the requesting observer.

        Raises:
            KeyError: If the provided observer or publisher is not registered in the mapping.
        """
        # Retrieve the mapping based on the observer and publisher
        mapping = self._get_observer_config(observer, publisher)
        source_keys = mapping["source_keys"]

        # Fetch the state from the relevant sources and keys
        state = {
            key: value
            for source, keys in source_keys.items()
            for key, value in source.get_state().items()
            if key in keys
        }

        return state

    def get_observer_state(self, observer: IObserver, publisher: IPublisher = None) -> dict:
        """
        Retrieves the updated state information for a specific observer and publisher.

        This method accesses the relevant mapping to fetch the state processing logic
        associated with the given observer and publisher. It then retrieves the relevant
        data from the appropriate data source.

        If no publisher is provided, it merges all publisher-specific state mappings
        into a single dictionary.

        Args:
            observer (IObserver): The observer requesting updated state information.
            publisher (IPublisher, optional): The publisher that triggered the update. Defaults to None.

        Returns:
            dict: The computed state information specific to the requesting observer.

        Raises:
            KeyError: If the provided observer or publisher is not registered in the mapping.
        """
        # Retrieve the mapping based on the observer and publisher
        mapping = self._get_observer_config(observer, publisher)

        # If no publisher is provided, merge all publisher-specific mappings
        if publisher is None:
            merged_source_keys = {}
            for publisher_mapping in mapping.values():  # Iterate over all publisher configs
                for source_name, keys in publisher_mapping["source_keys"].items():
                    if source_name not in merged_source_keys:
                        merged_source_keys[source_name] = set()
                    merged_source_keys[source_name].update(keys)

            # Convert merged sets back to lists
            merged_source_keys = {
                source_name: list(keys) for source_name, keys in merged_source_keys.items()
            }
            source_keys = merged_source_keys
        else:
            source_keys = mapping["source_keys"]
        # Fetch the state from the relevant sources and keys
        state = {
            key: value
            for source_name, keys in source_keys.items()
            if (source := getattr(self, f"_{source_name}", None)) is not None
            for key, value in source.get_state().items()
            if key in keys
        }
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
        for view in self._views_to_finalize:
            view.finalize_view()

    def register_view(self, view_id: str) -> None:
        """
        Initializes an Undo/Redo model for a specific view.

        Args:
            view_id (str): The unique identifier for the view for which the
                           Undo/Redo model is being set up.
        """
        self._undo_redo_models[view_id] = UndoRedoModel()

    # Perform methods

    def perform_pdf_extraction(self, extraction_data: dict) -> None:
        """
        Extracts text from a PDF file and updates the preview document model.

        Args:
            extraction_data (dict): A dictionary containing parameters for PDF extraction:
                - "pdf_path" (str): Path to the PDF file (required).
                - "page_margins" (str): Margins to apply to the pages (optional).
                - "page_ranges" (str): Specific page ranges to extract (optional).
        """

        extracted_text = self._pdf_extraction_manager.extract_document(
            extraction_data=extraction_data)
        self._extraction_document_model.set_text(text=extracted_text)

    def perform_text_adoption(self) -> None:
        """
        Adopts the current preview document's data into the annotation document model.

        This method retrieves the data state from the preview document model and updates
        the annotation document model with the same data. It also saves the adopted
        document.

        Updates:
            - The annotation document model is updated with data from the preview document model.
            - The adopted document is saved.
        """
        document = self._extraction_document_model.get_state()
        document["document_type"] = "annotation"
        self._annotation_document_model.set_document(document)
        self._tag_manager.set_document(document)
        self.perform_save_document(document)

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

    def perform_add_tag(self, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an AddTagCommand to add a new tag to the tag manager.

        Args:
            tag_data (Dict): A dictionary containing the data for the tag to be added.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        command = AddTagCommand(self._tag_manager, tag_data, target_model)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_edit_tag(self, tag_id: str, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an EditTagCommand to modify an existing tag in the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be edited.
            tag_data (Dict): A dictionary containing the updated data for the tag.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        command = EditTagCommand(
            self._tag_manager, tag_id, tag_data, target_model)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_delete_tag(self, tag_id: str, caller_id: str) -> None:
        """
        Creates and executes a DeleteTagCommand to remove a tag from the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be deleted.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        command = DeleteTagCommand(self._tag_manager, tag_id, target_model)
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

        file_path = file_paths[0]
        if self._active_view_id == "extraction":
            self._extraction_document_model.set_file_path(file_path=file_path)
            return

        document = self._file_handler.read_file(file_path=file_path)
        document["file_path"] = file_path
        document["document_type"] = self._active_view_id

        if self._active_view_id == "annotation":
            self._annotation_document_model.set_document(document)
        if self._active_view_id == "comparison":
            # todo improve
            if len(file_path) > 1 or document.get("document_type", "") != "comparison":
                document = self._perform_annotation_comparison(
                    file_paths)
            self._comparison_document_model.set_document(document)

    def perform_save_as(self, file_path: str):
        """
        Saves the current document to the specified file path.

        This method retrieves the document data from the configured data source,
        updates the filename and document type, and writes the updated data to the
        specified file path using the file handler.

        Args:
            file_path (str): The file path where the document should be saved.

        Behavior:
            - Retrieves the document data from the configured data source.
            - Updates the "filename" field with the derived file name from the file path.
            - Updates the "file_path" field the chosen file path.
            - Updates the "document_type" field with the current active view ID.
            - Writes the updated document to the specified file path using the file handler.
        """
        data_source = self.get_save_as_config()["data_source"]
        document = data_source.get_state()
        document["file_path"] = file_path
        document["filename"] = self._file_handler.derive_file_name(file_path)
        document["document_type"] = self._active_view_id
        self._file_handler.write_file(file_path, document)

        # todo implement

    def _perform_annotation_comparison(self, file_paths: List[str]) -> Dict:
        pass

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
        initial_dir = self._file_handler.get_default_path(key)

        # Construct the dialog configuration
        return {
            "initial_dir": initial_dir,
            "filetypes": [(f"{file_extension.upper()} Files", f"*.{file_extension}"), ("All Files", "*.*")],
            "title": "Open File",
            "multiselect": multiselect
        }

    def get_save_as_config(self) -> dict:
        """
        Returns the configuration for the save-as file dialog.

        This method constructs the configuration based on the active view and
        determines the initial directory, file types, default file extension, and dialog title.

        Returns:
            dict: A dictionary containing the configuration for the save-as file dialog.
                - "initial_dir" (str): The initial directory for the file dialog.
                - "filetypes" (list of tuples): The allowed file types.
                - "defaultextension" (str): The default file extension.
                - "title" (str): The title of the dialog.
        """

        # Determine the file extension and default path based on the active view
        file_extension = "json"
        data_source = self._document_source_mapping[self._active_view_id]
        key = f"default_{self._active_view_id}_save_folder"
        initial_dir = self._file_handler.get_default_path(key)

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

    def get_highlight_data(self) -> List[Tuple[str, int, int]]:
        """
        Retrieves the highlight data for text annotation.

        This method fetches the highlight data from the tag manager and maps the tag types 
        to their corresponding colors using the color scheme from the configuration model.

        Returns:
            List[Tuple[str, int, int]]: A list of tuples where:
                - The first element (str) is the highlight color associated with the tag type.
                - The second element (int) is the start position of the highlight in the text.
                - The third element (int) is the end position of the highlight in the text.
        """
        target_model = self._document_source_mapping[self._active_view_id]
        color_scheme = self._configuration_model.get_color_scheme()
        highlight_data = self._tag_manager.get_highlight_data(target_model)
        highlight_data = [
            (color_scheme[tag], start, end) for tag, start, end in highlight_data
        ]
        return highlight_data
