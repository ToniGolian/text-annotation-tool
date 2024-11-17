import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController


class PDFExtractionFrame(tk.Frame):
    def __init__(self, parent: tk.Widget, controller: IController) -> None:
        """
        Initializes the PDFExtractionView with a reference to the parent widget and controller.

        Args:
            parent (tk.Widget): The parent widget where this frame will be placed.
            controller (IController): The controller managing actions for this view.
        """
        super().__init__(parent)
        self._controller = controller

        # Configure the grid layout manager
        # Ensure the column expands to fill the frame
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self._render()

    def _render(self) -> None:
        # Label for page ranges
        self.label_page_ranges = tk.Label(self, text="Page ranges")
        self.label_page_ranges.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Entry widget for inputting page ranges
        self.page_range_entry = tk.Entry(self)
        self.page_range_entry.grid(
            row=1, column=0, columnspan=2, padx=10, pady=0, sticky='ew')
        # self.entry_tooltip = ToolTip(
        #     self.page_range_entry, "Enter page ranges in the format: page-page, page-page\ne.g.1-5, 7, 10-12, ...")

        # Label for page margins
        self.label_page_margins = tk.Label(self, text="Page margins")
        self.label_page_margins.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        # Entry widget for inputting page margins
        self.page_margins_entry = tk.Entry(self)
        self.page_margins_entry.grid(
            row=3, column=0, columnspan=2, padx=10, pady=0, sticky='ew')
        # self.entry_tooltip = ToolTip(
        #     self.page_margins_entry, "Enter page margins e.g. in the format: left_margin, top_margin, right_margin, bottom_margin\ne.g. 72,72,72,72\nor just one number if all margins are the same")

        # Label for document type
        self.label_page_margins = tk.Label(self, text="Dokument type")
        self.label_page_margins.grid(
            row=4, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        # Radio button for choosing between A4 documents and brochures
        # Default selection is A4 documents
        self.document_type = tk.StringVar(value="A4")
        self.radio_a4 = tk.Radiobutton(
            self, text="A4 Document", variable=self.document_type, value="A4")
        self.radio_brochure = tk.Radiobutton(
            self, text="Brochure", variable=self.document_type, value="Brochure")

        self.radio_a4.grid(row=5, column=0, padx=10, pady=5,
                           sticky='e')  # Adjust row accordingly
        self.radio_brochure.grid(
            row=5, column=1, padx=10, pady=5, sticky='w')

        # Button to initiate the extraction of pages
        self.button = ttk.Button(
            self, text="Extract pages", command=self._on_button_pressed_extract_pages)
        self.button.grid(row=6, column=0, columnspan=2,
                         padx=20, pady=10, sticky='ew')

    def update(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could be used to refresh the view if the PDF data changes
        or if new data needs to be loaded/displayed.
        """
        # Implement logic to update the view, e.g., refreshing data or resetting fields
        print("PDFExtractionView has been updated based on model changes.")

    def _on_button_pressed_extract_pages(self) -> None:
        """
        Handler for the extract button. Invokes the controller's command to 
        execute the PDF extraction.
        """
        # Example command: Call a method on the controller to start PDF extraction
        # This would actually be a command object or method call
        self._controller.execute_command("extract_pdf")
