import platform
import tkinter as tk
from tkinter import ttk
from view.extraction_view import ExtractionView
from view.annotation_view import AnnotationView
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
        self._controller = controller
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
        file_menu.add_command(label="Save as", command=self._on_save_as)
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
        pdf_view = ExtractionView(
            parent=notebook, controller=self.controller)
        notebook.add(pdf_view, text="PDF Extraction")

        # Add the Text Annotation tab
        text_annotation_view = AnnotationView(
            parent=notebook, controller=self.controller)  # Instantiate text annotation view
        notebook.add(text_annotation_view, text="Text Annotation")

        # Add the Text Comparison tab
        comparison_view = ComparisonView(
            parent=notebook, controller=self.controller)  # Instantiate text comparison view
        notebook.add(comparison_view, text="Text Comparison")

        # Choose the second page as default
        #!DEBUG change to 0
        notebook.select(1)
        self._controller.set_active_view("annotation")
        #!END DEBUG

    def _on_open(self):
        """
        Opens a file selection dialog and triggers the controller to handle the selected file.

        This method uses configuration from the controller to determine:
        - The initial directory for the dialog.
        - The allowed file types.
        - The title of the dialog.

        After a file is selected, it calls `perform_open_file` on the controller with the file path.

        Raises:
            Exception: Logs any exception that occurs during the file selection process.
        """
        config = self._controller.get_open_file_config()
        initial_dir = config.get("initial_dir", ".")
        filetypes = config.get("filetypes", [("All Files", "*.*")])
        title = config.get("title", "Open File")
        multi_select = config.get("multiselect", False)

        try:
            # Handle single or multi-select
            if multi_select:
                file_paths = tk.filedialog.askopenfilenames(
                    initialdir=initial_dir,
                    filetypes=filetypes,
                    title=title)
            else:
                file_paths = [tk.filedialog.askopenfilename(
                    initialdir=initial_dir,
                    filetypes=filetypes,
                    title=title
                )]

            # Filter out empty paths (if no selection was made)
            file_paths = [path for path in file_paths if path]
        except Exception as e:
            print(f"Error during open file dialog: {e}")
        if file_paths:
            self._controller.perform_open_file(file_paths)

    def _on_save_as(self):
        """
        Opens a save-as dialog and triggers the controller to handle the save operation.

        This method uses configuration from the controller to determine:
        - The initial directory for the dialog.
        - The allowed file types.
        - The default file extension.
        - The title of the dialog.

        After a file is selected, it calls `perform_save_as` on the controller with the file path.

        Raises:
            Exception: Logs any exception that occurs during the save-as process.
        """
        try:
            config = self._controller.get_save_as_config()
            initial_dir = config.get("initial_dir", ".")
            filetypes = config.get("filetypes", [("All Files", "*.*")])
            defaultextension = config.get("defaultextension", "")
            title = config.get("title", "Save File As")

            file_path = tk.filedialog.asksaveasfilename(
                initialdir=initial_dir,
                filetypes=filetypes,
                defaultextension=defaultextension,
                title=title
            )

        except Exception as e:
            print(f"Error during save as file dialog: {e}")
        if file_path:
            self._controller.perform_save_as(file_path)

    def _on_save(self):
        """Handles the 'Save' action from the File menu."""
        file_path = self._controller.get_file_path()
        print(f"DEBUG {file_path=}")
        if file_path:
            self._controller.perform_save_as(file_path)
        else:
            self._on_save_as()

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
