from enum import Enum
from typing import List
import tkinter as tk
from tkinter import ttk

from controller.interfaces import IController
from enums.menu_pages import MenuSubpage
from observer.interfaces import IObserver, IPublisher


class NewProjectWizardFrame(ttk.Frame, IObserver):
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

    def __init__(self, controller: IController,  master=None, project_data: dict = None) -> None:
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

        self._notebook.select(self._page_project_name)
        self._set_focus_on_default_widget()

    def _init_page_project_name(self) -> None:
        """Initializes the first wizard page for entering the project name."""
        self._page_project_name = ttk.Frame(self._notebook)
        self._notebook.add(self._page_project_name, text="Project Name")

        ttk.Label(self._page_project_name, text="Project Name:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w")
        self._entry_project_name = tk.Entry(self._page_project_name)
        self._entry_project_name.grid(
            row=0, column=1, padx=10, pady=10, sticky="ew")
        self._page_project_name.columnconfigure(1, weight=1)
        # Fill row=1 with weight so it takes up vertical space
        self._page_project_name.rowconfigure(1, weight=1)

        # Navigation buttons (Back hidden)
        # Place the button in the bottom row
        ttk.Button(self._page_project_name, text="Next", command=self._on_button_pressed_next_tab).grid(
            row=2, column=1, sticky="e", padx=10, pady=10
        )

    def _init_page_tag_selection(self) -> None:
        """Initializes the second wizard page for selecting tags and creating new ones."""
        self._page_tag_selection = ttk.Frame(self._notebook)
        self._notebook.add(self._page_tag_selection, text="Select Tags")

        # Content frame for both listboxes
        content_frame = ttk.Frame(self._page_tag_selection)
        content_frame.grid(row=0, column=0, columnspan=3,
                           sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Frame for available tags (left)
        tag_select_frame = ttk.Frame(content_frame)
        tag_select_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(tag_select_frame, text="Available Tags:").pack(anchor="w")
        self._listbox_available_tags = tk.Listbox(
            tag_select_frame, selectmode=tk.MULTIPLE)
        self._listbox_available_tags.pack(fill="both", expand=True)
        ttk.Button(tag_select_frame, text="Add Tags", command=self._on_button_pressed_add_selected_tags).pack(
            anchor="w", pady=5
        )

        # Frame for selected tags (right)
        selected_tag_frame = ttk.Frame(content_frame)
        selected_tag_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(selected_tag_frame, text="Selected Tags:").pack(anchor="w")
        self._listbox_selected_tags = tk.Listbox(selected_tag_frame)
        self._listbox_selected_tags.pack(fill="both", expand=True)
        ttk.Button(selected_tag_frame, text="Remove Tags", command=self._on_button_pressed_remove_selected_tags).pack(
            anchor="e", pady=5
        )

        # Navigation buttons
        ttk.Button(self._page_tag_selection, text="Back", command=self._on_button_pressed_previous_tab).grid(
            row=1, column=0, sticky="w", padx=10, pady=10
        )
        ttk.Button(self._page_tag_selection, text="Next", command=self._on_button_pressed_next_tab).grid(
            row=1, column=2, sticky="e", padx=10, pady=10
        )

        # Configure layout
        self._page_tag_selection.columnconfigure(0, weight=1)
        self._page_tag_selection.columnconfigure(1, weight=1)
        self._page_tag_selection.columnconfigure(2, weight=1)
        self._page_tag_selection.rowconfigure(0, weight=1)

    def _init_page_tag_groups(self) -> None:
        """Initializes the third wizard page for creating tag groups."""
        self._page_tag_groups = ttk.Frame(self._notebook)
        self._notebook.add(self._page_tag_groups, text="Tag Groups")

        # Frame for file name and group name entries
        entry_frame = ttk.Frame(self._page_tag_groups)
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
        content_frame = ttk.Frame(self._page_tag_groups)
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
        self._tree_created_groups = ttk.Treeview(
            group_display_frame, show="tree")
        self._tree_created_groups.pack(fill="both", expand=True)

        # Action buttons
        ttk.Button(self._page_tag_groups, text="Add Tag Group", command=self._on_button_pressed_add_tag_group).grid(
            row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Button(self._page_tag_groups, text="Delete Tag Group", command=self._on_button_pressed_delete_tag_group).grid(
            row=2, column=2, sticky="e", padx=10, pady=5)

        # Navigation buttons
        ttk.Button(self._page_tag_groups, text="Back", command=self._on_button_pressed_previous_tab).grid(
            row=3, column=0, sticky="w", padx=10, pady=10)
        ttk.Button(self._page_tag_groups, text="Finish", command=self._on_button_pressed_finish).grid(
            row=3, column=2, sticky="e", padx=10, pady=10)

        # Configure overall layout
        self._page_tag_groups.columnconfigure(0, weight=1)
        self._page_tag_groups.columnconfigure(1, weight=1)
        self._page_tag_groups.columnconfigure(2, weight=1)
        self._page_tag_groups.rowconfigure(1, weight=1)

    def update(self, publisher: IPublisher) -> None:
        """
        Populates the wizard fields with existing project data.

        Args:
            publisher (IPublisher): The publisher notifying about the update.
        """
        state = self._controller.get_observer_state(
            observer=self, publisher=publisher)
        # Project name
        self._entry_project_name.delete(0, tk.END)
        self._entry_project_name.insert(0, state.get("project_name", ""))

        # Tags
        self._populate_listbox(
            listbox=self._listbox_available_tags, items=state.get("locally_available_tags", []))
        self._populate_listbox(
            listbox=self._listbox_selected_tags, items=state.get("selected_tags", []))
        self._populate_listbox(
            listbox=self._listbox_tags_for_group, items=state.get("selected_tags", []))

        # Tag groups
        tag_groups = state.get("tag_groups", {})
        self._populate_tag_group_tree(tag_groups)
        # File name for tag groups
        self._entry_tag_group_file_name.delete(0, tk.END)
        self._entry_tag_group_file_name.insert(
            0, state.get("tag_group_file_name", ""))

    def _populate_listbox(self, listbox: tk.Listbox, items: List[str]) -> None:
        """Fills a listbox with the given items."""
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

    def _populate_tag_group_tree(self, groups: dict[str, list[str]]) -> None:
        """Fills the treeview with tag group categories as parents and tag names as children."""
        self._tree_created_groups.delete(
            *self._tree_created_groups.get_children())
        for group_name, tag_list in groups.items():
            parent_id = self._tree_created_groups.insert(
                "", "end", text=group_name)
            for tag in tag_list:
                self._tree_created_groups.insert(parent_id, "end", text=tag)

    def _collect_current_page_data(self) -> dict:
        """
        Collects data from the current page to update the model.
        Returns:
            dict: A dictionary containing the data from the current page. The keys depend on the current page:
                - Page 0 (Project Name): {'project_name': str}
                - Page 1 (Tag Selection): {'selected_tags': List[str]}
                - Page 2 (Tag Groups): {'tag_group_file_name': str, 'tag_groups': Dict[str, List[str]]}

        """
        current_tab = self._notebook.select()
        data = {}
        if current_tab == str(self._page_project_name):
            data["project_name"] = self._entry_project_name.get().strip()
        elif current_tab == str(self._page_tag_selection):
            selected_tags = [self._listbox_selected_tags.get(i)
                             for i in range(self._listbox_selected_tags.size())]
            data["selected_tags"] = selected_tags
        elif current_tab == str(self._page_tag_groups):
            data["tag_group_file_name"] = self._entry_tag_group_file_name.get().strip()
            # Collect tag groups from the treeview
            tag_groups = {}
            for parent_id in self._tree_created_groups.get_children():
                group_name = self._tree_created_groups.item(parent_id, "text")
                tags = [self._tree_created_groups.item(
                    child_id, "text") for child_id in self._tree_created_groups.get_children(parent_id)]
                tag_groups[group_name] = tags
            data["tag_groups"] = tag_groups
        return data

    def _on_button_pressed_add_tag_group(self) -> None:
        """
        Adds a new tag group based on the current entries and selected tags.
        """
        tag_group_file_name = self._entry_tag_group_file_name.get().strip()
        group_name = self._entry_tag_group_name.get().strip()
        if not group_name:
            tk.messagebox.showerror(
                "Error", "Tag group name cannot be empty.", parent=self)
            # self._notebook.select(-1)
            return

        selected_tags = [self._listbox_tags_for_group.get(i)
                         for i in self._listbox_tags_for_group.curselection()]
        if not selected_tags:
            tk.messagebox.showerror(
                "Error", "No tags selected for the group.", parent=self)
            # self._notebook.select(-1)
            return

        new_group = {"name": group_name, "tags": selected_tags}
        self._controller.perform_project_add_tag_group(tag_group_file_name,
                                                       new_group)

    def _on_button_pressed_delete_tag_group(self) -> None:
        """
        Deletes the currently selected tag group from the list.
        """
        selected_indices = self._tree_created_groups.curselection()
        if not selected_indices:
            tk.messagebox.showerror(
                "Error", "No tag group selected for deletion.", parent=self)
            self._notebook.select(-1)
            return

        for index in selected_indices[::-1]:
            group_name = self._tree_created_groups.get(index)
            self._controller.perform_project_remove_tag_group(
                group_name)

    def _on_button_pressed_add_selected_tags(self) -> None:
        """
        Adds selected tags from the available tags listbox to the selected tags listbox.
        """
        selected_indices = self._listbox_available_tags.curselection()
        if not selected_indices:
            return

        tags = []
        for index in selected_indices:
            tags.append(self._listbox_available_tags.get(index))
        self._controller.perform_project_add_tags(tags)

    def _on_button_pressed_remove_selected_tags(self) -> None:
        """
        Removes selected tags from the selected tags listbox back to the available tags listbox.
        """
        selected_indices = self._listbox_selected_tags.curselection()
        if not selected_indices:
            return
        self._controller.perform_project_remove_tags(
            selected_indices)

    def _on_button_pressed_finish(self) -> None:
        """
        Finalizes the project creation or editing process.
        This method should gather all data and notify the controller.
        """
        self._controller.perform_project_create_new_project()

    def _on_button_pressed_next_tab(self) -> None:
        """
        Switches to the next tab in the notebook.
        """
        current_page_data = self._collect_current_page_data()
        self._controller.perform_project_update_project_data(current_page_data)
        index = self._notebook.index(self._notebook.select())
        self._notebook.select(index + 1)

    def _on_button_pressed_previous_tab(self) -> None:
        """
        Switches to the previous tab in the notebook.
        """
        current_page_data = self._collect_current_page_data()
        self._controller.perform_project_update_project_data(current_page_data)
        index = self._notebook.index(self._notebook.select())
        self._notebook.select(index - 1)

    def select_subtab(self, subtab: MenuSubpage) -> None:
        """
        Selects a subtab within the current tab.

        Args:
            subtab (MenuSubpage): The subtab to select.
        """
        notebook_page = {
            MenuSubpage.PROJECT_NAME: self._page_project_name,
            MenuSubpage.PROJECT_TAGS: self._page_tag_selection,
            MenuSubpage.PROJECT_TAG_GROUPS: self._page_tag_groups
        }.get(subtab)
        if notebook_page is not None:
            self._notebook.select(notebook_page)
            self._set_focus_on_default_widget()
        else:
            raise ValueError(f"Unknown subtab: {subtab}")

    def _set_focus_on_default_widget(self) -> None:
        """
        Sets focus on the default widget of the current page.
        """
        current_tab = self._notebook.select()
        if current_tab == str(self._page_project_name):
            self._entry_project_name.focus_set()
        elif current_tab == str(self._page_tag_selection):
            self._listbox_available_tags.focus_set()
        elif current_tab == str(self._page_tag_groups):
            self._entry_tag_group_file_name.focus_set()

    def destroy(self) -> None:
        """
        Cleans up the observer before destroying the window.
        """
        self._controller.remove_observer(self)
        super().destroy()
