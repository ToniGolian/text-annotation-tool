from observer.interfaces import IPublisher
from input_output.template_loader import TemplateLoader
from input_output.file_handler import FileHandler
from typing import Dict


class ConfigurationModel(IPublisher):
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
        self._project = self._filehandler.read_file(
            self._saved_layout_path).get("project", "")
        self._project_path = f"{self._app_paths['default_project_config']}{self._project}/"

    def get_state(self) -> Dict:
        """
        Retrieves the current layout state of the application.

        This method returns a dictionary representing the layout configuration
        of the application. The layout state may include information such as 
        window positions, panel visibility, and other UI-related settings.

        Returns:
            Dict: A dictionary containing key-value pairs that define the 
                current layout state of the application.
        """
        saved_layout = self._filehandler.read_file(self._saved_layout_path)
        layout_state = {key: value for key, value in saved_layout.items()}

        # Load template groups based on the saved project path
        layout_state["template_groups"] = self._template_loader.load_template_groups(
            self._project_path)
        return layout_state

    def get_color_scheme(self) -> Dict:
        """
        Retrieves the current color scheme of the application.

        This method returns a dictionary containing the color scheme settings 
        used in the application. The color scheme typically defines UI colors 
        such as background, foreground, and highlight colors.

        Returns:
            Dict: A dictionary mapping UI elements to their corresponding colors.
        """
        color_path = self._project_path+"color_scheme.json"
        color_scheme = self._filehandler.read_file(color_path)

        return color_scheme
