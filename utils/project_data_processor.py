from controller.interfaces import IController
from enums.project_data_error import ProjectDataError
from exceptions.project_creation_aborted import ProjectCreationAborted
from input_output.interfaces import IFileHandler


class ProjectDataProcessor:
    def __init__(self, controller: IController, file_handler: IFileHandler):
        self._controller: IController = controller
        self._file_handler: IFileHandler = file_handler
        self._project_data: dict[str, any] = None
        # self._build_data: dict[str, any] = None

    def get_project_build_data(self, project_data: dict[str, any]) -> dict[str, any]:
        """
        Converts and processes the provided project data into a structured build data format.
        This method performs validation, normalization, completion, and payload creation.

        Args:
            project_data (dict[str, any]): The initial project data to be processed.

        Returns:
            dict[str, any]: The processed build data ready for project creation.

        Raises:
            ProjectCreationAborted: If the user aborts the project creation process.

        Example:
            >>> get_project_build_data(project_data)
            Processed build data:
            {
                "color_scheme": {"path": "...", "payload": {...}},
                "tags": [{"path": "...", "payload": {...}}, ...],
                "project_settings": {"path": "...", "payload": {...}},
                "database_configs": [{"path": "...", "payload": {...}}, ...],
                "database_registry_locks": [{"path": "...", "payload": {...}}, ...],
                "abbreviations": {"path": "...", "payload": {...}},
                "suggestions": {"path": "...", "payload": {...}},
                "wrong_suggestions": {"path": "...", "payload": {...}},
                "search_normalization": {"path": "...", "payload": {...}}
            }
        """
        self._project_data = project_data
        self._validate_initial()
        self._fix_validation_errors()
        self._normalize()
        self._complete()
        self._create_build_data()
        return self._create_build_data()

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

        if not self._project_data.get("tag_groups", {}):
            self._errors.append(ProjectDataError.EMPTY_TAG_GROUPS)
        # check for duplicate project name
        if self._controller.does_project_exist(self._project_data.get("project_name", None)):
            self._errors.append(ProjectDataError.DUPLICATE_PROJECT_NAME)

    def _fix_validation_errors(self) -> None:
        """
        Handles any validation errors found during the initial validation phase.
        This method will repeatedly prompt the controller to handle errors until
        there are no more errors left to address.
        """
        for error in self._errors:
            self._controller.handle_project_data_error(error)

    def _normalize(self) -> None:
        """
        Normalizes the project data by ensuring unique tag names and valid tag group references.

        Raises:
            ProjectCreationAborted: If the user aborts the project creation process.

        Note:
            This step modifies self._project_data in place to ensure consistency.
        """
        self._ensure_unique_tag_names()
        self._normalize_tag_groups()

    def _complete(self) -> None:
        """
        Completes the project data by collecting additional information and creating payloads.
        Note:
            This step modifies self._project_data in place by adding necessary data.
        """
        self._collect_additional_data()
        self._create_payloads()

    # Detailed steps
    # Normalization

    def _ensure_unique_tag_names(self) -> None:
        """
        Ensures that all tag names in the provided list are unique by appending a counter to duplicate names.
        This method modifies self._project_data in place by updating tag names to ensure uniqueness.

        Raises:
            ProjectCreationAborted: If the user aborts the project creation process.
        """
        tags = self._project_data.get("selected_tags", [])
        for tag in tags:
            # store original name to find data configs later
            tag.setdefault("original_name", tag.get("name", "unknown"))
            tag.setdefault("original_id_prefix",
                           tag.get("id_prefix", "unknown"))
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
                if renamed_duplicate_tags is None:
                    raise ProjectCreationAborted(
                        "User aborted duplicate tag renaming.")
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
        Note:
            This step modifies self._project_data in place by updating tag group references.
        """
        tags = self._project_data.get("selected_tags", [])
        tag_groups = self._project_data.get("tag_groups", {})
        self._project_data["tag_groups"] = {group_name: [tag["name"] for tag in tags if tag["display_name"]
                                                         in tag_display_names] for group_name, tag_display_names in tag_groups.items()}
        self._project_data["tag_group_file_name"] = self._derive_file_name(self._project_data.get(
            "tag_group_file_name", "groups01.json"))

    # Additional data collection
    def _collect_additional_data(self) -> None:
        """
        Collects additional data required for processing.
        This method adds necessary database information to each tag that requires a database.
        Note:
            This step modifies self._project_data in place by adding database info to relevant tags.
        """
        self._add_database_info_to_tags()

    def _add_database_info_to_tags(self) -> None:
        """
        Adds database information to each tag that requires a database.
        This method retrieves the necessary database configuration from the source project.
        Note:
            This step modifies self._project_data in place by adding database info to relevant tags.
        Raises:
            ValueError: If required database information is missing for any tag.
        """
        for tag in self._project_data.get("selected_tags", []):
            # collect needed database
            if not tag.get("has_database", False):
                continue

            tag_name = tag.get("name", "")
            default_file = self._derive_file_name(tag_name)
            database_info = {
                "current_config_file": default_file,
                "config_files": [
                    default_file
                ],
                "registry_lock": default_file
            }
            tag_source_project = tag.get("project", "")
            original_name = tag.get("original_name", tag_name)
            with self._file_handler.use_project(tag_source_project):
                project_settings = self._file_handler.read_file(
                    "project_settings")
                source_registry_lock_name = project_settings.get(
                    "tags", {}).get(tag_name, {}).get(original_name, {}).get("database", {}).get("registry_lock", self._derive_file_name(original_name))
                source_registry_lock = self._file_handler.read_file("project_database_registry_locks_directory",
                                                                    source_registry_lock_name)
                source_registry = source_registry_lock.get(
                    "source_registry", "")
                source = source_registry_lock.get("source", "")
            if not source_registry or not source:
                raise ValueError(
                    f"Missing source_registry or source for tag {tag_name} in project {tag_source_project}")

            tag["database"] = database_info
            tag["source_registry"] = source_registry
            tag["source"] = source

    # Payloads
    def _create_payloads(self) -> None:
        """
        Creates various payloads required for the project based on the provided project data.
        This method generates payloads for color schemes, tag definitions, database configurations,
        project settings, database registry locks, auxiliary databases, and search normalization rules.
        Note:
            This step modifies self._project_data in place by adding the generated payloads.
        """
        self._create_default_color_scheme_payload()
        self._create_tag_definition_payloads()
        self._create_database_config_payloads()
        self._create_project_settings_payload()
        self._create_database_registry_locks_payload()
        self._create_auxdb_payload()
        self._create_search_normalization_payload()

    def _create_default_color_scheme_payload(self) -> None:
        """
        Creates a default color scheme for the project based on the selected tags.
        This method generates a color scheme using the color manager and adds it to the project data.
        Note:
            This step modifies self._project_data in place by adding the color scheme data.
        """
        tag_keys = [tag["name"]
                    for tag in self._project_data.get("selected_tags", [])]
        colorset_name = "magma"
        complementary_search_color = True
        color_scheme_data = self._controller.perform_create_color_scheme(
            tag_keys=tag_keys,
            colorset_name=colorset_name,
            complementary_search_color=complementary_search_color,
            should_write_file=False
        )
        self._project_data["color_scheme_data"] = color_scheme_data

    def _create_tag_definition_payloads(self) -> None:
        """
        Creates tag payloads for each selected tag in the project data.
        This method constructs a payload for each tag based on its source definition
        and adds it to the project data.
        """
        tag_payloads = {}
        for tag in self._project_data.get("selected_tags", []):
            source_path = tag.get("path", "")
            source_definition = self._file_handler.read_file(source_path)
            tag_definition = {
                "type": tag.get("name", "UNKNOWN"),
                "has_database": source_definition.get("has_database", False),
                "id_prefix": tag.get("id_prefix", ""),
                "attributes": source_definition.get("attributes", [])
            }
            tag_payloads[self._derive_file_name(
                tag.get('name', ''))] = tag_definition
        self._project_data["tag_payloads"] = tag_payloads

    def _create_database_config_payloads(self) -> None:
        database_config_payloads = {}
        for tag in self._project_data.get("selected_tags", []):
            if not tag.get("has_database", False):
                continue

            source_tag_name = tag.get("original_name", tag.get("name", ""))
            source_project = tag.get("project", "")
            with self._file_handler.use_project(source_project):
                project_settings = self._file_handler.read_file(
                    "project_settings")
                source_database_config_file = project_settings.get(
                    "tags", {}).get(source_tag_name, {}).get("database", {}).get("current_config_file", self._derive_file_name(source_tag_name))
                database_config = self._file_handler.read_file(
                    "project_database_config_directory", source_database_config_file)
                database_config_payloads[self._derive_file_name(
                    tag.get('name', ''))] = database_config
        self._project_data["database_config_payloads"] = database_config_payloads

    def _create_project_settings_payload(self) -> None:
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
        settings["tags"] = {tag["name"]: {"file_name": self._derive_file_name(tag["name"]), "database": tag.get(
            "database", {})} for tag in self._project_data.get("selected_tags", [])}
        settings["current_group_file"] = self._project_data.get(
            "tag_group_file_name", "")
        settings["group_files"] = [
            self._project_data.get("tag_group_file_name", "groups01.json")]

        # other settings with defaults
        settings["search_normalization"] = default_settings.get(
            "default_search_normalization", "search_normalization_rules.json")
        settings["color_scheme"] = self._project_data.get("color_scheme_data", {}).get(
            "file_name", "default_color_scheme.json")
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

    def _create_database_registry_locks_payload(self) -> None:
        """
        Creates database registry lock information for tags that require a database.
        This method constructs a registry lock dictionary for each tag that has a database
        and adds it to the tag data.
        """
        registry_locks = {}
        for tag in self._project_data.get("selected_tags", []):
            if not tag.get("has_database", False):
                continue
            tag_name = tag.get("name", "")
            name_lower = tag_name.lower().replace(" ", "_")
            registry_lock = {
                "name": tag_name,
                "database_registry": name_lower,
                "source_registry": tag["source_registry"],
                "source": tag["source"],
                "current_db": "",
                "dbs": [],
                "current_config_file": self._derive_file_name(tag_name),
                "config_files": [
                    self._derive_file_name(tag_name)
                ],
                "count": 0
            }
            registry_locks[self._derive_file_name(tag_name)] = registry_lock
        self._project_data["database_registry_locks"] = registry_locks

    def _create_auxdb_payload(self) -> None:
        """
        Creates auxiliary database data for the project.
        This method constructs an auxiliary database dictionary that includes suggestions,
        wrong suggestions, and abbreviations, and adds it to the project data.

        Example:
            >>> create_auxdb_payload()
            Auxiliary database payload created:
            {
                "suggestions": {"TAG1": {}, "TAG2": {}},
                "wrong_suggestions": {"TAG1": [], "TAG2": []},
                "abbreviations": {...}
            }
        """
        project = self._project_data.get("project_name", "unknown_project")
        with self._file_handler.use_project(project):
            abbreviations = self._file_handler.read_file(
                "abbreviations_defaults")
        auxdb_data = {
            "suggestions": {tag["name"]: {} for tag in self._project_data.get("selected_tags", [])},
            "wrong_suggestions": {tag["name"]: [] for tag in self._project_data.get("selected_tags", [])},
            "abbreviations": abbreviations
        }
        self._project_data["auxdb_data"] = auxdb_data

    def _create_search_normalization_payload(self) -> None:
        """
        Creates search normalization rules payload for the project.
        This method constructs a search normalization rules dictionary and adds it to the project data.
        """
        default_rules = self._file_handler.read_file(
            "search_normalization_rules_defaults")
        self._project_data["search_normalization_rules"] = default_rules

    # Build data

    def _create_build_data(self) -> dict[str, any]:
        """
        Creates build data for the project based on the provided project data.
        This method constructs a build data dictionary that includes paths and payloads
        for color schemes, tags, database configurations, project settings, database registry locks,
        auxiliary databases, and search normalization rules.
        Returns:
            dict: A dictionary containing the build data for the project.
        Example:
            >>> create_build_data()
            Build data created:
            {
                "color_scheme": {"path": "...", "payload": {...}},
                "tags": [{"path": "...", "payload": {...}}, ...],
                "project_settings": {"path": "...", "payload": {...}},
                "database_configs": [{"path": "...", "payload": {...}}, ...],
                "database_registry_locks": [{"path": "...", "payload": {...}}, ...],
                "abbreviations": {"path": "...", "payload": {...}},
                "suggestions": {"path": "...", "payload": {...}},
                "wrong_suggestions": {"path": "...", "payload": {...}},
                "search_normalization": {"path": "...", "payload": {...}}
            }
        """
        build_data = {}
        # color scheme
        with self._file_handler.use_project(self._project_data.get("project_name", "unknown_project")):
            color_scheme_data = self._project_data.get("color_scheme_data", {})
            color_scheme_filename = color_scheme_data.get(
                "file_name", "default_color_scheme.json")
            color_scheme_path = self._file_handler.resolve_path(
                "project_color_scheme_directory", color_scheme_filename)
            build_data["color_scheme"] = {
                "path": color_scheme_path,
                "payload": color_scheme_data.get("color_scheme", {})
            }

        # tags
            tag_build_data = []
            for filename, tag_payload in self._project_data.get("tag_payloads", {}).items():
                tag_path = self._file_handler.resolve_path(
                    "project_tags_directory", filename)
                tag_build_data.append({
                    "path": tag_path,
                    "payload": tag_payload
                })
            build_data["tags"] = tag_build_data

        # tag groups
            tag_groups_payload = self._project_data.get("tag_groups", {})
            tag_group_file_name = self._project_data.get(
                "tag_group_file_name", "groups01.json")
            tag_groups_path = self._file_handler.resolve_path(
                "project_tag_groups_directory", tag_group_file_name)
            tag_groups_build_data = {
                "path": tag_groups_path,
                "payload": tag_groups_payload
            }
            build_data["tag_groups"] = tag_groups_build_data
        # db config
            db_config_build_data = []
            for filename, db_config in self._project_data.get("database_config_payloads", {}).items():
                db_config_path = self._file_handler.resolve_path(
                    "project_database_config_directory", filename)
                db_config_build_data.append({
                    "path": db_config_path,
                    "payload": db_config
                })
            build_data["database_configs"] = db_config_build_data
        # project settings
            project_settings_payload = self._project_data.get("settings", {})
            project_settings_path = self._file_handler.resolve_path(
                "project_settings")
            project_settings_build_data = {
                "path": project_settings_path,
                "payload": project_settings_payload
            }
            build_data["project_settings"] = project_settings_build_data
        # db registry locks
            db_registry_locks_build_data = []
            for filename, registry_lock in self._project_data.get("database_registry_locks", {}).items():
                registry_lock_path = self._file_handler.resolve_path(
                    "project_database_registry_locks_directory", filename)
                db_registry_locks_build_data.append({
                    "path": registry_lock_path,
                    "payload": registry_lock
                })
            build_data["database_registry_locks"] = db_registry_locks_build_data
        # abbreviations, suggestions, wrong suggestions
            # paths
            abbreviations_path = self._file_handler.resolve_path(
                "project_abbreviations")
            suggestions_path = self._file_handler.resolve_path(
                "project_suggestions")
            wrong_suggestions_path = self._file_handler.resolve_path(
                "project_wrong_suggestions")
            # unpack payloads
            auxdb_payload = self._project_data.get("auxdb_data", {})
            abbreviations_payload = auxdb_payload.get("abbreviations", {})
            suggestions_payload = auxdb_payload.get("suggestions", {})
            wrong_suggestions_payload = auxdb_payload.get(
                "wrong_suggestions", {})
            # build data
            build_data["abbreviations"] = {
                "path": abbreviations_path,
                "payload": abbreviations_payload
            }

            build_data["suggestions"] = {
                "path": suggestions_path,
                "payload": suggestions_payload
            }

            build_data["wrong_suggestions"] = {
                "path": wrong_suggestions_path,
                "payload": wrong_suggestions_payload
            }

            # search normalization rules
            search_normalization_rules_path = self._file_handler.resolve_path(
                "project_search_normalization_rules")

            build_data["search_normalization_rules"] = {
                "path": search_normalization_rules_path,
                "payload": self._project_data.get("search_normalization_rules", {})
            }

        return build_data

    def _derive_file_name(self, tag_name: str) -> str:
        """
        Derives a file name from the given tag name by converting it to lowercase,
        replacing spaces with underscores, and appending a .json extension.
        Args:
            tag_name (str): The name of the tag.
        Returns:
            str: The derived file name.
        Example:
            >>> derive_file_name("Example Tag")
            "example_tag.json"
        """
        filename = tag_name.lower().replace(" ", "_")
        if not filename.endswith(".json"):
            filename += ".json"
        return filename
