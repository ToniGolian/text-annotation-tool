import tkinter as tk
from controller.interfaces import IController
from view.text_display_frame import TextDisplayFrame


class ComparisonTextDisplayFrame(TextDisplayFrame):
    """
    A frame that displays text and integrates with an observer pattern.
    Includes a scrollbar for the text widget.
    """

    def __init__(self, index: int, parent: tk.Widget, controller: IController, editable=False, selectable: bool = False) -> None:
        """
        Initializes the TextDisplayFrame with a text widget, scrollbar, and observer registration.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller managing interactions.
            selectable (bool): Whether text selection events should trigger actions.
        """
        self._index = index
        self._selectable = selectable
        super().__init__(parent=parent, controller=controller, editable=editable)

    def _render(self) -> None:
        super()._render()
        # Bind selection event if selectable
        if self._selectable:
            self.text_widget.bind("<ButtonRelease-1>", self._on_selection)
