from typing import List
import tkinter as tk
from tkinter import ttk

from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.project_wizard_frame import ProjectWizardFrame


class EditProjectWizardFrame(ProjectWizardFrame):
    """
    A specialized version of the ProjectWizard used for editing existing projects.
    Adds an initial page for selecting a project from a list and adapts labels to reflect editing.
    """

    def __init__(self, controller: IController, master=None) -> None:

        super().__init__(controller=controller, master=master)
        self._available_projects = []
        self._selected_project = None

        # Add selection page at the beginning
        self._init_page_project_selection()
        self._notebook.insert(
            0, self._page_project_selection, text="Choose Project")
        self._notebook.select(0)

        # Update tab labels
        self._notebook.tab(1, text="Edit Project Name")
        self._notebook.tab(2, text="Edit Tags")
        self._notebook.tab(3, text="Edit Tag Groups")

        # Update last button label from "Finish" to "Edit Project"
        self._replace_finish_button()

    def _init_page_project_selection(self) -> None:
        """Initializes the first page for selecting an existing project."""
        self._page_project_selection = ttk.Frame(self._notebook)

        ttk.Label(self._page_project_selection, text="Select project to edit:").pack(
            anchor="w", padx=10, pady=10
        )

        self._listbox_projects = tk.Listbox(
            self._page_project_selection, exportselection=False)
        self._listbox_projects.pack(fill="both", expand=True, padx=10, pady=5)

        for project in self._available_projects:
            self._listbox_projects.insert(tk.END, project)

        ttk.Button(
            self._page_project_selection,
            text="Choose Project",
            command=self._choose_project
        ).pack(anchor="e", padx=10, pady=10)

    def _choose_project(self) -> None:
        """Handles selection of a project and loads its data into the wizard."""
        selected = self._listbox_projects.curselection()
        if not selected:
            tk.messagebox.showerror(
                "Error", "Please select a project.", parent=self)
            return

        self._selected_project = self._listbox_projects.get(selected[0])
        self._controller.perform_load_project_data_for_editing(
            self._selected_project)

        # Move to next tab
        self._notebook.select(1)

    def _replace_finish_button(self) -> None:
        """Replaces the 'Finish' button on the last page with 'Edit Project'."""
        last_page = self._notebook.nametowidget(self._notebook.tabs()[-1])
        for child in last_page.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text") == "Finish":
                child.config(text="Edit Project")

    def _populate_projects_listbox(self, projects: List[str]) -> None:
        """Populates the projects listbox with the given project names.
        Args:
            projects (List[str]): List of project names to display.
        """
        self._listbox_projects.delete(0, tk.END)
        for project in projects:
            self._listbox_projects.insert(tk.END, project)
        if projects:
            self._listbox_projects.selection_set(0)

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the wizard state based on the current project data.
        This method is called when the controller notifies observers of changes.
        """
        super().update(publisher)
        state = self._controller.get_observer_state(
            observer=self, publisher=publisher)
        projects = state.get("projects", [])
        project_names = [project["name"] for project in projects]
        self._populate_projects_listbox(project_names)
