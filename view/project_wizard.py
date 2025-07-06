from typing import List
import tkinter as tk
from tkinter import ttk

from controller.interfaces import IController
from observer.interfaces import IObserver


class ProjectWizard(ttk.Frame, IObserver):
    """
    A multi-step wizard widget used to create or edit a project.

    This widget is intended to be embedded in a parent container such as a notebook tab.
    It consists of three pages:
        1. Project name entry.
        2. Tag selection and creation.
        3. Tag group definition.

    Optionally, initial project data can be passed during construction or later via `set_project_data`.

    Attributes:
        _notebook (ttk.Notebook): The internal notebook managing the wizard pages.
        _entry_project_name (tk.Entry): Entry widget for the project name.
        _available_tags (list[str]): List of tags available for selection.
        _listbox_tag_selection (tk.Listbox): Listbox for selecting tags for the project.
        _entry_tag_group_file_name (tk.Entry): Entry for the tag group file name.
        _entry_tag_group_name (tk.Entry): Entry for the current tag group name.
        _listbox_tags_for_group (tk.Listbox): Listbox for selecting tags to include in a group.
        _listbox_created_groups (tk.Listbox): Listbox displaying created tag groups.
    """

    def __init__(self, controller: IController, master=None, project_data: dict = None) -> None:
        super().__init__(master)

        self._controller = controller
        self._controller.add_observer(self)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(expand=True, fill="both")

        self._init_page_project_name()
        self._init_page_tag_selection()
        self._init_page_tag_groups()

        if project_data:
            self.set_project_data(project_data)

    def _init_page_project_name(self) -> None:
        """Initializes the first wizard page for entering the project name."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Project Name")

        ttk.Label(frame, text="Project Name:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        self._entry_project_name = tk.Entry(frame)
        self._entry_project_name.grid(
            row=0, column=1, padx=10, pady=10, sticky="ew")
        frame.columnconfigure(1, weight=1)
        # Fill row=1 with weight so it takes up vertical space
        frame.rowconfigure(1, weight=1)

        # Navigation buttons (Back hidden)
        # Place the button in the bottom row
        ttk.Button(frame, text="Next", command=lambda: self._notebook.select(1)).grid(
            row=2, column=1, sticky="e", padx=10, pady=10
        )

    def _init_page_tag_selection(self) -> None:
        """Initializes the second wizard page for selecting tags and creating new ones."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Select Tags")

        ttk.Label(frame, text="Available Tags:").grid(
            row=0, column=0, sticky="w", padx=10, pady=5)

        self._listbox_tag_selection = tk.Listbox(frame, selectmode=tk.MULTIPLE)
        self._listbox_tag_selection.grid(
            row=1, column=0, padx=10, pady=5, sticky="nsew")

        ttk.Button(frame, text="Create Tag").grid(
            row=2, column=0, padx=10, pady=10, sticky="w")

        # Navigation buttons
        ttk.Button(frame, text="Back", command=lambda: self._notebook.select(0)).grid(
            row=3, column=0, sticky="w", padx=10, pady=10)
        ttk.Button(frame, text="Next", command=lambda: self._notebook.select(2)).grid(
            row=3, column=0, sticky="e", padx=10, pady=10)

        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

    def _init_page_tag_groups(self) -> None:
        """Initializes the third wizard page for creating tag groups."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Tag Groups")

        # Frame for file name and group name entries
        entry_frame = ttk.Frame(frame)
        entry_frame.grid(row=0, column=0, columnspan=3,
                         sticky="ew", padx=10, pady=5)
        entry_frame.columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="Tag Group File Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        self._entry_tag_group_file_name = tk.Entry(entry_frame)
        self._entry_tag_group_file_name.grid(
            row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(entry_frame, text="Tag Group Name:").grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        self._entry_tag_group_name = tk.Entry(entry_frame)
        self._entry_tag_group_name.grid(
            row=1, column=1, sticky="ew", padx=5, pady=2)

        # Frame for tag selection and tag group display
        content_frame = ttk.Frame(frame)
        content_frame.grid(row=1, column=0, columnspan=3,
                           sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Tag selection (left column)
        tag_select_frame = ttk.Frame(content_frame)
        tag_select_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(tag_select_frame, text="Select Tags for Group:").pack(
            anchor="w")
        self._listbox_tags_for_group = tk.Listbox(
            tag_select_frame, selectmode=tk.MULTIPLE)
        self._listbox_tags_for_group.pack(fill="both", expand=True)

        # Treeview for created groups (right column)
        group_display_frame = ttk.Frame(content_frame)
        group_display_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(group_display_frame,
                  text="Created Tag Groups:").pack(anchor="w")
        self._tree_created_groups = ttk.Treeview(group_display_frame)
        self._tree_created_groups.pack(fill="both", expand=True)

        # Action buttons
        ttk.Button(frame, text="Add Tag Group", command=self._add_tag_group).grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Button(frame, text="Delete Tag Group", command=self._delete_tag_group).grid(
            row=2, column=2, sticky="e", padx=10, pady=5)

        # Navigation buttons
        ttk.Button(frame, text="Back", command=lambda: self._notebook.select(1)).grid(
            row=3, column=0, sticky="w", padx=10, pady=10)
        ttk.Button(frame, text="Finish", command=self._finish).grid(
            row=3, column=2, sticky="e", padx=10, pady=10)

        # Configure overall layout
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(1, weight=1)

    def update(self) -> None:
        """
        Populates the wizard fields with existing project data.

        Args:
            data (dict): Dictionary containing keys like 'name', 'available_tags', 'tag_groups'.
        """
        state = self._controller.get_observer_state()
        # Project name
        self._entry_project_name.delete(0, tk.END)
        self._entry_project_name.insert(0, state.get("project_name", ""))

        # Tags
        self._populate_tag_listbox(state.get("available_tags", []))
        self._populate_group_tag_listbox(state.get("selected_tags", []))

        # Tag groups
        self._populate_tag_group_tree(state.get("tag_groups", []))
        # File name for tag groups
        self._entry_tag_group_file_name.delete(0, tk.END)
        self._entry_tag_group_file_name.insert(
            0, state.get("tag_group_file_name", ""))

    def _populate_tag_listbox(self, tags: List[str]) -> None:
        """Fills the listbox for selecting tags from available tag list."""
        self._listbox_tag_selection.delete(0, tk.END)
        for tag in tags:
            self._listbox_tag_selection.insert(tk.END, tag)

    def _populate_group_tag_listbox(self, tags: List[str]) -> None:
        """Fills the tag group creation listbox with available tags."""
        self._listbox_tags_for_group.delete(0, tk.END)
        for tag in tags:
            self._listbox_tags_for_group.insert(tk.END, tag)

    def _populate_tag_group_tree(self, groups: List[dict]) -> None:
        """Fills the treeview with existing tag groups."""
        self._tree_created_groups.delete(
            *self._tree_created_groups.get_children())
        for group in groups:
            name = group.get("name", "<unnamed>")
            self._tree_created_groups.insert("", tk.END, text=name)

    def _add_tag_group(self) -> None:
        """
        Adds a new tag group based on the current entries and selected tags.
        """
        group_name = self._entry_tag_group_name.get().strip()
        if not group_name:
            tk.messagebox.showerror("Error", "Tag group name cannot be empty.")
            return

        selected_tags = [self._listbox_tags_for_group.get(i)
                         for i in self._listbox_tags_for_group.curselection()]
        if not selected_tags:
            tk.messagebox.showerror("Error", "No tags selected for the group.")
            return

        new_group = {"name": group_name, "tags": selected_tags}
        self._populate_tag_group_list()
        self._controller.perform_project_add_tag_group(new_group)

    def _delete_tag_group(self) -> None:
        """
        Deletes the currently selected tag group from the list.
        """
        selected_indices = self._listbox_created_groups.curselection()
        if not selected_indices:
            tk.messagebox.showerror(
                "Error", "No tag group selected for deletion.")
            return

        for index in selected_indices[::-1]:
            group_name = self._listbox_created_groups.get(index)
            self._controller.perform_project_remove_tag_group(group_name)

    def _finish(self) -> None:
        """
        Finalizes the project creation or editing process.
        This method should gather all data and notify the controller.
        """
        project_name = self._entry_project_name.get().strip()
        if not project_name:
            tk.messagebox.showerror(
                "Error", "Project name cannot be empty.", parent=self)
            self._notebook.select(0)  # Switch back to "Project Name" tab
            return

        tag_groups = self._controller.get_project_wizard_model(
        ).get_state().get("tag_groups", {})
        tag_group_file_name = self._entry_tag_group_file_name.get().strip()

        # Notify controller to finalize the project
        self._controller.perform_project_finalize(
            project_name, tag_groups, tag_group_file_name)
