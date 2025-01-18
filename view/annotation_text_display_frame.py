from controller.interfaces import IController
from view.text_display_frame import TextDisplayFrame
import tkinter as tk


class AnnotationTextDisplayFrame(TextDisplayFrame):
    """
    A specialized TextDisplayFrame for annotation purposes.
    """

    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        super().__init__(parent=parent, controller=controller, editable=False)
