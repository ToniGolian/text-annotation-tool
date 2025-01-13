from typing import Dict

from observer.interfaces import IDataPublisher


class SelectionModel(IDataPublisher):
    """
    A model to manage and publish the currently selected text to its observers.
    """

    def __init__(self) -> None:
        """
        Initializes the SelectionModel with no selected text.
        """
        super().__init__()  # Initializes _data_observers from the base class
        self._selected_text: str = ""

    def set_selected_text(self, text: str) -> None:
        """
        Sets the currently selected text and notifies all observers.

        Args:
            text (str): The newly selected text.
        """
        self._selected_text = text
        self.notify_data_observers()

    def get_data_state(self) -> Dict[str, str]:
        """
        Retrieves the current selected text as a dictionary.

        Returns:
            Dict[str, str]: A dictionary containing the selected text.
        """
        return {"selected_text": self._selected_text}
