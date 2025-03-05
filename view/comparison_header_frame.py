import tkinter as tk
from tkinter import ttk
from typing import List
from controller.interfaces import IController
from observer.interfaces import IPublisher
from view.interfaces import IComparisonHeaderFrame


class ComparisonHeaderFrame(tk.Frame, IComparisonHeaderFrame):
    """
    A tkinter Frame that combines IO and Control widgets in a single grid layout.
    Includes directory selection, filter controls, action buttons, and annotation options.
    """

    def __init__(self, parent, controller):
        """
        Initializes the CombinedComparisonFrame with directory selection, controls, and annotation options.

        Args:
            parent (tk.Widget): The parent tkinter container for this frame.
            controller (IController): The controller managing interactions.
            default_directory (str): The default directory path to display in the entry.
            num_annotators (int): Number of annotators for radio buttons.
        """
        super().__init__(parent)
        self._controller: IController = controller
        self._num_files: int = 0
        self._radio_var = tk.IntVar()  # Shared variable for the radio buttons
        self.MAX_BUTTONS_PER_ROW = 8
        self._current_sentence_index: int = 0
        self._num_sentences: int = 0

        self._controller.add_observer(self)

        # self._render()

    def _render(self):
        """Sets up and arranges all widgets in a single grid layout."""
        # Filter Label, Combobox, and Start Button (Row 1)
        # self.filter_label = tk.Label(self, text="Filter:")
        # self.filter_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        # self.filter_var = tk.StringVar()
        # self.filter_combobox = ttk.Combobox(self, textvariable=self.filter_var)
        # self.filter_combobox['values'] = ("No Filter", "Timex3", "Geo")
        # self.filter_combobox.current(0)
        # self.filter_combobox.grid(
        #     row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=0)

        # self.start_button = ttk.Button(
        #     self, text="Start Comparison", command=self._on_button_pressed_start_comparison
        # )
        # self.start_button.grid(row=1, column=4, sticky="ew", padx=5, pady=0)

        # Radio Buttons Label (Row 2)
        self.radio_label = tk.Label(self, text="Choose preferred annotation:")
        self.radio_label.grid(row=2, column=0, columnspan=5,
                              sticky="w", padx=5, pady=0)

        # Frame for Radio Buttons (Row 3)
        radio_frame = tk.Frame(self)
        radio_frame.grid(row=3, column=0, columnspan=4,
                         sticky="ew", padx=5, pady=0)

        # Manual Annotation Radio Button
        manual_radio = tk.Radiobutton(
            radio_frame, text="Manual Annotation", variable=self._radio_var, value=0
        )
        manual_radio.grid(row=0, column=0, padx=5, pady=0, sticky="w")

        # Annotator Radio Buttons in multiple rows using grid
        for i in range(max(0, self._num_files-1)):
            # Calculate the row index
            row = ((i+1) // self.MAX_BUTTONS_PER_ROW)
            # Calculate the column index
            col = ((i+1) % self.MAX_BUTTONS_PER_ROW)

            radio_button = tk.Radiobutton(
                radio_frame, text=f"Annotator {i + 1}", variable=self._radio_var, value=i + 1
            )
            radio_button.grid(row=row, column=col,
                              padx=5, pady=0, sticky="w")

        # Overwrite Button (Row 3, Column 4)
        self.overwrite_button = ttk.Button(
            self, text="Overwrite", command=self._on_button_pressed_overwrite
        )
        self.overwrite_button.grid(
            row=2, column=4, sticky="ew", padx=5, pady=(5, 0))

        # Frame for current sentence and navigation
        nav_frame = tk.Frame(self)
        nav_frame.grid(row=3, column=4, padx=5, pady=(5, 0), sticky="ew")

        self.sentence_label = tk.Label(
            nav_frame, text=f"Current Sentence: {self._current_sentence_index+1}/{self._num_sentences}")
        self.sentence_label.pack(side=tk.LEFT, pady=0)

        self.prev_button = ttk.Button(
            nav_frame, text="<", command=self._on_button_pressed_prev_sentence)
        self.prev_button.pack(side=tk.LEFT, padx=0)

        self.next_button = ttk.Button(
            nav_frame, text=">", command=self._on_button_pressed_next_sentence)
        self.next_button.pack(side=tk.LEFT, padx=0)

        # Configure column resizing
        # Make column 1 expand horizontally
        self.grid_columnconfigure(1, weight=1)
        # Prevent column 0 from expanding
        self.grid_columnconfigure(0, weight=0)
        # Prevent column 4 from expanding
        self.grid_columnconfigure(4, weight=0)

    def update(self, publisher: IPublisher) -> None:
        """
        Retrieves updated data and layout information from the controller 
        and updates the view accordingly.

        This method fetches both data and layout state associated with this observer
        from the controller and processes it to refresh the displayed information.

        Args:
            publisher (IPublisher): The publisher that triggered the update.
        """
        state = self._controller.get_observer_state(self, publisher)

        # Update data-related attributes if available
        if "num_sentences" in state:
            self._num_sentences = state["num_sentences"]
        if "current_sentence_index" in state:
            self._current_sentence_index = state["current_sentence_index"]

        # Update layout-related attributes if available
        if "file_names" in state:
            self._num_files = len(state["file_names"])

        # Render the updated state
        self._render()

    # def _on_button_pressed_start_comparison(self):
    #     """Placeholder for start comparison logic."""
    #     pass

    def _on_button_pressed_overwrite(self):
        """Placeholder for overwrite logic."""
        pass

    def _on_button_pressed_prev_sentence(self) -> None:
        """
        Handles the event when the 'Previous Sentence' button is pressed.

        This method triggers the controller to switch to the previous sentence
        in the comparison view.
        """
        self._controller.perform_prev_sentence()

    def _on_button_pressed_next_sentence(self) -> None:
        """
        Handles the event when the 'Next Sentence' button is pressed.

        This method triggers the controller to switch to the next sentence
        in the comparison view.
        """
        self._controller.perform_next_sentence()

    def finalize_view(self) -> None:
        """
        Retrieves the layout state and updates the file_names before rendering the view.
        """
        state = self._controller.get_observer_state(self)
        if "num_sentences" in state:
            self._num_sentences = state["num_sentences"]
        if "current_sentence_index" in state:
            self._current_sentence_index = state["current_sentence_index"]
        if "file_names" in state:

            self._num_files = len(state["file_names"])
        self._render()
