from tkinter import ttk
from typing import List
from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.annotation_text_display_frame import AnnotationTextDisplayFrame
from view.interfaces import IComparisonTextDisplays
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

        self._num_comparison_displays: int = 0

        self._comparison_display_height = 8  # todo settings

        self._file_names: List[str] = []
        self._widget_structure: List[tk.Widget] = []

        # Add observer
        self._controller.add_observer(self)

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
        Clears all existing widgets and updates the layout with the new ones.
        Ensures that each text display maintains its predefined height.
        """
        # Destroy existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self._reconfigure_widgets()

        # Configure layout for each label and text display frame
        for index, (label, text_display_frame) in enumerate(self._widget_structure):
            row = index * 2
            label.grid(row=row, column=0, sticky="w", pady=(2, 0))

            # Ensure the text display does not expand beyond its height
            text_display_frame.grid(
                row=row + 1, column=0, sticky="ew", pady=(0, 0))
            text_display_frame.grid_propagate(False)

        # Prevent the entire frame from expanding vertically
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Ensure each row is properly configured
        for i in range(len(self._widget_structure) * 2):
            self.scrollable_frame.grid_rowconfigure(
                i, weight=0)  # Ensure no unexpected expansion

    def _reconfigure_widgets(self) -> None:
        """
        Reconfigures the widgets based on the current state of num_comparison_displays.
        Creates a new Label and TextDisplayFrame pair for each document and updates self._widget_structure.
        """
        self._widget_structure = []

        for _ in range(self._num_comparison_displays):
            # Create a TextDisplayFrame with a fixed height
            text_display_frame = AnnotationTextDisplayFrame(
                parent=self.scrollable_frame, controller=self._controller, height=self._comparison_display_height
            )

            # Ensure the frame does not expand vertically
            text_display_frame.grid_propagate(False)

            self._widget_structure.append(
                (tk.Label(self.scrollable_frame), text_display_frame))

    def update(self, publisher: IPublisher) -> None:
        """
        Retrieves updated data and layout information from the controller 
        and updates the view accordingly.

        This method fetches both data and layout state associated with this observer
        from the controller and processes it to refresh the displayed information.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        state = self._controller.get_observer_state(self, publisher)

        # Update view attributes dynamically based on the retrieved state
        if "num_comparison_displays" in state:
            self._num_comparison_displays = state["num_comparison_displays"]
            # Render the updated state
            self._render()
        if "file_names" in state:
            self._file_names = state["file_names"]
            for index, (file_name, (label, _)) in enumerate(zip(self._file_names, self._widget_structure)):
                if index == 0:
                    label.config(text="Original Text:")
                else:
                    label.config(text=f"Filename: {file_name}")

    def finalize_view(self) -> None:
        """
        Retrieves the layout state and updates the file_names before rendering the view.
        """
        layout = self._controller.get_observer_state(self)
        self._file_names = layout["file_names"]
        self._render()

    def get_displays(self) -> List[tk.Widget]:
        """
        Returns a list of all widgets representing the text display frames.

        Returns:
            List[tk.Widget]: A list of widgets that are part of the display structure.
        """
        return [widget for _, widget in self._widget_structure]
