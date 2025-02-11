
from controller.interfaces import IController
from commands.interfaces import ICommand
from mockclasses.mock_commands import MockAddTagCommand, MockDeleteTagCommand, MockEditTagCommand
from mockclasses.mock_tag_manager import MockTagManager
from model.interfaces import IComparisonModel
from observer.interfaces import IObserver, IPublisher, IObserver, IPublisher,  IObserver, IPublisher
from typing import Dict, List
import json

from view.interfaces import IAnnotationMenuFrame, IComparisonHeaderFrame, IComparisonTextDisplayFrame, IComparisonTextDisplays, IMetaTagsFrame, ITextDisplayFrame


class MockController(IController):
    def __init__(self, document_model: IPublisher, comparison_model: IComparisonModel, configuration_model: IPublisher):
        """
        Initializes the MockController with models and observer management.

        Args:
            text_model (IDataPublisher): The model responsible for managing and publishing data updates for text.
            comparison_model (IDataPublisher & ILayoutPublisher): The model responsible for managing and publishing 
                both data and layout updates for comparisons.
        """
        self._document_model: IPublisher = document_model
        self._comparison_model: IComparisonModel = comparison_model
        self._configuration_manager: IPublisher = configuration_model

        self._tag_manager = MockTagManager(self._document_model)

        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver, Dict] = {}
        self._observer_layout_map: Dict[IObserver, Dict] = {}
        self._observers_to_finalize: List[IObserver] = []

    # command pattern
    def _execute_command(self, command: ICommand) -> None:
        """Executes the specified command."""
        print(f"Controller execute {command}")

    def undo_command(self, command: ICommand) -> None:
        """Reverses the actions of the specified command."""
        print(f"Controller undo {command}")

    def redo_command(self, command: ICommand) -> None:
        """Reapplies the actions of the specified command."""
        print(f"Controller redo {command}")

    # observer pattern
    def add_data_observer(self, observer: IObserver) -> None:
        """
        Registers a data observer and maps its data-fetching logic.

        Args:
            observer (IDataObserver): The data observer to be added.
        """
        if isinstance(observer, ITextDisplayFrame):
            keys = ["text"]
            sources = [self._document_model]
            self._set_observer_mapping(observer, keys, sources, "data")
            self._document_model.add_data_observer(observer)

        elif isinstance(observer, IMetaTagsFrame):
            keys = ["file_names"]
            sources = [self._comparison_model]
            self._set_observer_mapping(observer, keys, sources, "data")
            self._comparison_model.add_data_observer(observer)
            self._observers_to_finalize.append(observer)
        elif isinstance(observer, IComparisonTextDisplays):
            keys = ["file_names"]
            sources = [self._comparison_model]
            self._set_observer_mapping(observer, keys, sources, "data")
            self._comparison_model.add_data_observer(observer)
            self._observers_to_finalize.append(observer)

        elif isinstance(observer, IComparisonHeaderFrame):
            keys = ["num_sentences", "current_sentence_index"]
            sources = [self._comparison_model]
            self._set_observer_mapping(observer, keys, sources, "data")
            self._comparison_model.add_data_observer(observer)
            self._observers_to_finalize.append(observer)

        elif isinstance(observer, IComparisonTextDisplayFrame):
            # Dynamically map the observer to a specific sentence in the list
            index = self._dynamic_observer_index  # Use the current dynamic observer index
            self._dynamic_observer_index += 1

            # Use a lambda to extract the specific sentence based on the index
            self._observer_data_map[observer] = lambda index=index: {
                "sentence": self._comparison_model.get_state()["comparison_sentences"][index]
            }

            self._comparison_model.add_data_observer(observer)

        else:
            print(f"Unknown Data Observer {type(observer)} registered")

    def add_layout_observer(self, observer: IObserver) -> None:
        """
        Registers a layout observer and maps its layout-fetching logic.

        Args:
            observer (ILayoutObserver): The layout observer to be added.
        """
        # standard source. observers can add additional sources
        sources = [self._configuration_manager]

        if isinstance(observer, (IComparisonTextDisplays, IComparisonHeaderFrame)):
            keys = ["file_names", "num_files"]
        elif isinstance(observer, IMetaTagsFrame):
            keys = ["tag_types"]
        elif isinstance(observer, IAnnotationMenuFrame):
            keys = ["template_groups"]
        else:
            keys = []
            print(f"Unknown Layout Observer {type(observer)} registered")

        self._set_observer_mapping(observer, keys, sources, "layout")
        self._comparison_model.add_layout_observer(observer)
        self._observers_to_finalize.append(observer)

    def remove_data_observer(self, observer: IObserver) -> None:
        print(f"{type(observer)} removed")

    def remove_layout_observer(self, observer: IObserver) -> None:
        print(f"{type(observer)} removed")

    def get_state(self, observer: IObserver) -> None:
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

    def get_layout_state(self, observer: IObserver) -> None:
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

    # performances

    def perform_text_selected(self, text: str) -> None:
        print(f"Text: {text} selected.")

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
            observer.update()

    # helpers
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
        """
        if mapping == "data":
            data = {key: value for source in sources for key,
                    value in source.get_state().items()}
            self._observer_data_map[observer] = lambda: {
                key: data[key] for key in keys if key in data}
        elif mapping == "layout":
            layout = {key: value for source in sources for key,
                      value in source.get_layout_state().items()}
            self._observer_layout_map[observer] = lambda: {
                key: layout[key] for key in keys if key in layout}
        else:
            raise ValueError("Invalid mapping type. Use 'data' or 'layout'.")

    def perform_add_tag(self, tag_data: dict) -> None:
        """
        Creates and executes an AddTagCommand to add a new tag.

        Args:
            tag_data (dict): Data for the tag to be added.
        """
        command = MockAddTagCommand(self._tag_manager, tag_data)
        self._execute_command(command)

    def perform_edit_tag(self, tag_id: str, tag_data: dict) -> None:
        """
        Creates and executes an EditTagCommand to edit an existing tag.

        Args:
            tag_id (str): The ID of the tag to edit.
            tag_data (dict): The new data for the tag.
        """
        command = MockEditTagCommand(self._tag_manager, tag_id, tag_data)
        self._execute_command(command)

    def perform_delete_tag(self, tag_id: str) -> None:
        """
        Creates and executes a DeleteTagCommand to delete a tag.

        Args:
            tag_id (str): The ID of the tag to delete.
        """
        command = MockDeleteTagCommand(self._tag_manager, tag_id)
        self._execute_command(command)
