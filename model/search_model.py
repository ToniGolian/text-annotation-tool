from typing import List, Optional
from data_classes.search_Result import SearchResult
from observer.interfaces import IPublisher


class SearchModel(IPublisher):
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
            "current_result": current_result,
            "results": self._results
        }

    # getters
    def get_current_result(self) -> Optional[SearchResult]:
        """
        Retrieves the currently selected search result.

        Returns:
            Optional[SearchResult]: The current result or None if no valid selection exists.
        """
        if 0 <= self._current_index < len(self._results):
            return self._results[self._current_index]
        return None

#!DEBUG
    def print_results(self) -> None:
        """
        Prints the current search results to the console for debugging purposes.
        """
        print("Search Results:")
        for i, result in enumerate(self._results):
            print(f"{i}: {result.term} ({result.start}-{result.end})")
        print(f"Current Index: {self._current_index}")
