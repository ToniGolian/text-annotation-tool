import tkinter as tk
from utils.interfaces import IObserver
from controller.interfaces import IController


class TextDisplayFrame(tk.Frame, IObserver):
    def __init__(self, parent: tk.Widget, controller: IController, selectable: bool = False):
        super().__init__(parent)

        self._controller = controller
        self._id = id
        self._selectable = selectable

        self.text_widget = None

        # Render the GUI components
        self._render()

        # Register as Observer
        self._controller.register_observer(self)

    def _render(self):
        """Sets up and arranges all widgets within the frame."""

        # Scrollbar initialization
        scrollbar = tk.Scrollbar(self)

        # Text widget initialization with scrollbar
        self.text_widget = tk.Text(
            self, yscrollcommand=scrollbar.set, state='disabled'
        )
        scrollbar.config(command=self.text_widget.yview)

        # Bind selection event to on_selection method depending on if the instance is markable
        if self._selectable:
            self.text_widget.bind("<ButtonRelease-1>", self._on_selection)

        # Pack text widget with padding on the left and bottom
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pack lower_frame in the main frame
        self.pack(fill=tk.BOTH, expand=True)

    def _on_selection(self, event):
        """Handles text selection events."""
        self._controller.perform_text_selected(
            self.text_widget.selection_get())

    def update(self, data):
        """Observer method to handle updates from subjects."""
        pass
