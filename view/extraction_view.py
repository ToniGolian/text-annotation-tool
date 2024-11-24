import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from view.meta_tags_frame import MetaTagsFrame
from view.extraction_frame import ExtractionFrame
from view.text_display_frame import TextDisplayFrame
from view.annotation_menu_frame import AnnotationMenuFrame


class ExtractionView(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the PDFExtractionView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller
        self._filename = ""  # Initialize file name as an empty string

        self._render()

    def _render(self) -> None:
        """
        Sets up the layout for the PDFExtractionView, allowing resizing between 
        the text display frames on the left, a center frame, and the tagging menu frame on the right.
        """
        # Create the main horizontal PanedWindow for the layout
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Center frame containing upper and lower frames for text and metadata display
        self.left_frame = tk.Frame(self.paned_window)

        # Pack the upper_frame at the top of left_frame
        self.upper_frame = MetaTagsFrame(
            self.left_frame, controller=self._controller)
        self.upper_frame.pack(fill=tk.X, expand=False, side="top")

        # Pack the lower_frame below the upper_frame
        self.lower_frame = TextDisplayFrame(
            self.left_frame, controller=self._controller)
        self.lower_frame.pack(fill=tk.BOTH, expand=True, side="top")

        # Now pack left_frame itself in the paned_window
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # Right frame for the tagging menu
        self.right_frame = ExtractionFrame(
            self, controller=self._controller)

        # Add frames to the PanedWindow with weights
        self.paned_window.add(self.left_frame, weight=6)
        self.paned_window.add(self.right_frame, weight=1)

        # Set initial sash positions
        self.old_sash = self.paned_window.sashpos(0)

    def update_layout(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could refresh the text display or tagging menu if necessary.
        """
        print("ExtractionView has been updated based on model changes.")
