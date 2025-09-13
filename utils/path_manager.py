import os
import json


class PathManager:
    """
    Resolves and manages project-specific file paths centrally.

    Loads path templates from app_paths.json and expands <project> placeholders
    using the active project name. Paths can be recomputed when switching projects.
    """

    def __init__(self) -> None:
        """
        Initializes the path manager by resolving the current project name
        and building the expanded path mapping.

        """
        self._app_paths_file = "app_data/app/config/app_paths.json"
        # initial load without project context to be able to read some files in init
        self._paths: dict = self._load_project_independent_paths()

    def get_last_project_name(self) -> str:
        """
        Resolves the project name from config or falls back to first existing directory.

        Returns:
            str: The name of the last project.

        Raises:
            FileNotFoundError: If the project root directory is missing.
            RuntimeError: If no projects are available.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as f:
            app_paths = json.load(f)

        path_to_last_project = app_paths.get(
            "last_project", "").strip()

        if path_to_last_project and os.path.exists(path_to_last_project):
            with open(path_to_last_project, "r", encoding="utf-8") as f:
                last_project_config = json.load(f)
                project_name = last_project_config.get(
                    "last_project", "").strip()
                if project_name:
                    return project_name

        project_root = os.path.join("app_data", "project_directory")
        try:
            projects = [
                name for name in os.listdir(project_root)
                if os.path.isdir(os.path.join(project_root, name))
            ]
        except FileNotFoundError:
            raise FileNotFoundError(
                "Project directory 'app_data/projects' does not exist.")

        if not projects:
            raise RuntimeError("No projects found in 'app_data/projects'.")

        return projects[0]

    def update_paths(self, project_name: str) -> None:
        """
        Rebuilds the internal path mapping for the given project name.

        Args:
            project_name (str): The new project to resolve paths for.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as f:
            raw_paths = json.load(f)

        self._paths = {
            key: os.path.normpath(path.replace("<project>", project_name))
            for key, path in raw_paths.items()
        }

    def resolve_path(self, key_or_path: str) -> str:
        """
        Resolves a configuration key to a full file path, or returns the path as-is
        if it's already a real path.

        Args:
            key_or_path (str): Key from config or already-resolved file path.

        Returns:
            str: Fully resolved and normalized file path.
        """
        if key_or_path in self._paths:
            return self._paths[key_or_path]
        return os.path.normpath(key_or_path)

    def _load_project_independent_paths(self) -> dict:
        """
        Loads paths from app_paths.json without expanding <project>.

        This is used during initialization before any project is selected.

        Returns:
            dict: Raw path templates from app_paths.json.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as f:
            raw_paths = json.load(f)
        project_independent_paths = {
            key: path for key, path in raw_paths.items() if "<project>" not in path}
        return project_independent_paths
