from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from controller.interfaces import IController


class ExtractionFrame(tk.Frame):
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
        # Label for PDF Path
        self.label_pdf_path = tk.Label(self, text="PDF Path")
        self.label_pdf_path.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Entry widget for PDF Path
        self.pdf_path_entry = tk.Entry(self)
        self.pdf_path_entry.grid(
            row=1, column=0, columnspan=2, padx=10, pady=0, sticky='ew')

        # Button for choosing a file
        self.button_choose_file = ttk.Button(
            self, text="Choose File", command=self._on_button_pressed_choose_file)
        self.button_choose_file.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Label for page ranges
        self.label_page_ranges = tk.Label(self, text="Page ranges")
        self.label_page_ranges.grid(
            row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Entry widget for inputting page ranges
        self.page_range_entry = tk.Entry(self)
        self.page_range_entry.grid(
            row=4, column=0, columnspan=2, padx=10, pady=0, sticky='ew')

        # Label for page margins
        self.label_page_margins = tk.Label(self, text="Page margins")
        self.label_page_margins.grid(
            row=5, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # Entry widget for inputting page margins
        self.page_margins_entry = tk.Entry(self)
        self.page_margins_entry.grid(
            row=6, column=0, columnspan=2, padx=10, pady=0, sticky='ew')

        # # Label for document type
        # self.label_document_type = tk.Label(self, text="Document type")
        # self.label_document_type.grid(
        #     row=7, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        # # Radio buttons for document type
        # self.document_type = tk.StringVar(value="A4")
        # self.radio_a4 = tk.Radiobutton(
        #     self, text="A4 Document", variable=self.document_type, value="A4")
        # self.radio_brochure = tk.Radiobutton(
        #     self, text="Brochure", variable=self.document_type, value="Brochure")

        # self.radio_a4.grid(row=8, column=0, padx=10, pady=5, sticky='e')
        # self.radio_brochure.grid(row=8, column=1, padx=10, pady=5, sticky='w')

        # Button to initiate the extraction of pages
        self.button_extract = ttk.Button(
            self, text="Extract pages", command=self._on_button_pressed_extract_pages)
        self.button_extract.grid(
            row=9, column=0, columnspan=2, padx=20, pady=10, sticky='ew')

        # Button to adopt the text
        self.button_adopt_text = ttk.Button(
            self, text="Adopt text", command=self._on_button_pressed_adopt_text)
        self.button_adopt_text.grid(
            row=10, column=0, columnspan=2, padx=20, pady=10, sticky='ew')

    def _on_button_pressed_choose_file(self) -> None:
        """
        Opens a file dialog to select a PDF file and updates the PDF path entry.

        This method uses a file dialog to allow the user to select a PDF file.
        The selected file path is then displayed in the PDF path entry widget.
        """
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self.pdf_path_entry.delete(0, tk.END)
            self.pdf_path_entry.insert(0, file_path)

    def update(self) -> None:
        """
        Updates the view in response to notifications from the observed object.
        This method could be used to refresh the view if the PDF data changes
        or if new data needs to be loaded/displayed.
        """
        print("PDFExtractionView has been updated based on model changes.")

    def _on_button_pressed_extract_pages(self) -> None:
        """
        Handler for the extract button. Invokes the controller's method for PDF extraction.
        """
        extraction_data = {"page_range": self.page_range_entry.get(),
                           "page_margins": self.page_margins_entry.get()
                           }
        self._controller.perform_pdf_extraction(extraction_data)

    def _on_button_pressed_adopt_text(self) -> None:
        """
        Handler for the adopt text button. Invokes the controller's method to 
        adopt the extracted text.
        """
        self._controller.perform_text_adoption()
