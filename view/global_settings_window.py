import tkinter as tk
from tkinter import ttk


class GlobalSettingsWindow(tk.Toplevel):
    """
    A window for managing global application settings.

    This window includes the following tabs:
    - Colors: for customizing UI colors.
    - Language: for selecting the application language.
    - Extraction: for setting parameters related to text extraction.
    - Suggestions: for configuring automatic suggestion behavior.
    """

    def __init__(self, master=None):
        """
        Initializes the GlobalSettingsWindow with four tabs inside a notebook.

        Args:
            master (tk.Widget): The parent widget, typically the main application window.
        """
        super().__init__(master)
        self.title("Global Settings")
        self.geometry("1000x600")
        self.resizable(True, True)

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        extraction_frame = ttk.Frame(self._notebook)
        suggestions_frame = ttk.Frame(self._notebook)
        colors_frame = ttk.Frame(self._notebook)
        language_frame = ttk.Frame(self._notebook)

        self._notebook.add(extraction_frame, text="Extraction")
        self._notebook.add(suggestions_frame, text="Suggestions")
        self._notebook.add(colors_frame, text="Colors")
        self._notebook.add(language_frame, text="Language")

        # Placeholder content for each tab
        ttk.Label(colors_frame, text="UI color settings go here.").pack(pady=20)
        ttk.Label(language_frame,
                  text="Language selection goes here.").pack(pady=20)
        ttk.Label(extraction_frame,
                  text="Extraction parameter settings go here.").pack(pady=20)
        ttk.Label(suggestions_frame,
                  text="Suggestion options go here.").pack(pady=20)
