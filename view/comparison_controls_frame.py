import tkinter as tk
from tkinter import ttk


class ComparisonControlsFrame(tk.Frame):
    """
    A tkinter Frame that contains widgets for filter controls, radio buttons, and action buttons.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the ComparisonControlsFrame with filter and action controls.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
        """
        super().__init__(parent, *args, **kwargs)
        self._render()

    def _render(self):
        """Sets up and arranges all widgets within the controls frame."""

        # Frame for filter controls
        filter_frame = tk.Frame(self)
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Filter label and combobox
        self.filter_label = tk.Label(filter_frame, text="Filter:")
        self.filter_label.pack(side=tk.LEFT, padx=5)

        self.filter_var = tk.StringVar()
        self.filter_combobox = ttk.Combobox(
            filter_frame, textvariable=self.filter_var)
        self.filter_combobox['values'] = ("No Filter", "Timex3", "Geo")
        self.filter_combobox.current(0)
        self.filter_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Start comparison button
        self.start_button = ttk.Button(
            filter_frame, text="Start Comparison", command=self.on_button_pressed_start_comparison)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Frame wrapper for action and navigation controls
        frame_wrapper = tk.Frame(self)
        frame_wrapper.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Frame for radio buttons and save button
        action_and_nav_frame = tk.Frame(frame_wrapper)
        action_and_nav_frame.pack(side=tk.LEFT, fill=tk.X, padx=5)

        # Frame for radio buttons
        action_frame = tk.Frame(action_and_nav_frame)
        action_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Radio button group for choosing annotations
        self.dir_label = tk.Label(
            action_frame, text="Choose preferred annotation:")
        self.dir_label.pack(side=tk.LEFT)
        self.radio_var = tk.IntVar()
        radio_button = tk.Radiobutton(
            action_frame, text="Manual Annotation", variable=self.radio_var, value=0)
        radio_button.pack(side=tk.LEFT, padx=5)
        for i in range(3):
            radio_button = tk.Radiobutton(
                action_frame, text=f"Annotator {i+1}", variable=self.radio_var, value=i+1)
            radio_button.pack(side=tk.LEFT, padx=5)

        # Overwrite button
        self.overwrite_button = ttk.Button(
            action_frame, text="Overwrite", command=self.on_button_pressed_overwrite)
        self.overwrite_button.pack(side=tk.LEFT, padx=5)

    def on_button_pressed_start_comparison(self):
        # Placeholder for start comparison logic
        pass

    def on_button_pressed_overwrite(self):
        # Placeholder for overwrite logic
        pass
