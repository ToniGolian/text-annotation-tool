from typing import List, Tuple
from controller.interfaces import IController
from model.highlight_model import HighlightModel
from observer.interfaces import IPublisher
from view.text_display_frame import TextDisplayFrame
import tkinter as tk


class AnnotationTextDisplayFrame(TextDisplayFrame):
    """
    A specialized TextDisplayFrame for annotation purposes.
    """

    def __init__(self, parent: tk.Widget, controller: IController, is_static_observer: bool = False, height: int = None) -> None:
        super().__init__(parent=parent, controller=controller,
                         editable=False, is_static_observer=is_static_observer, height=height)

    def update(self, publisher: IPublisher) -> None:
        """
        Updates the displayed text and refreshes text highlighting.

        This method retrieves the latest highlight data, removes any existing highlights,
        and applies the new highlights to the text.
        """
        super().update(publisher)
        print(f"DEBUG update {self.__class__.__name__} {publisher}")
        if isinstance(publisher, HighlightModel):
            highlight_data = self._controller.get_observer_state(
                self, publisher).get("highlight_data", [])
            print(f"DEBUG {highlight_data=}")
            self.unhighlight_text()
            self.highlight_text(highlight_data)

    def highlight_text(self, highlight_data: List[Tuple[str, int, int]]) -> None:
        """
        Applies text highlighting based on the provided highlight data.

        Args:
            highlight_data (List[Tuple[str, int, int]]): A list of tuples containing:
                - str: The highlight color.
                - int: The start position of the highlight in the text.
                - int: The end position of the highlight in the text.
        """
        for (bg_color, font_color, start, end) in highlight_data:
            tag_name = f"highlight_{bg_color}"
            self.text_widget.tag_configure(
                tag_name, background=bg_color, foreground=font_color)
            start_index = f"1.0+{start}c"
            end_index = f"1.0+{end}c"
            self.text_widget.tag_add(tag_name, start_index, end_index)

    def unhighlight_text(self) -> None:
        """
        Removes all existing text highlights.

        This method iterates through all existing highlight tags and removes them from the text widget.
        """
        for tag in self.text_widget.tag_names():
            if tag.startswith("highlight_"):
                self.text_widget.tag_remove(tag, "1.0", "end")
