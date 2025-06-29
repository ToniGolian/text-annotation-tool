from typing import List
from controller.interfaces import IController
import tkinter as tk
from tkinter import ttk

from view.annotation_menu_frame import AnnotationMenuFrame
# from view.comparison_io_frame import ComparisonIOFrame
# from view.comparison_controls_frame import ComparisonControlsFrame
from view.comparison_header_frame import ComparisonHeaderFrame
from view.comparison_text_displays import ComparisonTextDisplays
from view.interfaces import IComparisonView
from view.search_frame import SearchFrame
from view.view import View


class ComparisonView(View, IComparisonView):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the TextAnnotationView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent, controller)
        self._view_id = "comparison"
        self._controller.register_view(view_id=self._view_id, view=self)
        self._text_displays = None
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

        self._text_displays = ComparisonTextDisplays(
            self.left_frame, self._controller)
        self._text_displays.pack(side=tk.TOP, fill=tk.BOTH,
                                 expand=True, padx=10, pady=5)

        # Frame containing the export button
        self.export_frame = tk.Frame(self.left_frame)
        self.export_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Export button placed on the left side
        self.export_button = tk.Button(
            self.export_frame,
            text="Export Merged Document",
            # replace with your actual method
            command=self._controller.perform_export_merged_document
        )
        self.export_button.pack(side=tk.LEFT)

        # Now pack left_frame itself in the paned_window
        self.left_frame.pack(fill="both", expand=True)

        # Right frame for the tagging menu
        self.right_frame = AnnotationMenuFrame(
            self, controller=self._controller, root_view_id=self._view_id)

        # Add frames to the PanedWindow with weights
        self.paned_window.add(self.left_frame, weight=6)
        self.paned_window.add(self.right_frame, weight=1)

        # Set initial sash positions
        self.old_sash = self.paned_window.sashpos(0)

    def get_comparison_displays(self) -> List[tk.Widget]:
        """
        Returns a list of all text display widgets managed by this view.

        This method retrieves the text display widgets from `_text_displays` 
        and provides them as a flat list.

        Returns:
            List[tk.Widget]: A list of widgets representing the text displays.
        """
        return self._text_displays.get_displays()
