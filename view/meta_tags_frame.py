import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from typing import List, Dict

from view.interfaces import IMetaTagsFrame


class MetaTagsFrame(tk.Frame, IMetaTagsFrame):
    """
    A tkinter Frame that displays meta tag information and provides options to save data.

    Attributes:
        _meta_tag_labels (List[str]): A list of labels for meta tags.
        controller (IController): The controller managing interactions with this frame.
    """

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the MetaTagsFrame with a controller and meta tag labels.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller for handling interactions.
            meta_tag_labels (List[str]): A list of labels for meta tags to display.
        """
        super().__init__(parent)

        self._controller = controller

        # data state
        self._meta_tag_data = []
        self._filename = ""

        # layout state
        self._tag_types = []

        # layout elements
        self._filename_label = self._filename_label = ttk.Label(self)

        # observer pattern
        self._controller.add_data_observer(self)
        self._controller.add_layout_observer(self)

    def _render(self) -> None:
        """
        Sets up and arranges all widgets within the frame, including labels, entries, and buttons.
        """
        self.config(padx=10, pady=10)

        # Static label for the filename
        label = ttk.Label(self, text="Filename:", font=("Helvetica", 16))
        label.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        # Placeholder for filename display
        self._filename_label.config(text=self._filename)
        self._filename_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Create additional labels and entries based on meta_tag_labels
        for index, text in enumerate(self._tag_types, start=1):
            label = ttk.Label(self, text=text)
            label.grid(row=index, column=0, sticky="w", padx=5, pady=2)

            # Create entry fields for each label
            entry = tk.Entry(self)
            entry.grid(row=index, column=1, sticky="ew", padx=5, pady=2)

        # Configure grid columns: left column (labels) to fit contents, right column (entries) to expand
        # Left column for labels, no expansion
        self.grid_columnconfigure(0, weight=0)
        # Right column for entries, expands to fill space
        self.grid_columnconfigure(1, weight=1)

    def get_meta_tag_labels(self) -> List[str]:
        """
        Retrieves the current meta tag labels.

        Returns:
            List[str]: A list of meta tag label names.
        """
        return self._tag_types

    def set_meta_tag_labels(self, labels: List[str]) -> None:
        """
        Sets the meta tag labels to a new list of labels and re-renders the frame.

        Args:
            labels (List[str]): A list of new meta tag label names to display.
        """
        self._tag_types = labels
        # Re-render components if labels are updated
        for widget in self.winfo_children():
            widget.destroy()
        self._render()

    def update_data(self) -> None:
        """
        Retrieves updated data from the controller and updates the view accordingly.

        This method fetches data associated with this observer from the controller
        and processes it to refresh the displayed information.
        """
        data = self._controller.get_data_state(self)
        # todo: Process and update the view with the retrieved data
        self._render()

    def update_layout(self) -> None:
        """
        Retrieves updated layout information from the controller and updates the view accordingly.

        This method fetches layout data associated with this observer from the controller
        and processes it to adjust the layout of the view.
        """
        layout = self._controller.get_layout_state(self)
        self._tag_types = layout["tag_types"]
        # todo: Process and update the layout with the retrieved information

        self._render()
