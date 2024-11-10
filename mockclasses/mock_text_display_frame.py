import tkinter as tk
from view.interfaces import ITextDisplayFrame


class MockTextDisplayFrame(tk.Frame, ITextDisplayFrame):
    def __init__(self, parent: tk.Widget) -> None:
        """
        Initializes the MockTextDisplayFrame with a reference to the parent widget.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
        """
        super().__init__(parent)
        self._render()

    def _render(self) -> None:
        """
        Renders the text display frame layout with example content.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
        """
        # Create a Text widget to simulate a text display area
        self.text_area = tk.Text(self, wrap="word", width=50, height=15)
        self.text_area.insert(
            "1.0", "This is a mock text display area.\n\nHere you can display and annotate text.")
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)

    def update(self) -> None:
        """
        Updates the text display frame in response to notifications from the observed object.
        """
        # Example action for update; could refresh or modify the text content
        print("MockTextDisplayFrame has been updated based on model changes.")
