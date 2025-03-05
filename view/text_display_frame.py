import tkinter as tk
from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.interfaces import ITextDisplayFrame
import uuid


class TextDisplayFrame(tk.Frame, ITextDisplayFrame):
    """
    A frame that displays text and integrates with an observer pattern.
    Includes a scrollbar for the text widget.
    """

    DEBOUNCE_DELAY = 300  # milliseconds

    def __init__(self, parent: tk.Widget, controller: IController, editable: bool = False, is_static_observer: bool = False, height: int = None) -> None:
        """
        Initializes the TextDisplayFrame with a text widget, scrollbar, and optional observer registration.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller managing interactions.
            editable (bool, optional): Whether the text can be edited. Defaults to False.
            register_as_observer (bool, optional): Whether this instance should register itself as an observer. Defaults to False.
        """

        super().__init__(parent)

        self._controller: IController = controller
        self.text_widget: tk.Text = None
        self._editable: bool = editable

        self._debounce_job = None  # To track the scheduled job
        self._is_typing = False  # Indicates if the user is typing
        self._internal_update = False  # Tracks if the update is internal
        self._cursor_position: str = None  # Stores cursor position for internal updates
        self._is_static_observer: bool = is_static_observer
        self._height = height

        # Render the GUI components
        self._render()

        # Register as an observer
        if is_static_observer:
            self._controller.add_observer(self)

    def _render(self) -> None:
        """
        Sets up and arranges the text widget and scrollbar within the frame.
        If a height is specified, ensures the widget does not expand beyond this height.
        """
        # Create a scrollbar
        scrollbar = tk.Scrollbar(self, orient="vertical")

        # Initialize the text widget and configure the scrollbar
        self.text_widget = tk.Text(
            self, wrap="word", yscrollcommand=scrollbar.set, state="disabled"
        )
        scrollbar.config(command=self.text_widget.yview)

        if self._editable:
            self.text_widget.config(state="normal")
            self.text_widget.bind("<KeyRelease>", self._on_text_change)

        self.text_widget.bind("<ButtonRelease-1>", self._on_selection)

        # Ensure the widget respects the given height, if specified
        if self._height is not None:
            self.text_widget.config(height=self._height)
        # Pack the text widget and scrollbar
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=(10, 0), pady=(5, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_selection(self, event: tk.Event) -> None:
        """
        Handles text selection events and passes the selected text along with its absolute starting position
        in the entire text to the controller.

        Args:
            event (tk.Event): The event triggered by text selection.
        """
        try:
            # Get the selected text
            selected_text = self.text_widget.selection_get()

            # Get the start index of the selection (e.g., "line.column")
            start_index = self.text_widget.index(tk.SEL_FIRST)
            line, col = map(int, start_index.split("."))

            # Calculate the absolute start position in the entire text
            lines_before = sum(len(self.text_widget.get(
                f"{i}.0", f"{i}.end")) + 1 for i in range(1, line))
            start_position = lines_before + col

            # Prepare the selection data
            selection_data = {
                "position": start_position,
                "selected_text": selected_text
            }
            # Pass the data to the controller
            self._controller.perform_text_selected(selection_data)
        except tk.TclError:
            # No selection exists, so we simply ignore the event
            pass

    def _on_text_change(self, event: tk.Event) -> None:
        """
        Handles text change events to implement debouncing and optimistic updates.

        Args:
            event (tk.Event): The event triggered by text input.
        """
        if self._debounce_job:
            self.after_cancel(self._debounce_job)

        self._is_typing = True  # User is typing

        # Optimistically update the model
        new_text = self.text_widget.get("1.0", tk.END).strip()
        self._controller.perform_update_preview_text(new_text)

        # Track the cursor position
        self._cursor_position = self.text_widget.index(tk.INSERT)

        # Set up debouncing to finalize the changes
        self._debounce_job = self.after(
            self.DEBOUNCE_DELAY, self._finalize_update)

    def _finalize_update(self) -> None:
        """
        Finalizes updates to the model after debouncing.
        """
        self._is_typing = False
        new_text = self.text_widget.get("1.0", tk.END).strip()
        self._controller.perform_update_preview_text(
            new_text)  # Final update to ensure sync
        self._debounce_job = None  # Reset the job reference

    def update(self, publisher: IPublisher) -> None:
        """
        Observer method to handle updates from subjects, refreshing the displayed text.

        This method updates the text in the text widget based on the latest state 
        from the controller. If the user is currently typing, the update is skipped 
        to prevent unwanted overwrites.

        Behavior:
            - The text widget is cleared and updated with new content.
            - If a cursor position was stored, it is restored after the update.
            - If the widget is not editable, it is temporarily set to normal mode 
            to allow updates before being disabled again.
            - The internal update flag is used to distinguish between automatic 
            and manual updates.

        Updates:
            - Fetches the latest text from the controller.
            - Restores cursor position if available.
            - Ensures that typing interactions are not interrupted.
        """
        if self._is_typing:
            # Skip updates while the user is typing to prevent overwrites
            return

        self._internal_update = True  # Mark this as an internal update

        # Fetch the latest text from the model
        text = self._controller.get_observer_state(
            self, publisher).get("text", "NOTEXT")

        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)
        self.text_widget.update_idletasks()
        self.text_widget.update()

        actual_text = self.text_widget.get("1.0", tk.END).strip()

        # Restore cursor position if available
        if self._cursor_position:
            self.text_widget.mark_set(tk.INSERT, self._cursor_position)

        if not self._editable:
            self.text_widget.config(state="disabled")

        self._cursor_position = None  # Reset the cursor position
        self._internal_update = False  # Reset the internal update flag

    def is_static_observer(self) -> bool:
        """
        Checks whether this observer is static.

        A static observer is permanently registered and does not change dynamically
        during runtime.

        Returns:
            bool: True if the observer is static, False otherwise.
        """
        return self._is_static_observer
