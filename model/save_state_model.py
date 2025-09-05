class SaveStateModel:
    """
    Tracks the save state of multiple document modes using a change counter.

    This model allows tracking whether the current state of a document mode
    has unsaved changes by counting how many modifications have been made
    since the last save. A mode is considered 'clean' if its counter is zero.

    This supports undo/redo logic: each executed or redone command increments
    the counter, while each undo decrements it, without going below zero.
    """

    def __init__(self) -> None:
        """
        Initializes the SaveStateModel with an empty dictionary of change counters.
        """
        self._change_counts: dict[str, int] = {}

    def reset_key(self, key: str) -> None:
        """
        Marks the state of the given key (mode) as clean by resetting its counter.

        Args:
            key (str): The identifier of the document mode.
        """
        self._change_counts[key] = 0

    def reset(self) -> None:
        """
        Resets the change counters for all tracked keys (modes), marking them as clean.
        """
        self._change_counts = {}

    def increment(self, key: str) -> None:
        """
        Increments the change counter for the given key (used on execute/redo).

        Args:
            key (str): The identifier of the document mode.
        """
        self._change_counts[key] = self._change_counts.get(key, 0) + 1

    def decrement(self, key: str) -> None:
        """
        Decrements the change counter for the given key (used on undo).
        The counter will never go below zero.

        Args:
            key (str): The identifier of the document mode.
        """
        self._change_counts[key] = max(0, self._change_counts.get(key, 0) - 1)

    def is_dirty(self, key: str) -> bool:
        """
        Returns whether the state for the given key has unsaved changes.

        A mode is considered dirty if its change counter is greater than zero.

        Args:
            key (str): The identifier of the document mode.

        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        return self._change_counts.get(key, 0) > 0

    def get_dirty_keys(self) -> list[str]:
        """
        Returns a list of keys (document modes) that have unsaved changes.

        Returns:
            list[str]: A list of identifiers for modes that are dirty.
        """
        return [key for key, count in self._change_counts.items() if count > 0]
