import platform
import tkinter as tk
from tkinter import ttk
from observer.interfaces import IObserver, IPublisher
from view.extraction_view import ExtractionView
from view.annotation_view import AnnotationView
from view.comparison_view import ComparisonView
from controller.interfaces import IController


class MainWindow(tk.Tk, IObserver):
    def __init__(self, controller: IController) -> None:
        super().__init__()

        self.DEFAULT_NOTEBOOK_INDEX = 0
        self._controller = controller

        self._annotation_view = None
        self._extraction_view = None
        self._comparison_view = None

        if platform.system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        self.title("Text Annotation Tool")

        self._create_menu()
        self._render()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._controller.add_observer(self)

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self)
        self._notebook = ttk.Notebook(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self._on_open)
        file_menu.add_command(label="Save", command=self._on_save)
        file_menu.add_command(label="Save as", command=self._on_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(
            label="Preferences", command=self._on_preferences)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.config(menu=menu_bar)

    def _render(self) -> None:
        self._notebook.pack(fill="both", expand=True)

        self._extraction_view = ExtractionView(
            parent=self._notebook, controller=self._controller)
        self._notebook.add(self._extraction_view, text="PDF Extraction")

        self._annotation_view = AnnotationView(
            parent=self._notebook, controller=self._controller)
        self._notebook.add(self._annotation_view, text="Text Annotation")

        self._comparison_view = ComparisonView(
            parent=self._notebook, controller=self._controller)
        self._notebook.add(self._comparison_view, text="Text Comparison")

        active_views = ["extraction", "annotation", "comparison"]
        self._notebook.select(self.DEFAULT_NOTEBOOK_INDEX)
        self._controller.set_active_view(
            active_views[self.DEFAULT_NOTEBOOK_INDEX])

    def _on_open(self):
        config = self._controller.get_open_file_config()
        initial_dir = config.get("initial_dir", ".")
        filetypes = config.get("filetypes", [("All Files", "*.*")])
        title = config.get("title", "Open File")
        multi_select = config.get("multiselect", False)

        try:
            if multi_select:
                file_paths = tk.filedialog.askopenfilenames(
                    initialdir=initial_dir, filetypes=filetypes, title=title)
            else:
                file_paths = [tk.filedialog.askopenfilename(
                    initialdir=initial_dir, filetypes=filetypes, title=title)]

            file_paths = [path for path in file_paths if path]
        except Exception as e:
            print(f"Error during open file dialog: {e}")
        if file_paths:
            self._controller.perform_open_file(file_paths)

    #!DEPRECATED
    def _on_save_as(self):
        if self._controller.get_active_view() == "comparison":
            self._controller.perform_save_as(None)
            return

        try:
            config = self._controller.get_save_as_config()
            initial_dir = config.get("initial_dir", ".")
            filetypes = config.get("filetypes", [("All Files", "*.*")])
            defaultextension = config.get("defaultextension", "")
            title = config.get("title", "Save File As")

            file_path = tk.filedialog.asksaveasfilename(
                initialdir=initial_dir,
                filetypes=filetypes,
                defaultextension=defaultextension,
                title=title
            )

            if file_path:
                self._controller.perform_save_as(file_path)

        except Exception as e:
            print(f"Error during save as file dialog: {e}")

    def _on_save(self) -> None:
        file_path = self._controller.get_file_path()
        if file_path:
            self._controller.perform_save_as(file_path)
        else:
            self._on_save_as()
            #!END DEPRECATED

    def _on_save(self) -> None:
        self._controller.perform_save()

    def _on_save_as(self) -> None:
        self._controller.perform_save_as()

    def _on_preferences(self):
        print("Preferences dialog not implemented yet.")

    def _on_closing(self):
        self.destroy()

    def update(self, publisher: IPublisher) -> None:
        state = self._controller.get_observer_state(self, publisher)
        if "active_notebook_index" in state:
            self._notebook.select(state["active_notebook_index"])
            if state["active_notebook_index"] == 1:
                self._annotation_view.focus_set()
