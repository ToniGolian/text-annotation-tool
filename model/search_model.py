from typing import List, Optional
from data_classes.search_Result import SearchResult
from observer.interfaces import IPublisher


class SearchModel(IPublisher):
    """
    Manages a list of search results and maintains the current selection state.

    Instead of returning results directly, this model maintains an internal
    current index and notifies observers whenever it changes.
    It also provides validity tracking to signal whether the model contents are up-to-date.
    """

    def __init__(self):
        """
        Initializes the search model with an empty result set and a valid state.

        The model starts with no entries, no selection, and a validity flag set to True.
        """
        super().__init__()
        self._results: List[SearchResult] = []
        self._current_index: int = -1
        self._valid: bool = True

    def add_result(self, term: str, start: int, end: int) -> None:
        """
        Adds a new search result to the internal list.

        Args:
            term (str): The search term to be added.
            start (int): The start character index in the text.
            end (int): The end character index in the text.
        """
        self._results.append(SearchResult(term, start, end))

    def clear_results(self) -> None:
        """
        Removes all stored search results, resets the selection index,
        and notifies observers that the state has changed.
        """
        self._results.clear()
        self._current_index = -1
        self.notify_observers()

    def get_all_results(self) -> List[SearchResult]:
        """
        Retrieves the complete list of search results.

        Returns:
            List[SearchResult]: A list of all current search results.
        """
        return self._results

    def has_results(self) -> bool:
        """
        Checks whether any search results are currently stored.

        Returns:
            bool: True if the result list is non-empty, False otherwise.
        """
        return bool(self._results)

    def next_result(self) -> None:
        """
        Advances to the next search result and notifies observers.

        Wraps around to the beginning if the end of the list is reached.
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

        Wraps around to the end if the beginning of the list is passed.
        """
        if not self._results:
            return
        if self._current_index <= 0:
            self._current_index = len(self._results) - 1
        else:
            self._current_index -= 1
        self.notify_observers()

    def trigger_current_result(self) -> None:
        """
        Notifies observers of the current result without changing the selection.

        This can be used to explicitly trigger a UI update or state sync.
        """
        self.notify_observers()

    def is_valid(self) -> bool:
        """
        Indicates whether the search model is currently valid.

        Returns:
            bool: True if the model is valid and current, False otherwise.
        """
        return self._valid

    def invalidate(self) -> None:
        """
        Marks the search model as invalid.
        """
        self._valid = False

    def validate(self) -> None:
        """
        Marks the search model as valid.
        """
        self._valid = True

    def get_state(self) -> Optional[SearchResult]:
        """
        Returns the currently selected SearchResult instance.

        This method provides external components with the current state information,
        which is typically used in observer callbacks or UI updates.

        Returns:
            Optional[SearchResult]: The active SearchResult or None if no result is selected.
        """
        if 0 <= self._current_index < len(self._results):
            return self._results[self._current_index]
        return None
