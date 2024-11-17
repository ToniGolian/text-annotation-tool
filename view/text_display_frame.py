import tkinter as tk
from controller.interfaces import IController
from view.interfaces import ITextDisplayFrame


class TextDisplayFrame(tk.Frame, ITextDisplayFrame):
    """
    A frame that displays text and integrates with an observer pattern.
    Includes a scrollbar for the text widget.
    """

    def __init__(self, parent: tk.Widget, controller: IController, editable=False) -> None:
        """
        Initializes the TextDisplayFrame with a text widget, scrollbar, and observer registration.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller managing interactions.
            selectable (bool): Whether text selection events should trigger actions.
        """
        super().__init__(parent)

        self._controller: IController = controller
        self.text_widget: tk.Text = None
        self._editable: bool = editable

        # Render the GUI components
        self._render()

        # Register as an observer
        self._controller.add_data_observer(self)

    def _render(self) -> None:
        """
        Sets up and arranges the text widget and scrollbar within the frame.
        """
        # Create a scrollbar
        scrollbar = tk.Scrollbar(self, orient="vertical")

        # Initialize the text widget and configure the scrollbar
        self.text_widget = tk.Text(
            self, wrap="word", yscrollcommand=scrollbar.set, state="disabled")
        scrollbar.config(command=self.text_widget.yview)
        if self._editable:
            self.text_widget.config(state="normal")

        self.text_widget.bind("<ButtonRelease-1>", self._on_selection)

        # Pack the text widget and scrollbar to fill the frame
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=(10, 0), pady=(10, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_selection(self, event: tk.Event) -> None:
        """
        Handles text selection events.

        Args:
            event (tk.Event): The event triggered by text selection.
        """
        selected_text = self.text_widget.selection_get()
        self._controller.perform_text_selected(selected_text)

    def update_data(self) -> None:
        """
        Observer method to handle updates from subjects.

        Args:
            data (dict): Data passed from the observed subject.
        """
        # Implement any necessary updates based on the data
        text = self._controller.get_update_data(self)
        if self._editable:
            self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)
        if self._editable:
            self.text_widget.config(state="disabled")
