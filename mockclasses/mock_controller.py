
from controller.interfaces import IController
from commands.interfaces import ICommand
from model.interfaces import IComparisonModel
from utils.interfaces import IDataObserver, IDataPublisher, ILayoutObserver, ILayoutPublisher,  IObserver, IPublisher
from typing import Dict, List, Any, Sequence

from view.interfaces import IAnnotationMenuFrame, IComparisonHeaderFrame, IComparisonTextDisplayFrame, IComparisonTextDisplays, IMetaTagsFrame, ITextDisplayFrame


class MockController(IController):
    def __init__(self, text_model: IDataPublisher, comparison_model: IComparisonModel, configuration_model: ILayoutPublisher):
        """
        Initializes the MockController with models and observer management.

        Args:
            text_model (IDataPublisher): The model responsible for managing and publishing data updates for text.
            comparison_model (IDataPublisher & ILayoutPublisher): The model responsible for managing and publishing 
                both data and layout updates for comparisons.
        """
        self._text_model: IDataPublisher = text_model
        self._comparison_model: IComparisonModel = comparison_model
        self._configuration_manager: ILayoutPublisher = configuration_model

        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IDataObserver, Dict] = {}
        self._observer_layout_map: Dict[ILayoutObserver, Dict] = {}
        self._observers_to_finalize: List[IObserver] = []

    # command pattern
    def execute_command(self, command: ICommand) -> None:
        """Executes the specified command."""
        print("Controller execute command")

    def undo(self, command: ICommand) -> None:
        """Reverses the actions of the specified command."""
        print("Controller undo command")

    def redo(self, command: ICommand) -> None:
        """Reapplies the actions of the specified command."""
        print("Controller redo command")

    # observer pattern
    def add_data_observer(self, observer: IDataObserver) -> None:
        """
        Registers a data observer and maps its data-fetching logic.

        Args:
            observer (IDataObserver): The data observer to be added.
        """
        if isinstance(observer, ITextDisplayFrame):
            keys = ["text"]
            sources = [self._text_model]
            self._set_observer_mapping(observer, keys, sources, "data")
            self._text_model.add_data_observer(observer)

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
                "sentence": self._comparison_model.get_data_state()["comparison_sentences"][index]
            }

            self._comparison_model.add_data_observer(observer)

        else:
            print(f"Unknown Data Observer {type(observer)} registered")

    def add_layout_observer(self, observer: ILayoutObserver) -> None:
        """
        Registers a layout observer and maps its layout-fetching logic.

        Args:
            observer (ILayoutObserver): The layout observer to be added.
        """
        # standard source. observers can add additional sources
        sources = [self._configuration_manager]

        if isinstance(observer, (IComparisonTextDisplays, IComparisonHeaderFrame)):
            keys = ["filenames", "num_files"]
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

    def remove_data_observer(self, observer: IDataObserver) -> None:
        print(f"{type(observer)} removed")

    def remove_layout_observer(self, observer: ILayoutObserver) -> None:
        print(f"{type(observer)} removed")

    def get_data_state(self, observer: IDataObserver) -> None:
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

    def get_layout_state(self, observer: ILayoutObserver) -> None:
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
            observer.update_layout()

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

    #!depr

    def get_template_groups(self) -> Sequence:
        """Returns the Groups of templates for the dynamic creation of Tagging menu frames """
        return [{"group_name": "Group1", "templates": [{
            "type": "TIMEX1",
            "attributes": {
                "tid": {
                    "active": True,
                    "type": "ID"
                },
                "type": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                },
                "functionInDocument": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["CREATION_TIME", "EXPIRATION_TIME", "MODIFICATION_TIME", "PUBLICATION_TIME", "RELEASE_TIME", "RECEPTION_TIME", "NONE"],
                    "default": "NONE"
                },
                "endPoint": {
                    "active": True,
                    "type": "IDREF"
                }
            }
        },
            {
            "type": "TIMEX2",
            "attributes": {
                "tid": {
                    "active": True,
                    "type": "ID"
                },
                "type": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                },
                "functionInDocument": {
                    "active": True,
                    "type": "string",
                    "allowedValues": ["CREATION_TIME", "EXPIRATION_TIME", "MODIFICATION_TIME", "PUBLICATION_TIME", "RELEASE_TIME", "RECEPTION_TIME", "NONE"],
                    "default": "NONE"
                },
                "beginPoint": {
                    "active": True,
                    "type": "IDREF"
                }
            }
        }]}, {"group_name": "Group2", "templates": [
            {
                "type": "TIMEX3",
                "attributes": {
                    "tid": {
                        "active": True,
                        "type": "ID"
                    },
                    "type": {
                        "active": True,
                        "type": "string",
                        "allowedValues": ["DATE", "TIME", "DURATION", "SET"]
                    },
                    "functionInDocument": {
                        "active": True,
                        "type": "string",
                        "allowedValues": ["A", "B", "C", "D", "E", "F", "G"],
                        "default": "NONE"
                    },
                    "anchorPoint": {
                        "active": True,
                        "type": "IDREF"
                    }
                }
            }
        ]}]

    def get_meta_tag_labels(self):
        return ["a-Tag", "b-Tag", "c-Tag"]
