from controller.interfaces import IController
from commands.interfaces import ICommand
from model.interfaces import IComparisonModel, IDocumentModel
from utils.interfaces import IObserver, IPublisher
from typing import Dict, List, Sequence
import tkinter as tk

from view.comparison_text_display_frame import ComparisonTextDisplayFrame
from view.comparison_text_displays import ComparisonTextDisplays
from view.text_display_frame import TextDisplayFrame


class MockController(IController):
    def __init__(self, text_model: IPublisher, tag_model: IPublisher, comparison_model: IPublisher):
        self._text_model = text_model
        self.tag_model = tag_model
        self._comparison_model = comparison_model

        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observers_to_finalize: List = []

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
    def add_observer(self, observer: IObserver) -> None:
        if isinstance(observer, TextDisplayFrame):
            self._observer_data_map[observer] = lambda: {
                "data": self._text_model.get_data()["text"]}
            self._text_model.add_observer(observer=observer)

        elif isinstance(observer, ComparisonTextDisplays):
            self._observer_data_map[observer] = lambda: {
                "data": self._comparison_model.get_data()["file_names"]}
            self._observers_to_finalize.append(observer)

        elif isinstance(observer, ComparisonTextDisplayFrame):
            self._observer_data_map[observer] = lambda: {
                "data": self._comparison_model.get_data()["comparison_sentences"][self._dynamic_observer_index]}
            self._dynamic_observer_index += 1
            self._comparison_model.add_observer(observer)
            print(
                f"Comparison Observer {self._dynamic_observer_index} registered")
        else:
            print("Other Observer registered")

    def remove_observer(self, observer: IObserver) -> None:
        print("observer removed")

    def get_update_data(self, observer: IObserver) -> None:
        """
        Retrieves the updated data for a specific observer.

        This method accesses the `_observer_data_map` to fetch the data
        processing logic associated with the given observer. It then
        executes this logic (typically a lambda function) to return the
        computed data for the observer.

        Args:
            observer (IObserver): The observer requesting updated data.

        Raises:
            KeyError: If the provided observer is not registered in the
            `_observer_data_map`.
        """
        return self._observer_data_map[observer]()

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
