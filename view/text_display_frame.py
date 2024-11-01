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

    def render(self):
        """Sets up and arranges all widgets within the frame."""

        # Frame for text widget and scrollbar
        lower_frame = ttk.Frame(self)

        # Scrollbar initialization
        scrollbar = tk.Scrollbar(lower_frame)

        # Text widget initialization with scrollbar
        self.text_widget = tk.Text(
            lower_frame, yscrollcommand=scrollbar.set, state='disabled')
        scrollbar.config(command=self.text_widget.yview)

        # Bind selection event to on_selection method
        self.text_widget.bind("<ButtonRelease-1>", self.on_selection)

        # Pack text widget and scrollbar within lower_frame
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack lower_frame in the main frame
        lower_frame.pack(fill=tk.BOTH, expand=True)

    def on_selection(self, event):
        """Handles text selection events."""
        pass

    def update(self, data):
        """Observer method to handle updates from subjects."""
        pass
