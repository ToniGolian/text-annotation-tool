import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from enums.project_wizard_types import ProjectWizardType
from view.edit_project_wizard_frame import EditProjectWizardFrame
from view.project_wizard_frame import ProjectWizardFrame


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
        self._new_project_frame = ProjectWizardFrame(
            controller=self._controller, project_wizard_type=ProjectWizardType.NEW, master=self._notebook)
        self._edit_project_frame = EditProjectWizardFrame(
            controller=self._controller, project_wizard_type=ProjectWizardType.EDIT, master=self._notebook)
        self._project_settings_frame = ttk.Frame(self._notebook)

        self._controller.add_observer(
            observer=self._new_project_frame)
        self._controller.add_observer(
            observer=self._edit_project_frame)

        self._notebook.add(self._new_project_frame, text="New Project")
        self._notebook.add(self._edit_project_frame, text="Edit Project")
        self._notebook.add(self._project_settings_frame,
                           text="Project Settings")

    def select_tab(self, name: str) -> None:
        """
        Programmatically selects a tab by name.

        Args:
            name (str): One of "new", "edit", or "settings".
        """
        name = name.lower()
        tab_index = {"new": 0, "edit": 1, "settings": 2}.get(name)
        if tab_index is not None:
            self._notebook.select(tab_index)
        else:
            raise ValueError(f"Unknown tab name: {name}")

    def _on_save_project(self):
        raise NotImplementedError("Save project dialog not implemented yet.")

    def _on_save_project_as(self):
        raise NotImplementedError(
            "Save project as dialog not implemented yet.")

    def _on_export_project(self):
        raise NotImplementedError("Export project dialog not implemented yet.")
