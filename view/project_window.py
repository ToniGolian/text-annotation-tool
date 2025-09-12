import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from enums.menu_pages import MenuPage, MenuSubpage
from view.edit_project_wizard_frame import EditProjectWizardFrame
from view.new_project_wizard_frame import NewProjectWizardFrame


class ProjectWindow(tk.Toplevel):
    """
    A window for managing project-related tasks, including creating new projects,
    editing existing ones, and configuring project-specific settings.

    This window contains three tabs:
    - New Project
    - Edit Project
    - Project Settings
    """

    def __init__(self, controller: IController, master: tk.Tk, *args, **kwargs) -> None:
        """
        Initializes the project window with tabbed interface.

        Args:
            master (tk.Tk): The main application window or root.
        """
        super().__init__(master, *args, **kwargs)
        self._controller = controller
        self.title("Project Manager")
        self.geometry("1000x600")
        self.resizable(True, True)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize tabs
        self._init_tabs()

    def _init_tabs(self) -> None:
        """Initializes the notebook tabs with empty frames."""
        self._new_project_frame = NewProjectWizardFrame(
            controller=self._controller, master=self._notebook)
        self._edit_project_frame = EditProjectWizardFrame(
            controller=self._controller, master=self._notebook)
        self._project_settings_frame = ttk.Frame(self._notebook)

        self._controller.add_observer(
            observer=self._new_project_frame)
        self._controller.add_observer(
            observer=self._edit_project_frame)

        self._notebook.add(self._new_project_frame, text="New Project")
        self._notebook.add(self._edit_project_frame, text="Edit Project")
        self._notebook.add(self._project_settings_frame,
                           text="Project Settings")

    def select_tab(self, tab: MenuPage, subtab: MenuSubpage) -> None:
        """
        Programmatically selects a tab by name.

        Args:
            tab (ProjectWizardTab): The tab to select. One of 'NEW_PROJECT', 'EDIT_PROJECT', or 'PROJECT_SETTINGS'.
            subtab (MenuSubpage): The subtab to select within the chosen tab.

        """
        notebook_page = {MenuPage.NEW_PROJECT: self._new_project_frame,
                         MenuPage.EDIT_PROJECT: self._edit_project_frame,
                         MenuPage.PROJECT_SETTINGS: self._project_settings_frame}.get(tab)
        if notebook_page is not None:
            self._notebook.select(notebook_page)
        else:
            raise ValueError(f"Unknown tab: {tab}")

        if subtab:
            notebook_page.select_subtab(subtab)

    def _on_save_project(self):
        raise NotImplementedError("Save project dialog not implemented yet.")

    def _on_save_project_as(self):
        raise NotImplementedError(
            "Save project as dialog not implemented yet.")

    def _on_export_project(self):
        raise NotImplementedError("Export project dialog not implemented yet.")
