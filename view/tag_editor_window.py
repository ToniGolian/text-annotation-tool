import tkinter as tk
from tkinter import ttk


class TagEditorWindow(tk.Toplevel):
    """
    A window for managing tag definitions.

    This window includes two tabs:
    - 'New Tag': for defining a new tag type.
    - 'Edit Tag': for modifying existing tag types.
    """

    def __init__(self, master=None):
        """
        Initializes the TagEditorWindow with two tabs inside a notebook.

        Args:
            master (tk.Widget): The parent widget, typically the main application window.
        """
        super().__init__(master)
        self.title("Tag Editor")
        self.geometry("1000x600")
        self.resizable(True, True)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        new_tag_frame = ttk.Frame(self._notebook)
        edit_tag_frame = ttk.Frame(self._notebook)

        self._notebook.add(new_tag_frame, text="New Tag")
        self._notebook.add(edit_tag_frame, text="Edit Tag")

        # Placeholder content for 'New Tag' tab
        ttk.Label(new_tag_frame, text="New Tag creation UI goes here.").pack(
            pady=20)

        # Placeholder content for 'Edit Tag' tab
        ttk.Label(edit_tag_frame, text="Tag editing UI goes here.").pack(pady=20)

    def select_tab(self, name: str) -> None:
        """
        Programmatically selects a tab by name.

        Args:
            name (str): One of "new", "edit", or "settings".
        """
        name = name.lower()
        tab_index = {"new": 0, "edit": 1}.get(name)
        if tab_index is not None:
            self._notebook.select(tab_index)
        else:
            raise ValueError(f"Unknown tab name: {name}")
