import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.interfaces import IMetaTagsFrame


class MetaTagsFrame(tk.Frame, IMetaTagsFrame):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the MetaTagsFrame with a controller and a scrollable area.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller for handling interactions.
        """
        super().__init__(parent)

        self._controller = controller
        self._tag_types = []
        self._meta_tag_entries = {}

        # Configure grid layout to allow vertical expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create scrollable container
        self._canvas = tk.Canvas(self,  height=90)
        self._scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        # Frame inside the canvas
        self._scroll_frame = tk.Frame(self._canvas)
        self._scroll_window = self._canvas.create_window(
            (0, 0), window=self._scroll_frame, anchor="nw")

        # Ensure the scroll frame expands fully inside the canvas
        self._scroll_frame.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all"))
        )

        # Proper layout for the canvas and scrollbar
        self._canvas.grid(row=1, column=0, sticky="nsew")
        self._scrollbar.grid(row=1, column=1, sticky="ns")

        # Ensure the scrollable frame expands correctly
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(
            self._scroll_window, width=e.width))

        # Register observer
        self._controller.add_observer(self)

    def _render(self) -> None:
        """
        Sets up and arranges all widgets within the scrollable frame, including labels and entries.
        """
        # Clear previous frame contents
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()

        # Frame above scrollable area for file_name
        file_name_frame = tk.Frame(self)
        file_name_frame.grid(row=0, column=0, columnspan=2,
                             sticky="ew")
        file_name_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(file_name_frame, text="Filename:", font=("Helvetica", 16)).grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        self._file_name_label = ttk.Label(
            file_name_frame, text="", font=("Helvetica", 16))
        self._file_name_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Configure the layout of the scrollable frame
        self._scroll_frame.grid_columnconfigure(0, weight=0)
        self._scroll_frame.grid_columnconfigure(
            1, weight=1)

        # Create label-entry pairs inside the scrollable frame
        self._meta_tag_entries.clear()
        for index, tag_type in enumerate(self._tag_types):
            ttk.Label(self._scroll_frame, text=tag_type).grid(
                row=index, column=0, sticky="w", padx=5, pady=2
            )

            entry = tk.Entry(self._scroll_frame)
            self._meta_tag_entries[tag_type] = entry
            entry.grid(row=index, column=1, sticky="ew", padx=5, pady=2)

        # Ensure scrolling is correct
        self._scroll_frame.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all"))
        )

        # Frame below scrollable area for buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2,
                          sticky="ew", pady=(5, 0))
        button_frame.grid_columnconfigure(1, weight=1)

        # "Update Meta Tags" button
        update_button = ttk.Button(
            button_frame, text="Update Meta Tags", command=self._button_pressed_update_meta_tags)
        update_button.grid(row=0, column=1, sticky="e", padx=(0, 30))

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
        self._render()

    def update(self, publisher: IPublisher) -> None:
        """
        Retrieves updated layout information from the controller and updates the view accordingly.

        This method fetches layout data associated with this observer from the controller
        and processes it to adjust the layout of the view.
        """
        state = self._controller.get_observer_state(self, publisher)
        # Update tag types and re-render if needed
        if tag_types := state.get("tag_types"):
            self._tag_types = tag_types
            self._render()

        # Update file_name label
        if file_name := state.get("file_name"):
            self._file_name_label.config(text=file_name)

        # Update meta tag entries
        for tag_type, tags in state.get("meta_tags", {}).items():
            if tag_type in self._meta_tag_entries:
                self._meta_tag_entries[tag_type].delete(0, tk.END)
                self._meta_tag_entries[tag_type].insert(
                    0, ", ".join(str(tag) for tag in tags))

    def finalize_view(self) -> None:
        """
        Retrieves the layout state and updates the file_names before rendering the view.
        """
        layout = self._controller.get_observer_state(self)
        self._tag_types = layout.get("tag_types", [])
        self._render()

    def _button_pressed_update_meta_tags(self) -> None:
        """
        Updates the meta tags by retrieving the current values from the input widgets 
        and passing them to the controller for further processing.
        """
        meta_tags = {k: v.get() for k, v in self._meta_tag_entries.items()}
        self._controller.perform_update_meta_tags(meta_tags)
