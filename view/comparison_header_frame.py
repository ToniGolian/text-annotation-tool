import tkinter as tk
from tkinter import ttk
from utils.interfaces import IObserver


class ComparisonHeaderFrame(tk.Frame, IObserver):
    """
    A tkinter Frame that combines IO and Control widgets in a single grid layout.
    Includes directory selection, filter controls, action buttons, and annotation options.
    """

    def __init__(self, parent, controller):
        """
        Initializes the CombinedComparisonFrame with directory selection, controls, and annotation options.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller managing interactions.
            default_directory (str): The default directory path to display in the entry.
            num_annotators (int): Number of annotators for radio buttons.
        """
        super().__init__(parent)
        self._controller = controller
        # todo system independent path's
        self._default_directory: str = "resources/comparison"
        self._num_annotators: int = 0
        self._render()

    def _render(self):
        """Sets up and arranges all widgets in a single grid layout."""

        # Directory Label, Entry, and Button (Row 0 and 1)
        self.dir_label = tk.Label(self, text="Directory:")
        self.dir_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.dir_entry = tk.Entry(self)
        self.dir_entry.insert(0, self.default_directory)
        self.dir_entry.grid(row=0, column=1, columnspan=3,
                            sticky="ew", padx=5, pady=5)

        self.dir_button = ttk.Button(
            self, text="Select Directory", command=self.on_button_pressed_select_directory)
        self.dir_button.grid(row=0, column=4, sticky="ew", padx=5, pady=5)

        # Filter Label, Combobox, and Start Button (Row 2)
        self.filter_label = tk.Label(self, text="Filter:")
        self.filter_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self, textvariable=self.filter_var)
        self.filter_combobox['values'] = ("No Filter", "Timex3", "Geo")
        self.filter_combobox.current(0)
        self.filter_combobox.grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        self.start_button = ttk.Button(
            self, text="Start Comparison", command=self.on_button_pressed_start_comparison)
        self.start_button.grid(row=1, column=4, sticky="ew", padx=5, pady=5)

        # Radio Buttons and Overwrite Button (Row 3 and below)
        self.radio_label = tk.Label(self, text="Choose preferred annotation:")
        self.radio_label.grid(row=2, column=0, columnspan=5,
                              sticky="w", padx=5, pady=5)

        self.radio_var = tk.IntVar()
        # Manual Annotation Radio Button
        manual_radio = tk.Radiobutton(
            self, text="Manual Annotation", variable=self.radio_var, value=0)
        manual_radio.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        # Annotator Radio Buttons
        for i in range(self._num_annotators):
            radio_button = tk.Radiobutton(
                self, text=f"Annotator {i + 1}", variable=self.radio_var, value=i + 1)
            radio_button.grid(row=3, column=i + 1, sticky="w", padx=5, pady=5)

        # Overwrite Button
        self.overwrite_button = ttk.Button(
            self, text="Overwrite", command=self.on_button_pressed_overwrite)
        self.overwrite_button.grid(
            row=3, column=self._num_annotators + 1, sticky="ew", padx=5, pady=5)

        # Configure column resizing
        for col in range(5):
            self.grid_columnconfigure(col, weight=1)

    def update(self):
        """
        Implements the update method from the IObserver interface.
        Placeholder for responding to updates from the observed object.
        """
        self._num_annotators = self._controller.get_update_data(self)["data"]
        self._render()

    def on_button_pressed_select_directory(self):
        """Placeholder for directory selection logic."""
        pass

    def on_button_pressed_start_comparison(self):
        """Placeholder for start comparison logic."""
        pass

    def on_button_pressed_overwrite(self):
        """Placeholder for overwrite logic."""
        pass
