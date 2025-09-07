from input_output.interfaces import IFileHandler


class ProjectDirectoryManager:
    def create_project_structure(self, file_handler: IFileHandler, project_name: str) -> None:
        base_path = file_handler.get_project_base_path()
