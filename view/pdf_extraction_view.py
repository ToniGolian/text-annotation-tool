import tkinter as tk
from view.interfaces import IPDFExtractionView
from controller.interfaces import IController


class PDFExtractionView(tk.Frame, IPDFExtractionView):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the PDFExtractionView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller

        self.render()

    def render(self) -> None:
        """
        Sets up the layout for the PDFExtractionView, creating the main frame 
        and adding all necessary widgets.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.

        Returns:
            tk.Frame: The main frame for PDF extraction view.
        """
        # Add PDF extraction widgets here (e.g., buttons, labels, text boxes)
        extract_button = tk.Button(
            self, text="Extract PDF", command=self._on_extract)
        extract_button.pack(pady=10)

        self.pack(fill="both", expand=True)

    def update(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could be used to refresh the view if the PDF data changes
        or if new data needs to be loaded/displayed.
        """
        # Implement logic to update the view, e.g., refreshing data or resetting fields
        print("PDFExtractionView has been updated based on model changes.")

    def _on_extract(self) -> None:
        """
        Handler for the extract button. Invokes the controller's command to 
        execute the PDF extraction.
        """
        # Example command: Call a method on the controller to start PDF extraction
        # This would actually be a command object or method call
        self._controller.execute_command("extract_pdf")
