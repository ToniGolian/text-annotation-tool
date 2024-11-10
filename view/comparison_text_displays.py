from typing import Dict, List
from utils.interfaces import IObserver, IPublisher
from controller.interfaces import IController
from view.text_display_frame import TextDisplayFrame
import tkinter as tk


class ComparisonTextDisplays(tk.Frame, IObserver):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the ComparisonTextDisplays with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller: IController = controller

        self._different_documents: List = []
        self._widget_structure = []

        self._controller.register_observer(self)

        self._render()

    def _render(self) -> None:
        """
        Clears all existing widgets (except the first label and TextDisplayFrame pair),
        reconfigures the widgets according to self._different_documents,
        and updates the layout with the new widgets.
        """
        # Remove all existing widgets from the frame, except the first pair
        for widgets in self._widget_structure:
            for widget in widgets:
                widget.destroy()

        # Clear the old widget structure and reconfigure widgets based on updated data
        self._reconfigure_widgets()

        # First Label and TextDisplayFrame for "Original Text:"
        self.original_label = tk.Label(self, text="Original Text:")
        self.original_text_display = TextDisplayFrame(self, self._controller)
        self.original_label.pack(anchor="w", pady=(5, 2))
        self.original_text_display.pack(fill="both", expand=True, pady=(0, 10))

        # Add the new widgets to the layout
        for label, text_display_frame in self._widget_structure:
            label.pack(anchor="w", pady=(5, 2))
            text_display_frame.pack(fill="both", expand=True, pady=(0, 10))

    def _reconfigure_widgets(self) -> None:
        """
        Reconfigures the widgets based on the current state of self._different_documents.
        Creates a new Label and TextDisplayFrame pair for each document and updates self._widget_structure.
        """
        self._widget_structure = []

        for doc in self._different_documents:
            # Create a label with the document's filename
            label = tk.Label(self, text=doc["filename"])

            # Create a TextDisplayFrame for displaying the document's content
            text_display_frame = TextDisplayFrame(self)

            # Add the label and text display frame as a pair in the widget structure
            self._widget_structure.append((label, text_display_frame))

    # todo unify the updates
    def update(self, publisher: IPublisher) -> None:
        """
        Updates the text displays with new content from the specified publisher.

        Args:
            publisher (IPublisher): The publisher providing the updated data. The data is retrieved
                from the controller, which interacts with the publisher to get relevant content.

        Note:
            The method assumes that the number of sentences returned by the controller matches
            the number of text displays in self._text_displays.
        """
        sentences = self._controller.get_update_data(publisher)
        for index, text_display in enumerate(self._text_displays):
            text_display.delete("1.0", tk.END)
            text_display.insert("1.0", sentences[index])

    def set_different_documents(self, documents: List[Dict]) -> None:
        """
        Sets multiple documents and their associated filenames from a list of dictionaries.

        Args:
            text_dicts (List[Dict]): A list of dictionaries, each containing keys "text" and "filename".
                - "text" (str): The text content to be set.
                - "filename" (str): The filename associated with the text.

        Updates:
            - self._different_texts: A list of text contents extracted from each dictionary in text_dicts.
            - self._filenames: A list of filenames associated with each text.
            - self._num_different_texts: The total count of different texts set.
        """
        self._different_documents = documents
        self._render()
