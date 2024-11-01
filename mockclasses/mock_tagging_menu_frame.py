import tkinter as tk
from view.interfaces import ITaggingMenuFrame


class MockTaggingMenuFrame(tk.Frame, ITaggingMenuFrame):
    def __init__(self, parent: tk.Widget) -> None:
        """
        Initializes the TaggingMenuFrame with a reference to the parent widget.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
        """
        super().__init__(parent)
        self.render(parent)

    def render(self, parent: tk.Widget) -> None:
        """
        Renders the tagging menu frame layout with example widgets.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
        """
        # Create a label and a few example tagging buttons
        label = tk.Label(self, text="Tagging Menu")
        label.pack(pady=5)

        # Example buttons for tagging options
        add_tag_button = tk.Button(
            self, text="Add Tag", command=self._on_add_tag)
        add_tag_button.pack(fill="x", padx=10, pady=5)

        remove_tag_button = tk.Button(
            self, text="Remove Tag", command=self._on_remove_tag)
        remove_tag_button.pack(fill="x", padx=10, pady=5)

        edit_tag_button = tk.Button(
            self, text="Edit Tag", command=self._on_edit_tag)
        edit_tag_button.pack(fill="x", padx=10, pady=5)

    def update(self) -> None:
        """
        Updates the tagging menu in response to notifications from the observed object.
        """
        print("TaggingMenuFrame has been updated based on model changes.")

    def _on_add_tag(self) -> None:
        """Mock action for adding a tag."""
        print("Add Tag button clicked.")

    def _on_remove_tag(self) -> None:
        """Mock action for removing a tag."""
        print("Remove Tag button clicked.")

    def _on_edit_tag(self) -> None:
        """Mock action for editing a tag."""
        print("Edit Tag button clicked.")
