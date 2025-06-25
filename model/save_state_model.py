from typing import Dict, List


class SaveStateModel:
    """
    Tracks the dirty (unsaved) state of multiple views or modes by key.
    Used to determine whether a save prompt is required before critical actions.
    """

    def __init__(self) -> None:
        """Initializes the internal dictionary to track dirty flags per key."""
        self._dirty_flags: Dict[str, bool] = {}

    def set_dirty(self, key: str) -> None:
        """
        Marks the given key (e.g., view or mode) as dirty (unsaved changes exist).

        Args:
            key (str): Identifier for the view or mode.
        """
        self._dirty_flags[key] = True

    def set_clean(self, key: str) -> None:
        """
        Marks the given key as clean (no unsaved changes).

        Args:
            key (str): Identifier for the view or mode.
        """
        self._dirty_flags[key] = False

    def is_dirty(self, key: str) -> bool:
        """
        Checks whether the given key is currently marked as dirty.

        Args:
            key (str): Identifier for the view or mode.

        Returns:
            bool: True if dirty, False if clean or unknown.
        """
        return self._dirty_flags.get(key, False)

    def any_dirty(self) -> bool:
        """
        Checks whether any key is currently dirty.

        Returns:
            bool: True if at least one key is dirty, False otherwise.
        """
        return any(self._dirty_flags.values())

    def get_all_dirty_keys(self) -> List[str]:
        """
        Returns a list of all keys that are currently marked as dirty.

        Returns:
            List[str]: List of keys with unsaved changes.
        """
        return [key for key, dirty in self._dirty_flags.items() if dirty]

    def reset_all(self) -> None:
        """
        Clears all dirty flags, marking all keys as clean.
        """
        self._dirty_flags.clear()
