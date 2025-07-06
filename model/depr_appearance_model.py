from observer.interfaces import IPublisher


class AppearanceModel(IPublisher):
    """
    Manages dynamic appearance settings related to the display of annotation components.

    This model is responsible for tracking dynamically created UI elements such as annotator displays,
    ensuring that their creation and updates are managed independently from the document models.
    """

    def __init__(self):
        """
        Initializes the AppearanceModel with default values for dynamic UI components.
        """
        super().__init__()
        self._num_comparison_displays = 0
        self._active_notebook_index = 0

    def get_num_comparison_displays(self) -> int:
        """
        Retrieves the number of comparison displays.

        Returns:
            int: The number of comparison displays.
        """
        return self._num_comparison_displays

    def set_num_comparison_displays(self, num_comparison_displays: int) -> None:
        """
        Sets the number of dynamically created comparison displays.

        Args:
            num_comparison_displays (int): The number of comparison displays.
        """
        self._num_comparison_displays = num_comparison_displays
        self.notify_observers()

    def get_active_notebook_index(self) -> int:
        """
        Retrieves the index of the currently active notebook tab.

        Returns:
            int: The index of the active notebook tab.
        """
        return self._active_notebook_index

    def set_active_notebook_index(self, index: int) -> None:
        """
        Sets the index of the currently active notebook tab.

        Args:
            index (int): The index to set as active.
        """
        self._active_notebook_index = index
        self.notify_observers()

    def get_state(self) -> dict:
        """
        Retrieves the current state of the appearance model.

        Returns:
            dict: A dictionary containing:
                - "num_comparison_displays" (int): The number of dynamically created comparison displays.
                - "active_notebook_index" (int): The index of the currently active notebook tab.
        """
        return {
            "num_comparison_displays": self._num_comparison_displays,
            "active_notebook_index": self._active_notebook_index
        }
