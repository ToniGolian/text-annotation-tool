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

    def get_num_comparison_displays(self) -> int:
        """
        Retrieves the number comparison displays.

        Returns:
            int: The number of comparison displays.
        """
        return self._num_comparison_displays

    def set_num_comparison_displays(self, num_comparison_displays: int) -> None:
        """
        Sets the number of dynamically comparison displays.

        Args:
            num_comparison_displays (int): The number of comparison displays.
        """
        self._num_comparison_displays = num_comparison_displays
        self.notify_observers()

    def get_state(self) -> dict:
        """
        Retrieves the current state of the appearance model.

        Returns:
            dict: A dictionary containing:
                - "num_comparison_displays" (int): The number of dynamically created comparison displays.
        """
        return {"num_comparison_displays": self._num_comparison_displays}
