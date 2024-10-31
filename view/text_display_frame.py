# view/text_display_frame.py

import tkinter as tk
from view.interfaces import ITextDisplayFrame
from controller.controller import Controller

class TextDisplayFrame(tk.Frame, ITextDisplayFrame):
    def __init__(self, parent: tk.Widget, controller: Controller) -> None:
        """
        Initializes the TextDisplayFrame with a reference to the controller.
        Registers itself as an observer of the model via the controller.
        
        Args:
            parent (tk.Widget): The parent widget in which this frame will be displayed.
            controller (Controller): The controller managing the interaction between the view and model.
        """
        super().__init__(parent)
        self.controller = controller
        self.controller.register_observer(self)  # Register as observer through the controller
        self.render()
    
    def render(self) -> None:
        """
        Sets up the text display widget within the frame. This is where the tk.Text widget is created
        and packed to fill the frame.
        """
        self.text_widget = tk.Text(self)
        self.text_widget.pack(fill="both", expand=True)

    def update(self, text: str) -> None:
        """
        Called when the model notifies observers of a change.
        Updates the text content in the text_widget based on the provided text.

        Args:
            text (str): The new text content from the model to display in the text_widget.
        """
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", text)
