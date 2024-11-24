from controller.interfaces import IController
from commands.interfaces import ICommand
from mockclasses.mock_commands import MockAddTagCommand, MockDeleteTagCommand, MockEditTagCommand
from mockclasses.mock_tag_manager import MockTagManager
from model.interfaces import IComparisonModel, IDocumentModel
from utils.interfaces import IObserver, IPublisher
from typing import Dict, List, Sequence
import tkinter as tk

from view.comparison_text_display_frame import ComparisonTextDisplayFrame
from view.comparison_text_displays import ComparisonTextDisplays
from view.text_display_frame import TextDisplayFrame


class MockController(IController):
    def __init__(self, document_model: IPublisher, tag_model: IPublisher, comparison_model: IPublisher):
        self._document_model = document_model
        self._comparison_model = comparison_model
        self._tag_manager = TagManager(self._document_model)

        self._dynamic_observer_index: int = 0
        self._observer_data_map: Dict[IObserver:Dict] = {}
        self._observers_to_finalize: List = []

        self._undo_stack = []  # Stack to store commands for undo operations
        self._redo_stack = []  # Stack to store commands for redo operations

    # command pattern
    def _execute_command(self, command) -> None:
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

    def add_observer(self, observer: IObserver) -> None:
        if isinstance(observer, TextDisplayFrame):
            self._observer_data_map[observer] = lambda: {
                "data": self._document_model.get_data()["text"]}
            self._document_model.add_observer(observer=observer)

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
