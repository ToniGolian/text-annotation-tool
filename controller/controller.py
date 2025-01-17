import json
from commands.add_tag_command import AddTagCommand
from commands.delete_tag_command import DeleteTagCommand
from commands.edit_tag_command import EditTagCommand
from controller.interfaces import IController
from commands.interfaces import ICommand
from input_output.file_handler import FileHandler
from model.interfaces import IComparisonModel, IDocumentModel
from observer.interfaces import IDataObserver, IDataPublisher, ILayoutObserver, ILayoutPublisher, IObserver, IPublisher
from typing import Dict, List

from utils.list_manager import ListManager
from utils.pdf_extraction_manager import PDFExtractionManager
from utils.settings_manager import SettingsManager
from utils.tag_manager import TagManager
from utils.tag_processor import TagProcessor
from view.annotation_text_display_frame import AnnotationTextDisplayFrame
from view.comparison_text_display_frame import ComparisonTextDisplayFrame
from view.interfaces import IAnnotationMenuFrame, IComparisonHeaderFrame, IComparisonTextDisplayFrame, IComparisonTextDisplays, IMetaTagsFrame, ITextDisplayFrame
from view.preview_text_display_frame import PreviewTextDisplayFrame


class Controller(IController):
    def __init__(self, configuration_model: ILayoutPublisher, preview_document_model: IDataPublisher = None, annotation_document_model: IDataPublisher = None, comparison_document_model: IDataPublisher = None, selection_model: IDataPublisher = None, comparison_model: IDataPublisher = None):

        # dependencies
        self._file_handler = FileHandler()
        self._settings_manager = SettingsManager()
        self._tag_processor = TagProcessor()
        self._tag_manager = TagManager(self._tag_processor)
        self._configuration_manager: ILayoutPublisher = configuration_model
        self._list_manager = ListManager(
            self._file_handler, self._settings_manager)
        self._pdf_extraction_manager = PDFExtractionManager(
            list_manager=self._list_manager)

        # state
        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observer_layout_map: Dict[ILayoutObserver, Dict] = {}
        self._observers_to_finalize: List = []

        self._preview_document_model: IDocumentModel = preview_document_model
        self._annotation_document_model: IDocumentModel = annotation_document_model
        self._comparison_document_model: IDocumentModel = comparison_document_model
        self._comparison_model: IComparisonModel = comparison_model
        self._selection_model: IDataPublisher = selection_model

        # collections
        self._undo_stack = []
        self._redo_stack = []

        # Mapping observer classes to their respective data sources, keys, and finalize status
        self._data_source_mapping = {
            PreviewTextDisplayFrame: {
                "sources": [self._preview_document_model],
                "keys": ["text"],
                "finalize": False
            },
            AnnotationTextDisplayFrame: {
                "sources": [self._annotation_document_model],
                "keys": ["text"],
                "finalize": False
            },
            ComparisonTextDisplayFrame: {
                "sources": [self._comparison_document_model],
                "keys": ["text"],
                "finalize": False
            },
            IMetaTagsFrame: {
                "sources": [self._comparison_model],
                "keys": ["file_names"],
                "finalize": True
            },
            IComparisonTextDisplays: {
                "sources": [self._comparison_model],
                "keys": ["file_names"],
                "finalize": True
            },
            IComparisonHeaderFrame: {
                "sources": [self._comparison_model],
                "keys": ["num_sentences", "current_sentence_index"],
                "finalize": True
            },
            IComparisonTextDisplayFrame: {
                "sources": [self._comparison_model],
                "keys": ["comparison_sentences"],
                "finalize": False
            },
            IAnnotationMenuFrame: {
                "sources": [self._selection_model],
                "keys": ["selected_text"],
                "finalize": False
            }
        }

        # Mapping layout observer classes to their respective data sources, keys, and finalize status
        self._layout_source_mapping = {
            IComparisonTextDisplays: {
                "sources": [self._configuration_manager],
                "keys": ["filenames", "num_files"],
                "finalize": True
            },
            IComparisonHeaderFrame: {
                "sources": [self._configuration_manager],
                "keys": ["filenames", "num_files"],
                "finalize": True
            },
            IMetaTagsFrame: {
                "sources": [self._configuration_manager],
                "keys": ["tag_types"],
                "finalize": True
            },
            IAnnotationMenuFrame: {
                "sources": [self._configuration_manager],
                "keys": ["template_groups"],
                "finalize": True
            }
        }

    # command pattern

    def _execute_command(self, command: ICommand) -> None:
        """
        Executes a command, adds it to the redo stack, and clears the undo stack.

        Args:
            command: The command object to execute.
        """
        self._redo_stack.append(command)
        command.execute()

    def _undo_command(self) -> None:
        """
        Undoes the last command by moving it from the redo stack to the undo stack 
        and calling its undo method.
        """
        if self._redo_stack:
            command = self._redo_stack.pop()
            self._undo_stack.append(command)
            command.undo()

    def _redo_command(self) -> None:
        """
        Redoes the last undone command by moving it from the undo stack to the redo stack 
        and calling its redo method.
        """
        if self._undo_stack:
            command = self._undo_stack.pop()
            self._redo_stack.append(command)
            command.redo()

    # observer pattern
    def add_data_observer(self, observer: IDataObserver) -> None:
        """
        Registers a data observer and maps its data-fetching logic using the predefined mapping.

        Args:
            observer (IDataObserver): The data observer to be added.
        """
        # Retrieve the mapping by finding the appropriate key based on isinstance
        mapping = None
        for cls, value in self._data_source_mapping.items():
            if isinstance(observer, cls):
                mapping = value
                break

        if not mapping:
            print(f"Unknown Data Observer {type(observer)} registered")
            return

        sources = mapping["sources"]
        keys = mapping["keys"]

        # Handle specific logic for IComparisonTextDisplayFrame
        if isinstance(observer, IComparisonTextDisplayFrame):
            index = self._dynamic_observer_index
            self._dynamic_observer_index += 1

            # Add observer-specific data mapping
            self._observer_data_map[observer] = lambda index=index: {
                "sentence": sources[0].get_data_state()["comparison_sentences"][index]
            }

        # Register the observer to the sources
        self._set_observer_mapping(observer, keys, sources, "data")
        for source in sources:
            source.add_data_observer(observer)

        # Add to finalize list if the mapping specifies it
        if mapping["finalize"]:
            self._observers_to_finalize.append(observer)

    def add_layout_observer(self, observer: ILayoutObserver) -> None:
        """
        Registers a layout observer and maps its layout-fetching logic using the predefined mapping.

        Args:
            observer (ILayoutObserver): The layout observer to be added.
        """
        # Retrieve the mapping by finding the appropriate key based on isinstance
        mapping = None
        for cls, value in self._layout_source_mapping.items():
            if isinstance(observer, cls):
                mapping = value
                break

        if not mapping:
            print(f"Unknown Layout Observer {type(observer)} registered")
            return

        sources = mapping["sources"]
        keys = mapping["keys"]

        # Register the observer to the sources
        self._set_observer_mapping(observer, keys, sources, "layout")
        for source in sources:
            source.add_layout_observer(observer)

        # Add to finalize list if the mapping specifies it
        if mapping["finalize"]:
            self._observers_to_finalize.append(observer)

    def remove_data_observer(self, observer: IDataObserver) -> None:
        """
        Removes a data observer and clears any associated mappings or registrations using the predefined mapping.

        Args:
            observer (IDataObserver): The data observer to be removed.
        """
        # Retrieve the mapping by finding the appropriate key based on isinstance
        mapping = None
        for cls, value in self._data_source_mapping.items():
            if isinstance(observer, cls):
                mapping = value
                break

        if not mapping:
            print(f"Unknown Data Observer {type(observer)} cannot be removed")
            return

        sources = mapping["sources"]

        # Remove the observer from the data map if it exists
        if observer in self._observer_data_map:
            del self._observer_data_map[observer]

        # If the observer was added to finalize list, remove it
        if mapping["finalize"] and observer in self._observers_to_finalize:
            self._observers_to_finalize.remove(observer)

        # Remove the observer from all associated data sources
        for source in sources:
            source.remove_data_observer(observer)

        print(f"Data observer {type(observer)} removed.")

    def remove_layout_observer(self, observer: ILayoutObserver) -> None:
        """
        Removes a layout observer and clears any associated mappings or registrations using the predefined mapping.

        Args:
            observer (ILayoutObserver): The layout observer to be removed.
        """
        # Retrieve the mapping by finding the appropriate key based on isinstance
        mapping = None
        for cls, value in self._layout_source_mapping.items():
            if isinstance(observer, cls):
                mapping = value
                break

        if not mapping:
            print(
                f"Unknown Layout Observer {type(observer)} cannot be removed")
            return

        sources = mapping["sources"]

        # Remove the observer from the layout map if it exists
        if observer in self._observer_layout_map:
            del self._observer_layout_map[observer]

        # If the observer was added to finalize list, remove it
        if mapping["finalize"] and observer in self._observers_to_finalize:
            self._observers_to_finalize.remove(observer)

        # Remove the observer from all associated layout sources
        for source in sources:
            source.remove_layout_observer(observer)

        print(f"Layout observer {type(observer)} removed.")

    def _set_observer_mapping(self, observer: IObserver, keys: List[str], sources: List[IPublisher], mapping: str) -> None:
        """
        Sets the data or layout mapping for an observer with specific keys and sources.

        Depending on the `mapping` argument, this method registers the observer
        to either the data or layout map. The method combines the states from the
        provided sources and creates a lambda function to filter the relevant keys
        for the observer.

        Args:
            observer (IObserver): The observer to register.
            keys (List[str]): A list of keys to extract from the state.
            sources (List[IPublisher]): A list of sources providing state dictionaries.
            mapping (str): Specifies the type of mapping ("data" or "layout") to register.
                        - "data": The observer is mapped to the data state.
                        - "layout": The observer is mapped to the layout state.

        Raises:
            ValueError: If `mapping` is not "data" or "layout".
            ValueError: If `keys` or `sources` are empty.
        """
        if not keys:
            raise ValueError("Keys cannot be empty.")
        if not sources:
            raise ValueError("Sources cannot be empty.")

        if mapping == "data":
            data = {key: value for source in sources for key,
                    value in source.get_data_state().items()}
            self._observer_data_map[observer] = lambda: {
                key: data[key] for key in keys if key in data}
        elif mapping == "layout":
            layout = {key: value for source in sources for key,
                      value in source.get_layout_state().items()}
            self._observer_layout_map[observer] = lambda: {
                key: layout[key] for key in keys if key in layout}
        else:
            raise ValueError("Invalid mapping type. Use 'data' or 'layout'.")

    def get_data_state(self, observer: IDataObserver) -> any:
        """
        Retrieves the updated data for a specific data observer.

        This method accesses the `_observer_data_map` to fetch the data
        processing logic associated with the given observer. It then
        executes this logic (typically a callable) to return the
        computed data for the observer.

        Args:
            observer (IDataObserver): The data observer requesting updated data.

        Returns:
            The computed data specific to the requesting observer.

        Raises:
            KeyError: If the provided observer is not registered in the
            `_observer_data_map`.
        """
        return self._observer_data_map[observer]()

    def get_layout_state(self, observer: ILayoutObserver) -> any:
        """
        Retrieves the updated layout information for a specific layout observer.

        This method accesses the `_observer_layout_map` to fetch the layout
        processing logic associated with the given observer. It then
        executes this logic (typically a callable) to return the
        computed layout information for the observer.

        Args:
            observer (ILayoutObserver): The layout observer requesting updated layout information.

        Returns:
            The computed layout information specific to the requesting observer.

        Raises:
            KeyError: If the provided observer is not registered in the
            `_observer_layout_map`.
        """
        return self._observer_layout_map[observer]()

    #!
    # todo Mockmethod
    def get_abbreviations(self) -> set[str]:
        """
        Loads abbreviations from a JSON file and returns the list of German abbreviations.

        Arguments:
            file_path (str): The path to the JSON file containing abbreviations. 
                            Defaults to "app_data/abbreviations.json".

        Returns:
            List[str]: A list of German abbreviations as strings.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            KeyError: If the "german" key is missing in the JSON file.
        """
        file_path = "app_data/abbreviations.json"
        try:
            # Load the JSON file
            with open(file_path, "r") as file:
                data = json.load(file)

            # Extract and return the list of German abbreviations
            return set(data["german"])
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in '{file_path}': {e.msg}", e.doc, e.pos)
        except KeyError:
            raise KeyError(
                f"The key 'german' is missing in the JSON file '{file_path}'.")

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

