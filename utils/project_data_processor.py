from typing import Any, Dict

from controller.interfaces import IController
from enums.project_data_error import ProjectDataError
from input_output.interfaces import IFileHandler


class ProjectDataProcessor:
    def __init__(self, controller: IController, file_handler: IFileHandler):
        self._controller = controller
        self._file_handler = file_handler
        self._project_data = None

    def validate_and_complete(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        self._project_data = project_data
        print(f"DEBUG start {self._project_data=}")
        self._validate_initial()
        self._fix_validation_errors()
        self._normalize()
        self._complete()
        self._validate_final()
        return self._project_data

    # main steps
    def _validate_initial(self) -> None:
        """
        Performs initial validation checks on the provided project data.
        Populates self._errors with any validation issues found.
        """
        self._errors = []
        # check if data has required fields
        if not self._project_data.get("project_name", None):
            self._errors.append(ProjectDataError.EMPTY_PROJECT_NAME)
        if not self._project_data.get("selected_tags", []):
            self._errors.append(ProjectDataError.EMPTY_SELECTED_TAGS)
        if not self._project_data.get("tag_group_file_name", None):
            self._errors.append(ProjectDataError.EMPTY_TAG_GROUP_FILE_NAME)
        if not self._project_data.get("tag_groups", {}):
            self._errors.append(ProjectDataError.EMPTY_TAG_GROUPS)
        # check for duplicate project name
        if self._controller.project_name_exists(self._project_data.get("project_name", None)):
            self._errors.append(ProjectDataError.DUPLICATE_PROJECT_NAME)

    def _fix_validation_errors(self) -> None:
        """
        Handles any validation errors found during the initial validation phase.
        This method will repeatedly prompt the controller to handle errors until
        there are no more errors left to address.
        """
        while self._errors:
            for error in self._errors:
                self._controller.handle_project_data_error(error)
            self._validate_initial()

    def _normalize(self) -> None:
        """
        Normalizes the project data by ensuring unique tag names and valid tag group references.
        Note:
            This step modifies self._project_data in place to ensure consistency.
        """
        self._ensure_unique_tag_names()
        self._normalize_tag_groups()

    def _complete(self) -> None:
        self._collect_database_info()
        raise NotImplementedError("_complete method not implemented yet.")

    def _validate_final(self) -> None:
        raise NotImplementedError(
            "_validate_final method not implemented yet.")

    # detailed steps
    def _ensure_unique_tag_names(self) -> None:
        """
        Ensures that all tag names in the provided list are unique by appending a counter to duplicate names.
        """
        tags = self._project_data.get("selected_tags", [])
        for tag in tags:
            # store original name to find data configs later
            tag.setdefault("original_name", tag.get("name", "unknown"))
        while True:
            # search the duplicates
            tags_by_name = {}
            for tag in tags:
                tags_by_name.setdefault(tag["name"], []).append(tag)
            duplicates = {name: tag_list for name,
                          tag_list in tags_by_name.items() if len(tag_list) > 1}
            non_duplicates = [tag_list[0]
                              for _, tag_list in tags_by_name.items() if len(tag_list) == 1]
            if duplicates:
                renamed_duplicate_tags = self._controller.handle_project_data_error(ProjectDataError.TAG_NAME_DUPLICATES,
                                                                                    duplicates)
                if renamed_duplicate_tags is None:  # if user cancelled dialog
                    return
                tags = non_duplicates + renamed_duplicate_tags
                continue  # recheck for duplicates
            break  # loop until no duplicates are found
        self._project_data["selected_tags"] = tags

    def _normalize_tag_groups(self) -> None:
        """
        Normalizes the tag groups in the project data.
        Ensures that tag groups reference tags by their unique names.
        """
        tags = self._project_data.get("selected_tags", [])
        tag_groups = self._project_data.get("tag_groups", {})
        self._project_data["tag_groups"] = {group_name: [tag["name"] for tag in tags if tag["display_name"]
                                                         in tag_display_names] for group_name, tag_display_names in tag_groups.items()}

    def _collect_database_info(self) -> None:
        for tag in self._project_data.get("selected_tags", []):
            pass
            # def _collect_database_info(self) -> None:
            #     """
            #     Collects all relevant database information from the project data.
            #     Note: Adds a new field 'database_info' to self._project_data with structure
            #     {database_name:{csv_source_path:...,config:...}}
            #     """
            #     self._project_data["database_info"] = {}
            #     self._list_project_databases()
            #     self._complete_database_info()

            # def _list_project_databases(self) -> None:
            #     raise NotImplementedError(
            #         "_list_project_databases method not implemented yet.")

            # def _complete_database_info(self) -> None:
            #     raise NotImplementedError(
            #         "_complete_database_info method not implemented yet.")
