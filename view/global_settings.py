import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController
from observer.interfaces import IObserver, IPublisher


class GlobalSettings(tk.Frame, IObserver):
    """
    A container for global settings, displayed as a notebook with multiple tabs:
    - Extraction
    - Comparison
    - Suggestions
    """

    def __init__(self, controller: IController, master=None) -> None:
        """
        Initializes the GlobalSettings frame with a notebook for organizing settings.

        Args:
            master: The parent widget.
        """
        super().__init__(master)
        self._controller = controller
        self._controller.add_observer(self)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True)

        self._init_extraction_tab()
        self._init_comparison_tab()
        self._init_suggestions_tab()
        self._init_default_path_tab()

    def _init_extraction_tab(self) -> None:
        """Initializes the Extraction settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Extraction")
        # You can populate this frame with extraction-related settings later

    def _init_comparison_tab(self) -> None:
        """Initializes the Comparison settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Comparison")
        # You can populate this frame with comparison-related settings later

    def _init_suggestions_tab(self) -> None:
        """Initializes the Suggestions settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Suggestions")
        # You can populate this frame with suggestion-related settings later

    def _init_default_path_tab(self) -> None:
        """Initializes the Default Path settings tab."""
        frame = ttk.Frame(self._notebook)
        self._notebook.add(frame, text="Default Path")
        # You can populate this frame with default path-related settings later

    def update(self, publisher: IPublisher) -> None:
        """
        Receives updates from the controller.

        Args:
            publisher (IPublisher): The publisher notifying this observer.
        """
        pass  # Update logic can be implemented later if needed
