import tkinter as tk


class SearchFrame(tk.Frame):
    """
    A frame for user-driven text search with support for case sensitivity, whole word,
    and regular expression options. The frame includes a label, toggle buttons, and a text entry.

    Debounced input ensures that searches are only triggered after a short pause in typing.
    """

    def __init__(self, parent: tk.Widget, controller: object) -> None:
        """
        Initializes the SearchFrame UI and binds the input logic.

        Args:
            parent (tk.Widget): The parent widget to attach this frame to.
            controller (object): The controller responsible for handling the search logic.
        """
        super().__init__(parent)
        self._controller = controller
        self._debounce_id: int | None = None

        label = tk.Label(self, text="Search")
        label.grid(row=0, column=0, columnspan=3, pady=(5, 2))

        self._case_button = tk.Checkbutton(self, text="Aa", indicatoron=False)
        self._whole_word_button = tk.Checkbutton(
            self, text="ab_", indicatoron=False)
        self._regex_button = tk.Checkbutton(self, text="□*", indicatoron=False)

        self._case_button.grid(row=1, column=0, sticky="ew", padx=2)
        self._whole_word_button.grid(row=1, column=1, sticky="ew", padx=2)
        self._regex_button.grid(row=1, column=2, sticky="ew", padx=2)

        self._initialize_button_vars()

        self._entry = tk.Entry(self)
        self._entry.grid(row=2, column=0, columnspan=3,
                         sticky="ew", pady=(5, 5), padx=2)
        self._entry.bind("<KeyRelease>", self._on_entry_changed)

        for i in range(3):
            self.columnconfigure(i, weight=1)

    def _initialize_button_vars(self) -> None:
        """
        Initializes internal state variables for toggle buttons.
        """
        self._case_button.var = tk.IntVar()
        self._whole_word_button.var = tk.IntVar()
        self._regex_button.var = tk.IntVar()

        self._case_button.config(variable=self._case_button.var)
        self._whole_word_button.config(variable=self._whole_word_button.var)
        self._regex_button.config(variable=self._regex_button.var)

    def _on_entry_changed(self, event: tk.Event) -> None:
        """
        Debounced event handler for user input in the search entry.

        Cancels any pending search trigger and schedules a new one.
        """
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(300, self._trigger_search)

    def _trigger_search(self) -> None:
        """
        Collects current search parameters and initiates the manual search via controller.
        """
        search_term: str = self._entry.get().strip()
        case_sensitive: bool = bool(self._case_button.var.get())
        whole_word: bool = bool(self._whole_word_button.var.get())
        regex: bool = bool(self._regex_button.var.get())

        self._controller.perform_manual_search(
            search_term=search_term,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            regex=regex
        )
