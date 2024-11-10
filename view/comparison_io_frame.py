import tkinter as tk
from tkinter import ttk


class ComparisonIOFrame(tk.Frame):
    """
    A tkinter Frame that contains widgets for directory selection and directory display.
    """

    def __init__(self, parent, default_directory="", *args, **kwargs):
        """
        Initializes the ComparisonIOFrame with directory selection and entry widgets.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            default_directory (str): The default directory path to display in the entry.
        """
        super().__init__(parent, *args, **kwargs)
        self.default_directory = default_directory
        self._render()

    def _render(self):
        """Sets up and arranges all widgets within the IO frame."""

        # Frame for directory controls
        dir_frame = tk.Frame(self)
        dir_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Directory label and entry
        self.dir_label = tk.Label(dir_frame, text="Directory:")
        self.dir_label.pack(side=tk.LEFT, padx=5)

        self.dir_entry = tk.Entry(dir_frame)
        self.dir_entry.insert(0, self.default_directory)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Directory selection button
        self.dir_button = ttk.Button(
            dir_frame, text="Select Directory", command=self.on_button_pressed_select_directory)
        self.dir_button.pack(side=tk.LEFT, padx=5)

    def on_button_pressed_select_directory(self):
        # Placeholder for directory selection logic
        pass
