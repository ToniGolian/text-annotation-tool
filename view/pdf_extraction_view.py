import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from view.meta_tag_frame import MetaTagsFrame
from view.pdf_extraction_frame import PDFExtractionFrame
from view.text_display_frame import TextDisplayFrame
from view.tagging_menu_frame import TaggingMenuFrame


class PDFExtractionView(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the PDFExtractionView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller
        self._file_name = ""  # Initialize file name as an empty string

        self._render()

    def _render(self) -> None:
        """
        Sets up the layout for the PDFExtractionView, allowing resizing between 
        the text display frames on the left, a center frame, and the tagging menu frame on the right.
        """
        # Create the main horizontal PanedWindow for the layout
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left frame containing a label and a text display
        self.left_frame = tk.Frame(self.paned_window)

        # Create a sub-frame for the labels
        label_frame = tk.Frame(self.left_frame)
        label_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create the "Filename:" label
        filename_label = tk.Label(
            label_frame, text="Filename:", font=("Helvetica", 16), anchor="w"
        )
        filename_label.pack(side=tk.LEFT, padx=(5, 5))

        # Create the dynamic label for the filename
        self.file_name_display = tk.Label(
            label_frame, text=self._file_name, font=("Helvetica", 16), anchor="w"
        )
        self.file_name_display.pack(side=tk.LEFT)

        # Add the lower frame for the text display
        self.lower_frame = TextDisplayFrame(
            self.left_frame, controller=self._controller
        )
        self.lower_frame.pack(fill=tk.BOTH, expand=True, side="top")

        # Pack the left frame itself in the paned window
        self.left_frame.pack(fill=tk.BOTH, expand=True)

        # Right frame for the tagging menu
        self.right_frame = PDFExtractionFrame(
            self, controller=self._controller)

        # Add frames to the PanedWindow with weights
        self.paned_window.add(self.left_frame, weight=6)
        self.paned_window.add(self.right_frame, weight=1)

        # Set initial sash positions
        self.old_sash = self.paned_window.sashpos(0)

    def update(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could refresh the text display or tagging menu if necessary.
        """
        print("PDFExtractionView has been updated based on model changes.")

    def set_file_name(self, file_name: str) -> None:
        """
        Sets the file name and updates the display label text.

        Args:
            file_name (str): The name of the file to display.
        """
        self._file_name = file_name
        self.file_name_display.config(text=self._file_name)
