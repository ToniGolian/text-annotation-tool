import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from enums.menu_pages import MenuSubpage
from observer.interfaces import IObserver, IPublisher


class LoadProjectWindow(tk.Toplevel, IObserver):
    """
    A window for selecting and loading a project.

    This window observes the controller for available projects and allows the user
    to select one from a dropdown and trigger its loading.
    """

    def __init__(self, controller: IController, master: tk.Tk, *args, **kwargs) -> None:
        """
        Initializes the LoadProjectWindow.

        Args:
            controller (IController): The controller providing project data and actions.
            master (tk.Tk): The parent application window.
        """
        super().__init__(master, *args, **kwargs)
        self._controller = controller
        self._controller.add_observer(self)
        self.title("Load Project")
        self.geometry("600x200")
        self.resizable(False, False)

        # Combobox for selecting a project
        ttk.Label(self, text="Select Project:").pack(
            anchor="w", padx=10, pady=(10, 0))
        self._combo_projects = ttk.Combobox(self, state="readonly")
        self._combo_projects.pack(fill="x", padx=10, pady=5)

        # Button to trigger loading
        ttk.Button(self, text="Load Project", command=self._on_load_project).pack(
            anchor="e", padx=10, pady=10)

    def update(self, publisher: IPublisher) -> None:
        """
        Called by the controller to update this observer with new data.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        state = self._controller.get_observer_state(
            observer=self, publisher=publisher)
        projects = state.get("projects", [])
        project_names = [project["name"]
                         for project in projects if "name" in project]
        self._combo_projects["values"] = project_names
        if project_names:
            self._combo_projects.current(0)

    def _on_load_project(self) -> None:
        """
        Loads the selected project via the controller.
        """
        selected = self._combo_projects.get()
        if selected:
            self._controller.perform_project_load_project(
                project_name=selected, reload=True)
            self.destroy()

    def destroy(self) -> None:
        """
        Cleans up the observer before destroying the window.
        """
        self._controller.remove_observer(self)
        super().destroy()
