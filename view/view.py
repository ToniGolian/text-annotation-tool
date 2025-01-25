import tkinter as tk
import uuid

from controller.interfaces import IController


class View(tk.Frame):
    """
    Base class for views with shared functionality for binding shortcuts
    and handling undo/redo actions.
    """

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the View with a reference to the parent widget, controller, 
        and a unique view identifier (UUID).

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._view_id = str(uuid.uuid4())
        self._controller = controller
        self._controller.register_view(self._view_id)
        self._bind_shortcuts()

    def _bind_shortcuts(self) -> None:
        """
        Binds the keyboard shortcuts for undo (Ctrl+Z) and redo (Ctrl+Y).
        """
        self.bind_all("<Control-z>", self._handle_undo)
        self.bind_all("<Control-y>", self._handle_redo)

    def _handle_undo(self, event: tk.Event) -> None:
        """
        Handles the undo action triggered by the Ctrl+Z shortcut.

        Args:
            event (tk.Event): The keyboard event that triggered this action.
        """
        print("Undo action triggered")
        self._controller.undo_command(self._view_id)

    def _handle_redo(self, event: tk.Event) -> None:
        """
        Handles the redo action triggered by the Ctrl+Y shortcut.

        Args:
            event (tk.Event): The keyboard event that triggered this action.
        """
        print("Redo action triggered")
        self._controller.redo_command(self._view_id)
        # Placeholder for actual redo logic; override as needed

    def get_view_id(self) -> str:
        """
        Returns the unique identifier (UUID) of this view.

        Returns:
            str: The unique view identifier.
        """
        return self._view_id
