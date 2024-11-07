import tkinter as tk
from tkinter import ttk
from utils.interfaces import IObserver
from controller.interfaces import IController


class TextDisplayFrame(ttk.Frame, IObserver):
    def __init__(self, parent, controller: IController):
        super().__init__(parent)

        # Controller reference for interaction
        self.controller = controller

        # Initialize widget placeholders
        self.text_widget = None

        # Render the GUI components
        self.render()

        # Register as Observer
        self.controller.register_observer(self)

    def render(self):
        """Sets up and arranges all widgets within the frame."""

        # Scrollbar initialization
        scrollbar = tk.Scrollbar(self)

        # Text widget initialization with scrollbar
        self.text_widget = tk.Text(
            self, yscrollcommand=scrollbar.set, state='disabled'
        )
        scrollbar.config(command=self.text_widget.yview)

        # Bind selection event to on_selection method
        self.text_widget.bind("<ButtonRelease-1>", self.on_selection)

        # Pack text widget with padding on the left and bottom
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack lower_frame in the main frame
        self.pack(fill=tk.BOTH, expand=True)

    def on_selection(self, event):
        """Handles text selection events."""
        pass

    def update(self, data):
        """Observer method to handle updates from subjects."""
        pass
