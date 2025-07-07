import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from view.global_settings import GlobalSettings
from view.project_settings import ProjectSettings


class SettingsWindow(tk.Toplevel):
    """
    A window for managing application settings, including global and project-specific preferences.

    This window contains two tabs:
    - Global Settings
    - Project Settings
    """

    def __init__(self, controller: IController, master: tk.Tk, *args, **kwargs) -> None:
        """
        Initializes the settings window with tabbed interface.

        Args:
            controller (IController): The main application controller.
            master (tk.Tk): The main application window or root.
        """
        super().__init__(master, *args, **kwargs)
        self._controller = controller
        self.title("Settings")
        self.geometry("1000x600")
        self.resizable(True, True)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._global_settings = GlobalSettings(
            controller=self._controller, master=self._notebook)
        self._project_settings = ProjectSettings(
            controller=self._controller, master=self._notebook)

        self._notebook.add(self._global_settings, text="Global Settings")
        self._notebook.add(self._project_settings, text="Project Settings")

    def select_tab(self, name: str) -> None:
        """
        Programmatically selects a tab by name.

        Args:
            name (str): Either "global" or "project".
        """
        name = name.lower()
        tab_index = {"global": 0, "project": 1}.get(name)
        if tab_index is not None:
            self._notebook.select(tab_index)
        else:
            raise ValueError(f"Unknown tab name: {name}")
