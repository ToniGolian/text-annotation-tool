import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from observer.interfaces import IObserver, IPublisher


class ProjectSettings(tk.Frame, IObserver):
    """
    A container for project-specific settings, displayed as a notebook with multiple tabs:
    - Search
    - Colors
    - Language
    """

    def __init__(self, controller: IController, master=None) -> None:
        """
        Initializes the ProjectSettings frame with a notebook for organizing settings.

        Args:
            master: The parent widget.
        """
        super().__init__(master)
        self._controller = controller
        self._controller.add_observer(self)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        self._init_search_tab()
        self._init_colors_tab()
        self._init_language_tab()

    def _init_search_tab(self) -> None:
        """Initializes the Search settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Search")
        # Add search-related settings here later

    def _init_colors_tab(self) -> None:
        """Initializes the Colors settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Colors")
        # Add color customization settings here later

    def _init_language_tab(self) -> None:
        """Initializes the Language settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Language")
        # Add language selection options here later

    def update(self, publisher: IPublisher) -> None:
        """
        Receives updates from the controller.

        Args:
            publisher (IPublisher): The publisher notifying this observer.
        """
        pass  # Implement update logic if needed
