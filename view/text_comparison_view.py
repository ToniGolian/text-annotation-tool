import tkinter as tk
from view.interfaces import ITextComparisonView
from controller.interfaces import IController
# from view.comparison_display_frame import ComparisonDisplayFrame
# from view.tagging_menu_frame import TaggingMenuFrame
from mockclasses.mock_tagging_menu_frame import MockTaggingMenuFrame
from mockclasses.mock_text_display_frame import MockTextDisplayFrame


class TextComparisonView(tk.Frame, ITextComparisonView):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the TextComparisonView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller

        self.render()

    def render(self) -> None:
        """
        Sets up the layout for the TextComparisonView, adding the comparison display 
        and control frames within itself.
        """
        # Instantiate and pack the comparison display frame on the top
        self._comparison_display_frame = MockTextDisplayFrame(self)
        self._comparison_display_frame.pack(
            side="top", fill="both", expand=True)

        # Instantiate and pack the comparison control frame on the bottom
        self._comparison_control_frame = MockTaggingMenuFrame(self)
        self._comparison_control_frame.pack(side="bottom", fill="x")

    def update(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could refresh the comparison display or control frame if necessary.
        """
        # Placeholder for update logic based on model changes
        print("TextComparisonView has been updated based on model changes.")
