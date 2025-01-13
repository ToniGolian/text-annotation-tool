from mockclasses.mock_template_loader import MockTemplateLoader
from observer.interfaces import ILayoutPublisher
from input_output.template_loader import TemplateLoader
from input_output.file_handler import FileHandler
from typing import List, Dict


class ConfigurationModel(ILayoutPublisher):
    """
    A configuration manager that provides access to templates and manages meta tag names 
    and template groups for the application.
    """

    def __init__(self):
        """
        Initializes the ConfigurationManager, including layout observers and layout state.
        """
        super().__init__()  # Call the constructor of the ILayoutPublisher to initialize layout observers
        self._template_loader = TemplateLoader()
        self._filehandler = FileHandler()

        # Load default application paths
        self._app_paths = self._filehandler.read_file(
            "app_data/app_paths.json")

        # Load the stored layout information
        self._saved_layout_path = self._app_paths["saved_layout"]
        saved_layout = self._filehandler.read_file(self._saved_layout_path)
        self.layout_state = {key: value for key, value in saved_layout.items()}

        # Load template groups based on the saved project path
        project_path = f"{self._app_paths['default_project_config']}{saved_layout['project']}/"
        self.layout_state["template_groups"] = self._template_loader.load_template_groups(
            project_path)

    def get_layout_state(self) -> Dict:
        """Retrieves the layout state of the application."""
        return self.layout_state
