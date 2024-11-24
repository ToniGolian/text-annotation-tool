from controller.interfaces import IController
import tkinter as tk
from tkinter import ttk

from view.annotation_menu_frame import AnnotationMenuFrame
# from view.comparison_io_frame import ComparisonIOFrame
# from view.comparison_controls_frame import ComparisonControlsFrame
from view.comparison_header_frame import ComparisonHeaderFrame
from view.comparison_text_displays import ComparisonTextDisplays


class ComparisonView(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the TextAnnotationView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller

        self._render()

    def _render(self):
        """
        Sets up the layout for the ComparisonView, allowing resizing between 
        the text display frames on the left, a center frame, and the tagging menu frame on the right.
        """
        # Create the main horizontal PanedWindow for the layout
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Center frame containing upper and lower frames for text and metadata display
        self.left_frame = tk.Frame(self.paned_window)

        header_frame = ComparisonHeaderFrame(
            self.left_frame, controller=self._controller)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        text_displays = ComparisonTextDisplays(
            self.left_frame, self._controller)
        text_displays.pack(side=tk.TOP, fill=tk.BOTH,
                           expand=True, padx=10, pady=5)

        # Now pack left_frame itself in the paned_window
        self.left_frame.pack(fill="both", expand=True)

        # Right frame for the tagging menu
        self.right_frame = AnnotationMenuFrame(
            self, controller=self._controller)

        # Add frames to the PanedWindow with weights
        self.paned_window.add(self.left_frame, weight=6)
        self.paned_window.add(self.right_frame, weight=1)

        # Set initial sash positions
        self.old_sash = self.paned_window.sashpos(0)
