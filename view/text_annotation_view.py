import tkinter as tk
from view.interfaces import ITextAnnotationView
from controller.interfaces import IController
# from view.text_display_frame import TextDisplayFrame
# from view.tagging_menu_frame import TaggingMenuFrame
from mockclasses.mock_tagging_menu_frame import MockTaggingMenuFrame
from mockclasses.mock_text_display_frame import MockTextDisplayFrame


class TextAnnotationView(tk.Frame, ITextAnnotationView):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the TextAnnotationView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller
        self.config(bg="red")

        self.render()

    def render(self) -> None:
        """
        Sets up the layout for the TextAnnotationView, adding the text display 
        and tagging menu frames within itself.
        """
        # Instantiate and pack the text display frame on the left side
        self._text_display_frame = MockTextDisplayFrame(self)
        self._text_display_frame.pack(side="left", fill="both", expand=True)

        # Instantiate and pack the tagging menu frame on the right side
        self._tagging_menu_frame = MockTaggingMenuFrame(self)
        self._tagging_menu_frame.pack(side="right", fill="y")

    def update(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could refresh the text display or tagging menu if necessary.
        """
        # Placeholder for update logic based on model changes
        print("TextAnnotationView has been updated based on model changes.")
