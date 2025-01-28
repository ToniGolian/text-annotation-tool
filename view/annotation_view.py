import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from view.annotation_text_display_frame import AnnotationTextDisplayFrame
from view.meta_tags_frame import MetaTagsFrame
from view.text_display_frame import TextDisplayFrame
from view.annotation_menu_frame import AnnotationMenuFrame
from view.view import View
# from mockclasses.mock_tagging_menu_frame import MockTaggingMenuFrame
# from mockclasses.mock_text_display_frame import MockTextDisplayFrame


class AnnotationView(View):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the TextAnnotationView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent, controller)
        self._view_id = "annotation"
        self._controller.register_view(self._view_id)
        self._render()

    def _render(self) -> None:
        """
        Sets up the layout for the TextAnnotationView, allowing resizing between 
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
        self.lower_frame = AnnotationTextDisplayFrame(
            self.left_frame, controller=self._controller)
        self.lower_frame.pack(fill=tk.BOTH, expand=True, side="top")

        # Now pack left_frame itself in the paned_window
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # Right frame for the tagging menu
        self.right_frame = AnnotationMenuFrame(
            self, controller=self._controller, root_view_id=self._view_id)

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
        # Placeholder for update logic based on model changes
        print("TextAnnotationView has been updated based on model changes.")
