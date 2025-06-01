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
        self._app_paths_file = "app_data/app_paths.json"
        self._paths: dict = {}
        self._project: str = self._resolve_project_name()
        self._build_paths(self._project)

    def _resolve_project_name(self) -> str:
        """
        Resolves the project name from config or falls back to first existing folder.

        Returns:
            str: The name of the active project.

        Raises:
            FileNotFoundError: If the project root directory is missing.
            RuntimeError: If no projects are available.
        """
        with open(self._app_paths_file, "r", encoding="utf-8") as f:
            app_paths = json.load(f)

        path_to_last_project = app_paths.get(
            "path_to_last_project", "").strip()

        if path_to_last_project and os.path.exists(path_to_last_project):
            with open(path_to_last_project, "r", encoding="utf-8") as f:
                last_project_config = json.load(f)
                project_name = last_project_config.get(
                    "last_project", "").strip()
                if project_name:
                    return project_name

        project_root = os.path.join("app_data", "projects")
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

    def _build_paths(self, project_name: str) -> None:
        """
        Rebuilds the internal path mapping for the given project name.

        Args:
            project_name (str): The new project to resolve paths for.
        """
        self._project = project_name
        with open(self._app_paths_file, "r", encoding="utf-8") as f:
            raw_paths = json.load(f)

        self._paths = {
            key: os.path.normpath(path.replace("<project>", self._project))
            for key, path in raw_paths.items()
        }

    def get_path(self, key: str) -> str:
        """
        Retrieves a fully resolved and normalized path for a given key.

        Args:
            key (str): The path identifier defined in app_paths.json.

        Returns:
            str: The expanded, normalized file path.

        Raises:
            KeyError: If the key is not defined.
        """
        if key not in self._paths:
            raise KeyError(f"Path key '{key}' not found in configuration.")
        return self._paths[key]

    def update_project(self, new_project: str) -> None:
        """
        Updates the current project and rebuilds all paths accordingly.

        Args:
            new_project (str): The new project name to apply.
        """
        self._build_paths(new_project)

    def get_project_name(self) -> str:
        """
        Returns the currently active project name.

        Returns:
            str: The project name.
        """
        return self._project
