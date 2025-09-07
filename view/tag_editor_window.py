import tkinter as tk
from tkinter import ttk

from enums.menu_pages import MenuPage


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

        self._new_tag_frame = ttk.Frame(self._notebook)
        self._edit_tag_frame = ttk.Frame(self._notebook)

        self._notebook.add(self._new_tag_frame, text="New Tag")
        self._notebook.add(self._edit_tag_frame, text="Edit Tag")

        # Placeholder content for 'New Tag' tab
        ttk.Label(self._new_tag_frame, text="New Tag creation UI goes here.").pack(
            pady=20)

        # Placeholder content for 'Edit Tag' tab
        ttk.Label(self._edit_tag_frame,
                  text="Tag editing UI goes here.").pack(pady=20)

    def select_tab(self, tab: MenuPage) -> None:
        """
        Programmatically selects a tab by name.

        Args:
            tab (MenuPage): The tab to activate. One of 'NEW_TAB' or 'EDIT_TAB'.
        """
        notebook_page = {MenuPage.NEW_TAB: self._new_tag_frame,
                         MenuPage.EDIT_TAB: self._edit_tag_frame}.get(tab)
        if notebook_page is not None:
            self._notebook.select(notebook_page)
        else:
            raise ValueError(f"Unknown tab name: {tab}")
