from typing import List, Optional
from data_classes.search_Result import SearchResult


class SearchModel:
    """
    Manages a list of search results and provides indexed navigation.

    This model maintains a list of matched search terms along with their
    respective character index positions in the source text. It supports
    adding, clearing, and navigating through results via an internal iterator.
    It also provides validity tracking to indicate whether the results are up-to-date.
    """

    def __init__(self):
        """
        Initializes the search model with an empty result set.

        The model starts with no entries, no selection, and is marked as valid.
        """
        self._results: List[SearchResult] = []
        self._current_index: int = -1
        self._valid: bool = True

    def add_result(self, term: str, start: int, end: int) -> None:
        """
        Adds a new search result to the internal list.

        This method appends a new SearchResult instance containing
        the term and its position to the model's result list.

        Args:
            term (str): The search term to be added.
            start (int): The start character index in the text.
            end (int): The end character index in the text.
        """
        self._results.append(SearchResult(term, start, end))

    def clear_results(self) -> None:
        """
        Removes all stored search results and resets the internal index.

        After this call, the result list is empty and no result is selected.
        """
        self._results.clear()
        self._current_index = -1

    def get_all_results(self) -> List[SearchResult]:
        """
        Retrieves the complete list of search results.

        This method returns all stored search results in the order they were added.

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

    def get_current_result(self) -> Optional[SearchResult]:
        """
        Retrieves the currently selected search result.

        This method returns the result at the current index if valid,
        or None if no result is selected.

        Returns:
            Optional[SearchResult]: The active search result, or None.
        """
        if 0 <= self._current_index < len(self._results):
            return self._results[self._current_index]
        return None

    def next_result(self) -> Optional[SearchResult]:
        """
        Advances to the next search result in the list.

        The internal index is incremented, wrapping around to the beginning
        if the end of the list is reached.

        Returns:
            Optional[SearchResult]: The newly selected search result, or None if the list is empty.
        """
        if not self._results:
            return None
        self._current_index = (self._current_index + 1) % len(self._results)
        return self._results[self._current_index]

    def previous_result(self) -> Optional[SearchResult]:
        """
        Moves to the previous search result in the list.

        The internal index is decremented, wrapping around to the end
        if the beginning of the list is passed.

        Returns:
            Optional[SearchResult]: The newly selected search result, or None if the list is empty.
        """
        if not self._results:
            return None
        self._current_index = (self._current_index - 1) % len(self._results)
        return self._results[self._current_index]

    def is_valid(self) -> bool:
        """
        Indicates whether the search model is currently valid.

        The validity flag is used to determine whether the stored results are
        up-to-date. This is typically evaluated by the accessor or controller
        before using the model in a search operation.

        Returns:
            bool: True if the model is valid and current, False otherwise.
        """
        return self._valid

    def invalidate(self) -> None:
        """
        Marks the search model as invalid.

        This should be called when the input data or configuration changes in
        a way that renders the current results outdated.
        """
        self._valid = False

    def validate(self) -> None:
        """
        Marks the search model as valid.

        This should be called after the model has been fully (re)computed
        and the results are considered current.
        """
        self._valid = True
