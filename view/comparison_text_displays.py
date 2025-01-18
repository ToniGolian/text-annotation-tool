from tkinter import ttk
from typing import List
from controller.interfaces import IController
from view.interfaces import IComparisonTextDisplays
from view.comparison_text_display_frame import ComparisonTextDisplayFrame
import tkinter as tk


class ComparisonTextDisplays(tk.Frame, IComparisonTextDisplays):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the ComparisonTextDisplays with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller: IController = controller

        self._filenames: List[str] = []
        self._widget_structure: List[tk.Widget] = []

        # Add observer
        self._controller.add_observer(self, "data")
        self._controller.add_observer(self, "layout")

        # Create the canvas and scrollbar
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=canvas.yview)

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas that will be scrollable
        self.scrollable_frame = tk.Frame(canvas)

        # Update the scrollable frame width to match the canvas width
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Force the canvas width to match the container_frame's width
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                "scrollable_window", width=canvas.winfo_width())
        )

        # Add the scrollable frame to the canvas
        canvas.create_window((0, 0), window=self.scrollable_frame,
                             anchor="nw", tags="scrollable_window")

        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _render(self) -> None:
        """
        Clears all existing widgets, reconfigures the layout with the scrollable frame,
        and updates the layout with the new widgets.
        """
        # Remove all existing widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Reconfigure the widgets
        self._reconfigure_widgets()

        # Add subsequent labels and text displays
        for index, (label, text_display_frame) in enumerate(self._widget_structure):
            row = (index) * 2  # Alternate rows for label and text display
            label.grid(row=row, column=0, sticky="w", pady=(2, 0))
            text_display_frame.grid(
                row=row + 1, column=0, sticky="nsew", pady=(0, 0)
            )

        # Expand horizontally
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def _reconfigure_widgets(self) -> None:
        """
        Reconfigures the widgets based on the current state of self._file_names.
        Creates a new Label and TextDisplayFrame pair for each document and updates self._widget_structure.
        """
        self._widget_structure = []
        index = 0

        original_label = tk.Label(
            self.scrollable_frame, text="Original Text:"
        )
        original_text_display = ComparisonTextDisplayFrame(
            index=index, parent=self.scrollable_frame, controller=self._controller, selectable=True)
        index += 1
        self._widget_structure.append((original_label, original_text_display))

        for filename in self._filenames:
            # Create a label with the document's filename
            label = tk.Label(self.scrollable_frame,
                             text=f"Filename: {filename}")

            # Create a TextDisplayFrame for displaying the document's content
            text_display_frame = ComparisonTextDisplayFrame(
                index=index, parent=self.scrollable_frame, controller=self._controller, selectable=True)
            index += 1
            # Add the label and text display frame as a pair in the widget structure
            self._widget_structure.append((label, text_display_frame))

    def update_data(self) -> None:
        """
        Retrieves updated data from the controller and updates the view accordingly.

        This method fetches data associated with this observer from the controller
        and processes it to refresh the displayed information.
        """
        self._controller = self._controller.get_observer_state(self, "data")
        self._render()

    def update_layout(self) -> None:
        """
        Retrieves updated layout information from the controller and updates the view accordingly.

        This method fetches layout data associated with this observer from the controller
        and processes it to adjust the layout of the view.
        """
        layout = self._controller.get_observer_state(self, "layout")
        self._filenames = layout["filenames"]
        self._render()
