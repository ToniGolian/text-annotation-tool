from typing import List, Tuple
from model.interfaces import IPublisher


class HighlightModel(IPublisher):
    """
    A model that manages and publishes highlight data for display in the view.

    This model separates highlights originating from tag annotations and search results,
    allowing independent updates and deletions. The combined state can be retrieved
    for use in visual rendering.

    Attributes:
        _tag_highlights (List[Tuple[str, int, int]]): Highlights from tag annotations.
        _search_highlights (List[Tuple[str, int, int]]): Highlights from search results.
        _observers (List[ICallback]): Registered observers for state change notifications.
    """

    def __init__(self) -> None:
        """
        Initializes the HighlightModel with empty tag and search highlight lists.
        """
        self._tag_highlights: List[Tuple[str, int, int]] = []
        self._search_highlights: List[Tuple[str, int, int]] = []
        self._observers = []

    def add_tag_highlights(self, highlights: List[Tuple[str, int, int]]) -> None:
        """
        Replaces the current tag highlights with a new set.

        Args:
            highlights (List[Tuple[str, int, int]]): A list of tag highlights, each as a tuple of
                (color, start_position, end_position).
        """
        self._tag_highlights = highlights
        self._notify_observers()

    def add_search_highlights(self, highlights: List[Tuple[str, int, int]]) -> None:
        """
        Replaces the current search highlights with a new set.

        Args:
            highlights (List[Tuple[str, int, int]]): A list of search highlights, each as a tuple of
                (color, start_position, end_position).
        """
        self._search_highlights = highlights
        self._notify_observers()

    def clear_search_highlights(self) -> None:
        """
        Clears all search highlights and notifies observers.
        """
        self._search_highlights = []
        self._notify_observers()

    def get_state(self) -> List[Tuple[str, int, int]]:
        """
        Returns the combined highlight data from tags and searches.

        Returns:
            List[Tuple[str, int, int]]: A list of all current highlights.
        """
        return self._tag_highlights + self._search_highlights
