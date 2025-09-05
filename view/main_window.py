import platform
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import Optional
from observer.interfaces import IObserver, IPublisher
from typing import Dict
from view.extraction_view import ExtractionView
from view.annotation_view import AnnotationView
from view.comparison_view import ComparisonView
from controller.interfaces import IController
from view.load_project_window import LoadProjectWindow
from view.project_window import ProjectWindow
from view.settings_window import SettingsWindow
from view.tag_editor_window import TagEditorWindow


class MainWindow(tk.Tk, IObserver):
    def __init__(self, controller: IController) -> None:
        super().__init__()

        self.DEFAULT_NOTEBOOK_INDEX = 0
        self._controller = controller
        self._controller.register_view("main_window", self)

        self._annotation_view = None
        self._extraction_view = None
        self._comparison_view = None

        self._project_window: Optional[ProjectWindow] = None
        self._tag_editor_window: Optional[TagEditorWindow] = None

        if platform.system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        self.title("Text Annotation Tool")

        self._create_menu()
        self._render_views()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._controller.add_observer(self)

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self)
        # self._notebook = ttk.Notebook(self)

        # Create File, Project, Settings, and Help menus
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open File", command=self._on_open)
        file_menu.add_command(label="Save File", command=self._on_save)
        file_menu.add_command(label="Save as...", command=self._on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Project menu
        project_menu = tk.Menu(menu_bar, tearoff=0)
        project_menu.add_command(
            label="New Project", command=self._on_new_project)
        project_menu.add_command(label="Open Project",
                                 command=self._on_open_project)

        project_menu.add_separator()
        project_menu.add_command(label="Edit Project",
                                 command=self._on_edit_project)
        project_menu.add_command(label="Project Settings",
                                 command=self._on_project_settings)
        menu_bar.add_cascade(label="Project", menu=project_menu)

        # Tags menu
        tags_menu = tk.Menu(menu_bar, tearoff=0)
        tags_menu.add_command(label="New Tag type",
                              command=self._on_new_tag_type)
        tags_menu.add_command(label="Edit Tag type",
                              command=self._on_edit_tag_type)
        menu_bar.add_cascade(label="Tags", menu=tags_menu)

        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(
            label="Global Settings", command=self._on_settings)
        settings_menu.add_command(label="Project Settings",
                                  command=self._on_project_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label="About", command=self._on_about)
        help_menu.add_separator()
        help_menu.add_command(label="Help", command=self._on_help)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

    def _render_views(self) -> None:
        """
        Renders the main views within the notebook.
        """
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        self._extraction_view = ExtractionView(
            parent=self._notebook, controller=self._controller)
        self._notebook.add(self._extraction_view, text="PDF Extraction")

        self._annotation_view = AnnotationView(
            parent=self._notebook, controller=self._controller)
        self._notebook.add(self._annotation_view, text="Text Annotation")

        self._comparison_view = ComparisonView(
            parent=self._notebook, controller=self._controller)
        self._notebook.add(self._comparison_view, text="Text Comparison")

        self._notebook.select(self.DEFAULT_NOTEBOOK_INDEX)
        self._controller.set_active_view(
            ["extraction", "annotation", "comparison"][self.DEFAULT_NOTEBOOK_INDEX])

    def _destroy_views(self) -> None:
        """
        Destroys the current views and the notebook.
        """
        if hasattr(self, "_notebook") and self._notebook.winfo_exists():
            self._notebook.destroy()
        self._extraction_view = None
        self._annotation_view = None
        self._comparison_view = None

    def reload_views_for_new_project(self) -> None:
        """
        Destroys and re-renders the views, typically called when a new project is loaded
        to ensure views are in sync with the new project data.
        """
        self._controller.cleanup_observers_for_reload()
        self._destroy_views()
        self._render_views()

    # Menu actions
    # File actions
    def _on_open(self):
        self._controller.perform_open_file()

    def _on_save(self) -> None:
        self._controller.perform_save()

    def _on_save_as(self) -> None:
        self._controller.perform_save_as()

    # Project actions
    def _on_new_project(self):
        """ Opens the project creation window. """
        self._open_project_window(tab="new")

    def _on_edit_project(self):
        """ Opens the project edit window. """
        self._open_project_window(tab="edit")

    def _on_open_project(self):
        """
        Opens the project loading dialog to select an existing project.
        """
        self._open_load_project_dialog()

    # Tags actions
    def _on_new_tag_type(self):
        self._open_tag_editor("new")

    def _on_edit_tag_type(self):
        self._open_tag_editor("edit")

    # Settings actions
    def _on_settings(self):
        """ Opens the global settings window. """
        self._open_settings_window(tab="global")

    def _on_project_settings(self):
        """ Opens the project settings window. """
        self._open_settings_window(tab="project")

    # Help actions
    def _on_help(self):
        raise NotImplementedError("Help dialog not implemented yet.")

    def _on_about(self):
        raise NotImplementedError("About dialog not implemented yet.")

    # Window close action
    def _on_closing(self):
        self._controller.check_for_saving(enforce_check=True)
        self.destroy()

    # Observer pattern methods
    def update(self, publisher: IPublisher) -> None:
        state = self._controller.get_observer_state(self, publisher)
        if "active_notebook_index" in state:
            self._notebook.select(state["active_notebook_index"])
            if state["active_notebook_index"] == 1:
                self._annotation_view.focus_set()
        if "project_name" in state:
            project_name = state["project_name"]
            self.title(
                f"Text Annotation Tool ({project_name})" if project_name else "Text Annotation Tool")

    # Helpers
    def _open_project_window(self, tab: str = "new") -> None:
        """
        Opens the project window and focuses the requested tab.

        Args:
            tab (str): The tab to activate upon opening. One of 'new', 'edit', 'settings'.
        """
        # Create the project window if it doesn't exist or was closed
        if not self._project_window or not self._project_window.winfo_exists():
            self._project_window = ProjectWindow(
                controller=self._controller, master=self)
        self._controller.perform_project_update_projects()

        # Show and focus the window
        self._project_window.deiconify()
        self._project_window.lift()

        # Switch to the specified tab
        self._project_window.select_tab(tab)

    def _open_load_project_dialog(self) -> None:
        """
        Opens a dialog to select and load an existing project.
        """
        if not hasattr(self, "_load_project_window") or not self._load_project_window.winfo_exists():
            self._load_project_window = LoadProjectWindow(
                controller=self._controller, master=self)
        self._controller.perform_project_update_projects()

        # Show and focus the window
        self._load_project_window.deiconify()
        self._load_project_window.lift()

    def _open_tag_editor(self, tab: str = "new") -> None:
        """
        Opens the tag editor window in the specified mode.

        Args:
            tab (str): The tab to open in the tag editor. One of 'new' or 'edit'.
        """
        if not self._tag_editor_window or not self._tag_editor_window.winfo_exists():
            self._tag_editor_window = TagEditorWindow(self)

        self._tag_editor_window.deiconify()
        self._tag_editor_window.lift()
        self._tag_editor_window.select_tab(tab)

    def _open_settings_window(self, tab: str = "global") -> None:
        """
        Opens the settings window and focuses the requested tab.

        Args:
            tab (str): The tab to activate upon opening. One of 'global', 'project'.
        """
        # Create the settings window if it doesn't exist or was closed
        if not hasattr(self, "_settings_window") or not self._settings_window.winfo_exists():
            self._settings_window = SettingsWindow(
                controller=self._controller, master=self)

        # Show and focus the window
        self._settings_window.deiconify()
        self._settings_window.lift()

        # Switch to the specified tab
        self._settings_window.select_tab(tab)

    # popup dialogs
    def ask_user_for_save_path(self, initial_dir: str = None) -> Optional[str]:
        """
        Opens a file dialog to let the user choose a file path for saving.

        Args:
            initial_dir (str): The initial directory to open the dialog in.
            If None, the dialog will open in the current working directory.

        Returns:
            Optional[str]: The selected file path as a string, or None if the dialog was cancelled.
        """
        return filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".json",
            filetypes=[("Project files", "*.json"), ("All files", "*.*")],
            initialdir=initial_dir if initial_dir else ".",
        )

    def ask_user_for_file_paths(self, load_config: Dict = None) -> list[str]:
        """
        Opens a file dialog to let the user select one or multiple JSON files.

        Args:
            load_config (Dict): Configuration dictionary that specifies the mode and dialog options.

        Returns:
            list[str]: A list of selected file paths. If no files are selected, returns an empty list.

        Raises:
            ValueError: If the load_config does not specify a valid mode.
        """
        if load_config.get("mode") == "single":
            # Allow selection of a single JSON file
            path = filedialog.askopenfilename(**load_config.get("config"))
            return [path] if path else []
        elif load_config.get("mode") == "multiple":
            # Allow selection of multiple JSON files
            paths = filedialog.askopenfilenames(**load_config.get("config"))
            return list(paths)  # always returns a list
        else:
            raise ValueError("Invalid load configuration.")

    def ask_user_for_overwrite_confirmation(self, path: str) -> bool:
        """
        Opens a confirmation dialog asking the user whether to overwrite an existing file.

        Args:
            path (str): The file path that would be overwritten.

        Returns:
            bool: True if the user confirms overwriting, False otherwise.
        """
        return messagebox.askyesno(
            title="Overwrite File?",
            message=f"The file '{path}' already exists.\nDo you want to overwrite it?"
        )

    def prompt_save(self, view_id: str) -> bool:
        """
        Prompts the user with a dialog asking whether to save changes for a specific view.

        Args:
            view_id (str): The identifier of the view with unsaved changes.

        Returns:
            bool: True if the user chooses to save, False otherwise.
        """
        from tkinter import messagebox

        view_name = view_id.capitalize().replace("_", " ")
        message = f"The document in view '{view_name}' has unsaved changes.\nDo you want to save it?"
        return messagebox.askyesno("Unsaved Changes", message)

    def finalize_view(self) -> None:
        """ 
        Finalizes the main window view, updating the title based on the current project name.
        """
        state = self._controller.get_observer_state(self)
        if "project_name" in state:
            project_name = state["project_name"]
            self.title(
                f"Text Annotation Tool ({project_name})" if project_name else "Text Annotation Tool")
