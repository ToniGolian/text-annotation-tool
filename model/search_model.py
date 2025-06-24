from typing import List, Optional
from data_classes.search_result import SearchResult
from model.interfaces import ISearchModel


class SearchModel(ISearchModel):
    """
    Manages a list of search results and maintains the current selection state.

    This model supports navigation and state broadcasting via the observer pattern.
    Only one model is active at a time; inactive models suppress observer notifications.
    """

    def __init__(self):
        """
        Initializes the search model with an empty result set and a valid, inactive state.
        """
        super().__init__()
        self._results: List[SearchResult] = []
        self._current_index: int = -1
        self._valid: bool = True
        self._is_active: bool = False
        self._search_options = {}

    def add_result(self, search_result: SearchResult) -> None:
        """
        Adds a new search result to the internal list.

        Args:
            term (str): The matched term.
            start (int): Start index in the text.
            end (int): End index in the text.
        """
        self._results.append(search_result)

    def next_result(self) -> None:
        """
        Advances to the next search result and notifies observers.

        Wraps to the beginning when reaching the end of the list.
        """
        if not self._results:
            return
        if self._current_index == -1 or self._current_index >= len(self._results) - 1:
            self._current_index = 0
        else:
            self._current_index += 1
        self.notify_observers()

    def previous_result(self) -> None:
        """
        Moves to the previous search result and notifies observers.

        Wraps to the end when at the beginning of the list.
        """
        if not self._results:
            return
        if self._current_index <= 0:
            self._current_index = len(self._results) - 1
        else:
            self._current_index -= 1
        self.notify_observers()

    def activate(self) -> None:
        """
        Marks the model as active, allowing it to notify observers.
        """
        self._is_active = True

    def deactivate(self) -> None:
        """
        Marks the model as inactive, suppressing observer notifications.
        """
        self._is_active = False

    def invalidate(self) -> None:
        """
        Marks the model as invalid, triggering recalculation on next use.
        """
        self._valid = False

    def validate(self) -> None:
        """
        Marks the model as valid after a successful calculation.
        """
        self._valid = True

    def is_valid(self) -> bool:
        """
        Checks whether the model is currently valid.

        Returns:
            bool: True if the model is valid, False otherwise.
        """
        return self._valid

    def delete_current_result(self) -> None:
        """
        Deletes the currently selected search result and updates the selection.

        If the current index is invalid after deletion, it resets to -1.
        """
        if 0 <= self._current_index < len(self._results):
            del self._results[self._current_index]
            if not self._results:
                self._current_index = -1
            elif self._current_index >= len(self._results):
                self._current_index = len(self._results) - 1
            self.notify_observers()

    # observerpattern
    def notify_observers(self) -> None:
        """
        Notifies observers if the model is active.
        """
        if self._is_active:
            super().notify_observers()

    def get_state(self) -> dict:
        """
        Returns the current state of the search model, including the selected result
        and the full list of results.

        Returns:
            dict: A dictionary with the following keys:
                - 'current_result' (Optional[SearchResult]): The selected result or None.
                - 'results' (List[SearchResult]): The full list of results (can be empty).
        """
        current_result = (
            self._results[self._current_index]
            if 0 <= self._current_index < len(self._results)
            else None
        )
        return {
            "current_search_result": current_result,
            "results": self._results
        }

    def reset(self) -> None:
        """
        Resets the search model to its initial state, clearing all results and selection.
        """
        self._results.clear()
        self._current_index = -1
        self._valid = True
        self._is_active = False

    def get_current_index(self) -> int:
        """
        Returns the current index of the selected search result.

        Returns:
            int: The current index, or -1 if no result is selected.
        """
        return self._current_index

    def set_current_index(self, index: int) -> None:
        """
        Sets the current index to a specific value and notifies observers.

        Args:
            index (int): The new index to set.
        """
        if 0 <= index < len(self._results):
            self._current_index = index
            self.notify_observers()
        else:
            raise IndexError("Index out of bounds for search results.")

    def get_search_options(self) -> dict:
        """
        Returns the current search options.

        Returns:
            dict: The search options used for the current search.
        """
        return self._search_options

    def set_search_options(self, options: dict) -> None:
        """
        Sets the search options for the current search.

        Args:
            options (dict): A dictionary of search options.
        """
        self._search_options = options
