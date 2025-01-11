from mockclasses.mock_template_loader import MockTemplateLoader
from observer.interfaces import ILayoutPublisher
from input_output.template_loader import TemplateLoader
from input_output.file_handler import FileHandler
from typing import List, Dict


class ConfigurationModel(ILayoutPublisher):
    """
    A configuration manager that provides access to templates and manages meta tag names 
    and template groups for the application.

    Attributes:
        meta_tag_names (List[str]): A list of names for meta tags.
        template_groups (List[Dict]): A list of dictionaries representing template groups.
    """

    def __init__(self):
        """
        Initializes the ConfigurationManager, setting up meta_tag_names and template_groups
        using the TemplateManager to retrieve templates.
        """
        self._template_loader = TemplateLoader()
        self._filehandler = FileHandler()

        # load default app paths
        self._app_paths = self._filehandler.read_file(
            "app_data/app_paths.json")

        # load the stored layout information
        self._saved_layout_path = self._app_paths["saved_layout"]
        saved_layout = self._filehandler.read_file(
            self._saved_layout_path)
        self.layout_state = {key: value for key, value in saved_layout.items()}

        project_path = f"{self._app_paths['default_project_config']}{saved_layout['project']}/"

        self.layout_state["template_groups"] = self._template_loader.load_template_groups(
            project_path)

        self.layout_state

    def get_layout_state(self) -> Dict:
        """Retrieves the layout state of the application."""
        return self.layout_state
