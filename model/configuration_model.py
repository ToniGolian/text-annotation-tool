from observer.interfaces import IPublisher
from input_output.template_loader import TemplateLoader
from input_output.file_handler import FileHandler
from typing import Dict, List


class ConfigurationModel(IPublisher):
    """
    Manages application configuration, including templates, meta tag names, 
    template groups, and layout settings.

    This class loads and provides access to configuration-related data such as 
    project settings, template groups, and the color scheme. It also maintains 
    and retrieves the current layout state of the application.
    """

    def __init__(self):
        """
        Initializes the ConfigurationModel and loads essential configuration files.

        This constructor initializes dependencies, loads application paths, 
        retrieves project-specific settings, and sets up the initial layout state.
        """
        super().__init__()  # Initialize the IPublisher base class

        # Load essential components
        self._template_loader = TemplateLoader()
        self._filehandler = FileHandler()

        # Load default application paths
        self._app_paths = self._filehandler.read_file(
            "app_data/app_paths.json")

        # Retrieve stored layout configuration path
        self._saved_layout_path = self._app_paths["saved_layout"]

        # Extract project name and build project configuration path
        self._project = self._filehandler.read_file(
            self._saved_layout_path).get("project", "")
        self._project_path = f"{self._app_paths['default_project_config']}{self._project}/"

        # Define path for the color scheme configuration
        self._color_path = self._project_path + "color_scheme.json"

        # Initialize layout state
        self.update_state()

    def update_state(self) -> None:
        """
        Updates the current layout state of the application.

        This method reads the saved layout configuration from a file and 
        updates the `layout_state` attribute with relevant UI settings. 
        It also loads template groups associated with the current project.
        """
        # Load the saved layout configuration
        self._saved_layout = self._filehandler.read_file(
            self._saved_layout_path)

        # Store all key-value pairs from the saved layout
        self.layout_state = {key: value for key,
                             value in self._saved_layout.items()}

        # Load and add template groups based on the saved project path
        self.layout_state["template_groups"] = self._template_loader.load_template_groups(
            self._project_path)

    def get_state(self) -> Dict:
        """
        Retrieves the current layout state of the application.

        This method returns a dictionary containing key-value pairs that define 
        the current layout configuration, including window positions, panel 
        visibility, and other UI settings.

        Returns:
            Dict: A dictionary representing the current layout state.
        """
        return self.layout_state

    def get_color_scheme(self) -> Dict:
        """
        Retrieves the current color scheme used in the application.

        This method loads and returns a dictionary containing UI color settings. 
        The color scheme defines the visual appearance, including background, 
        foreground, and highlight colors.

        Returns:
            Dict: A dictionary mapping UI elements to their respective colors.
        """
        self._color_scheme = self._filehandler.read_file(self._color_path)
        return self._color_scheme

    def get_tag_types(self) -> List[str]:
        """
        Extracts and returns all available tag types from the loaded template groups.

        This method iterates through the template groups and collects unique 
        tag types used within the templates.

        Returns:
            List[str]: A list of unique tag types found in the template groups.
        """
        tag_types = []

        # Extract tag types from all template groups
        for group in self.layout_state["template_groups"]:
            for template in group.get("templates", []):
                tag_types.append(template.get("type", ""))
        return tag_types
