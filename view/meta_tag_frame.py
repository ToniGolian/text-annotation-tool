import tkinter as tk
from tkinter import ttk
from utils.interfaces import IObserver
from controller.interfaces import IController


class MetaTagsFrame(tk.Frame, IObserver):
    def __init__(self, parent, controller: IController):
        super().__init__(parent)

        # Controller reference for interaction
        self.controller = controller

        # Filename label placeholder
        self._filename_label = None

        # Render the GUI components
        self.render()

    def render(self):
        """Sets up and arranges all widgets within the frame."""

        # Left frame for labels and entries
        left_frame = ttk.Frame(self)
        labels_text = ["Filename:", "Semantic Tags:", "Geo Tags:", "Time Tags"]

        # Create labels and entries dynamically
        for index, text in enumerate(labels_text):
            # Create and position label
            label = ttk.Label(left_frame, text=text)
            label.grid(row=index, column=0, sticky="w", padx=5, pady=2)

            # Styling for the filename label
            if index == 0:
                label.configure(font=("Helvetica", 16))
                self._filename_label = ttk.Label(left_frame, text="")
                self._filename_label.grid(
                    row=index, column=1, sticky="w", padx=5, pady=2)
            else:
                # Create entry fields for the other labels
                entry = tk.Entry(left_frame)
                entry.grid(row=index, column=1, sticky="ew", padx=5, pady=2)

        # Pack left_frame to expand and adjust with window resizing
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                        expand=True, padx=10, pady=10)
        # Entries expand horizontally with window
        left_frame.grid_columnconfigure(1, weight=1)

        # Right frame for buttons
        right_frame = ttk.Frame(self)
        save_button = ttk.Button(right_frame, text="Save", command=self.save)
        save_as_button = ttk.Button(
            right_frame, text="Save as...", command=self.save_as)

        # Pack buttons at the bottom of right_frame
        save_as_button.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        save_button.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Position right_frame in this main frame, allowing window resizing
        right_frame.pack(side=tk.RIGHT, fill=tk.Y,
                         padx=10, pady=10, anchor='s')

        # Set column weights for flexible resizing between left and right frames
        self.grid_columnconfigure(0, weight=3)  # Left side takes more space
        self.grid_columnconfigure(1, weight=1)  # Right side takes less space

    def save(self):
        # TODO Implement save functionality
        pass

    def save_as(self):
        # TODO Implement save as functionality
        pass

    def update(self, data):
        # TODO Implement observer update functionality if needed
        pass
