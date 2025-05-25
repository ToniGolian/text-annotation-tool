import tkinter as tk
from controller.interfaces import IController
from view.interfaces import IView


class View(tk.Frame, IView):
    """
    Base class for views with shared functionality for managing focus,
    binding keyboard shortcuts, and handling undo/redo actions.
    """

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the View with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        # Generate a unique identifier for this view
        self._controller = controller
        self._view_id = None  # will be assigned by subclass
        self._bind_shortcuts()

        self.bind("<FocusIn>", self._on_focus)

        # Ensure this Frame can receive focus
        self.configure(takefocus=True)

    def _bind_shortcuts(self) -> None:
        """
        Globally binds the keyboard shortcuts for undo (Ctrl+Z) and redo (Ctrl+Y).
        These events are routed to the controller, which delegates them to the active view.

        This ensures that shortcuts are always captured, regardless of the widget focus.
        """
        self.bind_all("<Control-z>", self._global_undo_handler)
        self.bind_all("<Control-y>", self._global_redo_handler)

    def _global_undo_handler(self, event: tk.Event) -> None:
        """
        Handles the global undo action by delegating it to the controller.

        The controller determines the currently active view and performs the undo action
        for that view.

        Args:
            event (tk.Event): The keyboard event that triggered this action.
        """
        self._controller.undo_command(self._controller.get_active_view())

    def _global_redo_handler(self, event: tk.Event) -> None:
        """
        Handles the global redo action by delegating it to the controller.

        The controller determines the currently active view and performs the redo action
        for that view.

        Args:
            event (tk.Event): The keyboard event that triggered this action.
        """
        self._controller.redo_command(self._controller.get_active_view())

    def _on_focus(self, event: tk.Event) -> None:
        """
        Updates the controller with the active view when this view gains focus
        and ensures the keyboard focus is set to this view.

        Args:
            event (tk.Event): The event triggered when this view gains focus.
        """
        self.focus_set()  # Set keyboard focus to this widget
        print(f"DEBUG {self._view_id=}")
        self._controller.set_active_view(self._view_id)

    def get_view_id(self) -> str:
        """
        Returns the unique identifier (UUID) of this view.

        Returns:
            str: The unique view identifier.
        """
        return self._view_id
