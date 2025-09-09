from typing import Any, Dict

from controller.interfaces import IController
from enums.project_data_error import ProjectDataError


class ProjectDataProcessor:
    def __init__(self, controller: IController):
        self._controller = controller
        self._project_data = None

    def validate_and_complete(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        self._project_data = project_data
        self._validate_initial()
        self._fix_validation_errors()
        self._normalize()
        self._complete()
        self._validate_final()
        return self._project_data

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
        if self._controller.project_name_exists():
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
        self._ensure_unique_tag_names()

    def _complete(self) -> None:
        pass

    def _validate_final(self) -> None:
        pass

    def _ensure_unique_tag_names(self) -> None:
        """
        Ensures that all tag names in the provided list are unique by appending a counter to duplicate names.
        """
        tags = self._project_data.get("selected_tags", [])
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
                renamed_duplicate_tags = self._controller.ask_user_for_tag_duplicates(
                    duplicates)
                if renamed_duplicate_tags is None:  # if user cancelled dialog
                    return
                tags = non_duplicates + renamed_duplicate_tags
                continue  # recheck for duplicates
            break  # loop until no duplicates are found
        self._project_data["selected_tags"] = tags