# Perform methods

    def perform_pdf_extraction(self, extraction_data: dict) -> None:
        extracted_text = self._pdf_extraction_manager.extract_document(
            extraction_data=extraction_data)
        self._preview_document_model.set_text(text=extracted_text)

    def perform_add_tag(self, tag_data: dict) -> None:
        """
        Creates and executes an AddTagCommand to add a new tag.

        Args:
            tag_data (dict): Data for the tag to be added.
        """
        command = AddTagCommand(self._tag_manager, tag_data)
        self._execute_command(command)

    def perform_edit_tag(self, tag_id: str, tag_data: dict) -> None:
        """
        Creates and executes an EditTagCommand to edit an existing tag.

        Args:
            tag_id (str): The ID of the tag to edit.
            tag_data (dict): The new data for the tag.
        """
        command = EditTagCommand(self._tag_manager, tag_id, tag_data)
        self._execute_command(command)

    def perform_delete_tag(self, tag_id: str) -> None:
        """
        Creates and executes a DeleteTagCommand to delete a tag.

        Args:
            tag_id (str): The ID of the tag to delete.
        """
        command = DeleteTagCommand(self._tag_manager, tag_id)
        self._execute_command(command)

    # performances
    def perform_text_selected(self, text: str) -> None:
        print(f"Text: {text} selected.")
