from typing import Dict, Union
from observer.interfaces import IPublisher


class SelectionModel(IPublisher):
    """
    A model to manage and publish the currently selected text and its position to its observers.
    """

    def __init__(self) -> None:
        """
        Initializes the SelectionModel with no selected text or position.
        """
        super().__init__()  # Initializes _data_observers from the base class
        self._selected_text = ""
        self._position = -1
        self._suggestions = {}

    def set_selected_text_data(self, data: Dict[str, Union[str, int]]) -> None:
        """
        Sets the currently selected text and its position, then notifies all observers.

        Args:
            data (Dict[str, Union[str, int]]): A dictionary containing:
                - "selected_text" (str): The newly selected text.
                - "position" (int): The starting position of the selected text.
                - "suggestions" (Dict[str, str]): A dictionary of suggestion terms and their corresponding metadata.
        """
        self._selected_text = data.get("selected_text", "")
        self._position = data.get("position", -1)
        self._suggestions = data.get("suggestions", {})
        self.notify_observers()

    def get_state(self) -> Dict[str, Union[str, int]]:
        """
        Retrieves the current selected text and its position as a dictionary.

        Returns:
            Dict[str, Union[str, int]]: A dictionary containing the selected text and its position.
        """
        return {
            "selected_text": self._selected_text,
            "position": self._position,
            "suggestions": self._suggestions
        }
