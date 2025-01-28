from commands.add_tag_command import AddTagCommand
from commands.delete_tag_command import DeleteTagCommand
from commands.edit_tag_command import EditTagCommand
from controller.interfaces import IController
from commands.interfaces import ICommand
from input_output.file_handler import FileHandler
from model.interfaces import IComparisonModel, IDocumentModel, ISelectionModel
from model.undo_redo_model import UndoRedoModel
from observer.interfaces import IDataPublisher, ILayoutObserver, ILayoutPublisher, IObserver
from typing import Dict, List

from utils.list_manager import ListManager
from utils.pdf_extraction_manager import PDFExtractionManager
from utils.settings_manager import SettingsManager
from utils.tag_manager import TagManager
from utils.tag_processor import TagProcessor
from view.annotation_text_display_frame import AnnotationTextDisplayFrame
from view.comparison_text_display_frame import ComparisonTextDisplayFrame
from view.interfaces import IAnnotationMenuFrame, IComparisonHeaderFrame, IComparisonTextDisplays, IExtractionFrame, IMetaTagsFrame, ITextDisplayFrame
from view.preview_text_display_frame import PreviewTextDisplayFrame


class Controller(IController):
    def __init__(self, configuration_model: ILayoutPublisher, preview_document_model: IDataPublisher = None, annotation_document_model: IDataPublisher = None, comparison_document_model: IDataPublisher = None, selection_model: IDataPublisher = None, comparison_model: IDataPublisher = None):

        # dependencies
        self._file_handler = FileHandler()
        self._settings_manager = SettingsManager()
        self._tag_processor = TagProcessor()
        self._tag_manager = TagManager(self._tag_processor)
        self._list_manager = ListManager(
            self._file_handler, self._settings_manager)
        self._pdf_extraction_manager = PDFExtractionManager(
            list_manager=self._list_manager)

        # state

        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observer_layout_map: Dict[ILayoutObserver, Dict] = {}
        self._observers_to_finalize: List = []

        self._configuration_model: ILayoutPublisher = configuration_model
        self._extraction_document_model: IDocumentModel = preview_document_model
        self._annotation_document_model: IDocumentModel = annotation_document_model
        self._comparison_document_model: IDocumentModel = comparison_document_model
        self._comparison_model: IComparisonModel = comparison_model
        self._selection_model: ISelectionModel = selection_model
        #!debug
        self._tag_manager.set_document(self._annotation_document_model)

        # command pattern
        self._active_view_id = None  # Track the currently active view
        self._undo_redo_models: Dict[str, UndoRedoModel] = {}

        # maps view ids to document sources for save actions
        self._document_source_mapping = {"extraction": self._extraction_document_model,
                                         "annotation": self._annotation_document_model,
                                         "comparison": self._comparison_document_model}

        # Mapping observer classes to their respective data sources, keys, and finalize status
        self._data_source_mapping = {
            PreviewTextDisplayFrame: {
                "finalize": False,
                "source_keys": {
                    self._extraction_document_model: ["text"]
                }
            },
            AnnotationTextDisplayFrame: {
                "finalize": False,
                "source_keys": {
                    self._annotation_document_model: ["text"]
                }
            },
            ComparisonTextDisplayFrame: {
                "finalize": False,
                "source_keys": {
                    self._comparison_document_model: ["text"],
                    self._comparison_model: [
                        "comparison_sentences"]
                }
            },
            IMetaTagsFrame: {
                "finalize": True,
                "source_keys": {
                    self._comparison_model: ["file_names"]
                }
            },
            IComparisonTextDisplays: {
                "finalize": True,
                "source_keys": {
                    self._comparison_model: ["file_names"]
                }
            },
            IComparisonHeaderFrame: {
                "finalize": True,
                "source_keys": {
                    self._comparison_model: [
                        "num_sentences", "current_sentence_index"]
                }
            },
            IAnnotationMenuFrame: {
                "finalize": False,
                "source_keys": {
                    self._selection_model: ["selected_text"]
                }
            },
            IExtractionFrame: {
                "finalize": False,
                "source_keys": {
                    self._extraction_document_model: ["file_path"]
                }
            }
        }

        # Mapping layout observer classes to their respective data sources, keys, and finalize status
        self._layout_source_mapping = {
            IComparisonTextDisplays: {
                "finalize": True,
                "source_keys": {
                    self._configuration_model: [
                        "filenames", "num_files"]
                }
            },
            IComparisonHeaderFrame: {
                "finalize": True,
                "source_keys": {
                    self._configuration_model: [
                        "filenames", "num_files"]
                }
            },
            IMetaTagsFrame: {
                "finalize": True,
                "source_keys": {
                    self._configuration_model: ["tag_types"]
                }
            },
            IAnnotationMenuFrame: {
                "finalize": True,
                "source_keys": {
                    self._configuration_model: [
                        "template_groups"]
                }
            }
        }

        self._mapping_types = {
            "data": self._data_source_mapping,
            "layout": self._layout_source_mapping
        }

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

    def add_observer(self, observer: IObserver, mapping_type: str) -> None:
        """
        Registers an observer (data or layout) and maps its logic using the predefined mapping.

        Args:
            observer (IObserver): The observer to be added.
            mapping_type (str): Specifies the type of observer to add ("data" or "layout").
        """
        # Retrieve the mapping based on the observer and mapping type
        mapping = self._get_observer_config(
            observer=observer, mapping_type=mapping_type)

        # Extract finalize flag and source_keys from the mapping
        finalize = mapping["finalize"]
        source_keys = mapping["source_keys"]

        # Extract sources
        sources = list(source_keys.keys())

        # Register the observer to the sources
        for source in sources:
            if mapping_type == "data":
                source.add_data_observer(observer)
            elif mapping_type == "layout":
                source.add_layout_observer(observer)

        # Add to finalize list if the mapping specifies it
        if finalize:
            self._observers_to_finalize.append(observer)

    def remove_observer(self, observer: IObserver, mapping_type: str) -> None:
        """
        Removes an observer (data or layout) and clears any associated mappings or registrations using the predefined mapping.

        Args:
            observer (IObserver): The observer to be removed.
            mapping_type (str): Specifies the type of observer to remove ("data" or "layout").
        """
        # Retrieve the mapping based on the observer and mapping type
        mapping = self._get_observer_config(
            observer=observer, mapping_type=mapping_type)

        # Extract source_keys and sources
        source_keys = mapping["source_keys"]
        sources = list(source_keys.keys())

        # If the observer was added to the finalize list, remove it
        if observer in self._observers_to_finalize:
            self._observers_to_finalize.remove(observer)

        # Remove the observer from all associated sources
        for source in sources:
            if mapping_type == "data":
                source.remove_data_observer(observer)
            elif mapping_type == "layout":
                source.remove_layout_observer(observer)

        print(f"{mapping_type.capitalize()} observer {type(observer)} removed.")

    def get_observer_state(self, observer: IObserver, mapping_type: str) -> any:
        """
        Retrieves the updated state information for a specific observer.

        This method accesses the relevant mapping (data or layout) to fetch the
        state processing logic associated with the given observer. It then executes
        this logic to return the computed state information for the observer.

        Args:
            observer (IObserver): The observer requesting updated state information.
            mapping_type (str): Specifies the type of state to retrieve ("data" or "layout").

        Returns:
            dict: The computed state information specific to the requesting observer.

        Raises:
            KeyError: If the provided observer is not registered in the corresponding mapping.
        """
        # Retrieve the mapping based on the observer and mapping type
        mapping = self._get_observer_config(observer, mapping_type)
        source_keys = mapping["source_keys"]

        # Fetch the state from the relevant sources and keys
        state = {
            key: value
            for source, keys in source_keys.items()
            for key, value in (source.get_data_state() if mapping_type == "data" else source.get_layout_state()).items()
            if key in keys
        }
        return state

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
        for observer in self._observers_to_finalize:
            observer.update_layout()

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
        document = self._extraction_document_model.get_data_state()
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
        command = AddTagCommand(self._tag_manager, tag_data)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_edit_tag(self, tag_id: str, tag_data: Dict, caller_id: str) -> None:
        """
        Creates and executes an EditTagCommand to modify an existing tag in the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be edited.
            tag_data (Dict): A dictionary containing the updated data for the tag.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        command = EditTagCommand(self._tag_manager, tag_id, tag_data)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_delete_tag(self, tag_id: str, caller_id: str) -> None:
        """
        Creates and executes a DeleteTagCommand to remove a tag from the tag manager.

        Args:
            tag_id (str): The unique identifier of the tag to be deleted.
            caller_id (str): The unique identifier of the view initiating this action.
        """
        command = DeleteTagCommand(self._tag_manager, tag_id)
        self._execute_command(command=command, caller_id=caller_id)

    def perform_text_selected(self, selection_data: Dict) -> None:
        """
        Updates the selection model with the newly selected text and its position.

        This method is triggered when text is selected in the view and updates
        the selection model to reflect the new selection.

        Args:
            text (str): The text that has been selected.
            position (int): The starting position of the selected text in the document.

        Updates:
            - The `selected_text` and `selected_position` attributes in the selection model.
        """
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
        document = data_source.get_data_state()
        document["file_path"] = file_path
        document["filename"] = self._file_handler.derive_file_name(file_path)
        document["document_type"] = self._active_view_id
        self._file_handler.write_file(file_path, document)

        # todo implement

    def _perform_annotation_comparison(self, file_paths: List[str]) -> Dict:
        pass

    def _get_observer_config(self, observer: IObserver, mapping_type: str) -> Dict:
        """
        Retrieves the configuration for a given observer based on its type and the mapping type.

        The method checks if the observer is an instance of any class or interface
        defined in the specified mapping type (`data_source_mapping` or `layout_source_mapping`).
        If a match is found, the corresponding configuration is returned.

        Args:
            observer (IObserver): The observer whose configuration needs to be retrieved.
            mapping_type (str): The type of mapping to use (e.g., "data" or "layout").

        Returns:
            Dict: The configuration dictionary associated with the observer.

        Raises:
            KeyError: If the observer does not match any entry in the specified mapping.
        """
        source_mapping = self._mapping_types[mapping_type]  # Access the correct mapping type

        for cls, config in source_mapping.items():
            if isinstance(observer, cls):
                return config

        raise KeyError(
            f"No configuration found for observer of type {type(observer).__name__}")

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
        return self._selection_model.get_data_state()

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
