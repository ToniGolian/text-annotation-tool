from typing import Any, Dict

from controller.interfaces import IController
from enums.project_data_error import ProjectDataError
from input_output.interfaces import IFileHandler


class ProjectDataProcessor:
    def __init__(self, controller: IController, file_handler: IFileHandler):
        self._controller: IController = controller
        self._file_handler: IFileHandler = file_handler
        self._project_data: dict[str, any] = None
        # self._build_data: dict[str, any] = None

    def validate_and_complete(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"DEBUG validate_and_complete")
        self._project_data = project_data
        self._validate_initial()
        self._fix_validation_errors()
        self._normalize()
        self._complete()
        self._validate_final()
        self._create_build_data()
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
        if self._controller.does_project_exist(self._project_data.get("project_name", None)):
            self._errors.append(ProjectDataError.DUPLICATE_PROJECT_NAME)
        print(f"DEBUG {self._errors=}")

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
        self._add_database_info()

    def _complete(self) -> None:
        self._create_project_settings()
        self._create_build_data()

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
        are_tag_names_modified = False
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
                are_tag_names_modified = True
                if renamed_duplicate_tags is None:  # if user cancelled dialog
                    return
                tags = non_duplicates + renamed_duplicate_tags
                continue  # recheck for duplicates
            break  # loop until no duplicates are found
        self._project_data["selected_tags"] = tags
        self._project_data["are_tag_names_modified"] = are_tag_names_modified

    def _normalize_tag_groups(self) -> None:
        """
        Normalizes the tag groups in the project data.
        Ensures that tag groups reference tags by their unique names.
        """
        tags = self._project_data.get("selected_tags", [])
        tag_groups = self._project_data.get("tag_groups", {})
        self._project_data["tag_groups"] = {group_name: [tag["name"] for tag in tags if tag["display_name"]
                                                         in tag_display_names] for group_name, tag_display_names in tag_groups.items()}

    def _add_database_info(self) -> None:
        """
        Adds database information to tags that require it by loading the relevant project settings.
        """
        for tag in self._project_data.get("selected_tags", []):
            # collect needed database
            if not tag.get("needs_database", False):
                continue

            tag_project = tag.get("project", "")
            if not tag_project:
                raise ValueError(
                    f"Tag {tag['name']} needs database but has no project assigned.")

            tag_original_name = tag.get("original_name", "")
            with self._file_handler.use_project(tag_project):
                project_settings = self._file_handler.read_file(
                    "project_Settings")
                tag_database = project_settings.get("tags", {}).get(
                    tag_original_name, {}).get("database", {})
                if not tag_database:
                    raise ValueError(
                        f"Tag {tag['name']} needs database but no database info found in project settings of project {tag_project}.")
                tag["database"] = tag_database

    def _create_project_settings(self) -> None:
        """
        Creates the project settings based on the provided project data.
        This method constructs a settings dictionary that includes project name, tags, groups,
        and other default settings, and adds it to the project data.
        """
        default_settings = self._file_handler.read_file(
            "project_settings_defaults")
        settings = {}
        settings["name"] = self._project_data.get("project_name", "")
        # tags and groups
        settings["tags"] = {tag["name"]: {"file_name": f"{tag['name']}.json", "database": tag.get(
            "database", {})} for tag in self._project_data.get("selected_tags", [])}
        settings["current_group_file"] = self._project_data.get(
            "tag_group_file_name", "")
        settings["group_files"] = [
            self._project_data.get("tag_group_file_name", "groups01.json")]

        # other settings with defaults
        settings["search_normalization"] = default_settings.get(
            "default_search_normalization", "search_normalization_rules.json")
        settings["color_scheme"] = default_settings.get(
            "default_color_scheme", "magma_comp_search_color_scheme.json")
        settings["are_all_search_results_highlighted"] = default_settings.get(
            "default_are_all_search_results_highlighted", True)
        settings["current_language"] = default_settings.get(
            "default_language", "english")
        settings["abbreviations"] = default_settings.get(
            "default_abbreviations", "abbreviations.json")
        settings["suggestions"] = default_settings.get(
            "default_suggestions", "suggestions.json")
        settings["wrong_suggestions"] = default_settings.get(
            "default_wrong_suggestions", "wrong_suggestions.json")
        self._project_data["settings"] = settings

    def _create_build_data(self) -> None:

        build_data = {}
