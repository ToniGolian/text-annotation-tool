import platform
import tkinter as tk
from tkinter import ttk
from view.pdf_extraction_view import PDFExtractionView
from view.text_annotation_view import TextAnnotationView
from view.comparison_view import ComparisonView
from controller.interfaces import IController


class MainWindow(tk.Tk):
    def __init__(self, controller: IController) -> None:
        """
        Initializes the MainFrame window, sets its size, and immediately renders 
        the notebook with three tabs for PDF extraction, text annotation, and text comparison.

        Args:
            controller (IController): The controller managing actions for the main application.
        """
        super().__init__()

        # Set window size
        if platform.system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        self.title("Text Annotation Tool")

        # Store controller reference
        self.controller = controller

        # Render the menu bar
        self._create_menu()

        # Render the notebook structure
        self._render()

        # Set the protocol for handling window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu(self) -> None:
        """
        Creates a menu bar with dropdown menus for "File" and "Settings".
        """
        menu_bar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self._on_open)
        file_menu.add_command(label="Save", command=self._on_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(
            label="Preferences", command=self._on_preferences)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Attach the menu bar to the main window
        self.config(menu=menu_bar)

    def _render(self) -> None:
        """
        Sets up the MainFrame layout by creating a notebook and adding 
        the PDF extraction, text annotation, and text comparison views as separate tabs.
        """
        # Create a notebook widget within the main window
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # Add the PDF Extraction tab
        pdf_view = PDFExtractionView(
            parent=notebook, controller=self.controller)
        notebook.add(pdf_view, text="PDF Extraction")

        # Add the Text Annotation tab
        text_annotation_view = TextAnnotationView(
            parent=notebook, controller=self.controller)  # Instantiate text annotation view
        notebook.add(text_annotation_view, text="Text Annotation")

        # Add the Text Comparison tab
        comparison_view = ComparisonView(
            parent=notebook, controller=self.controller)  # Instantiate text comparison view
        notebook.add(comparison_view, text="Text Comparison")

        # Choose the second page as default
        #! change
        notebook.select(2)

    def _on_open(self):
        """Handles the 'Open' action from the File menu."""
        print("Open file dialog not implemented yet.")

    def _on_save(self):
        """Handles the 'Save' action from the File menu."""
        print("Save file dialog not implemented yet.")

    def _on_preferences(self):
        """Handles the 'Preferences' action from the Settings menu."""
        print("Preferences dialog not implemented yet.")

    def _on_closing(self):
        """
        Handles the window close event.
        """
        # TODO ask for save changes
        # if self.controller and self.controller.document_is_modified():
        #     if self.ask_for_end_program_without_save():
        #         self.controller.perform_save_document()
        self.destroy()
