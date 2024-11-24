from utils.interfaces import ILayoutPublisher
from config.template_manager import TemplateManager
from typing import List, Dict


class ConfigurationManager(ILayoutPublisher):
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
        self._meta_tag_names: List[str] = []
        self._template_groups: List[Dict[str, List[Dict]]] = []
        self._template_manager = TemplateManager()

    def get_meta_tag_names(self) -> List[str]:
        """
        Retrieves the list of meta tag names.

        Returns:
            List[str]: The list of meta tag names.
        """
        return self._meta_tag_names

    def set_meta_tag_names(self, names: List[str]) -> None:
        """
        Sets the list of meta tag names.

        Args:
            names (List[str]): The new list of meta tag names to set.
        """
        self._meta_tag_names = names

    def get_template_groups(self) -> List[Dict[str, List[Dict]]]:
        """
        Retrieves the list of template groups.

        Returns:
            List[Dict[str, List[Dict]]]: The list of template groups.
        """
        return self._template_groups

    def set_template_groups(self, groups: List[Dict[str, List[Dict]]]) -> None:
        """
        Sets the list of template groups.

        Args:
            groups (List[Dict[str, List[Dict]]]): The new list of template groups to set.
        """
        self._template_groups = groups

    def _add_template_group(self, group_name: str, templates: List[Dict]) -> None:
        """
        Adds a new template group to the template_groups list.

        Args:
            group_name (str): The name of the new template group.
            templates (List[Dict]): The list of templates for this group.
        """
        new_group = {"group_name": group_name, "templates": templates}
        self._template_groups.append(new_group)

    def _remove_template_group(self, group_name: str) -> None:
        """
        Removes a template group from the template_groups list by its group name.

        Args:
            group_name (str): The name of the template group to remove.
        """
        self._template_groups = [
            group for group in self._template_groups if group["group_name"] != group_name]

    def _update_template_group(self, group_name: str, templates: List[Dict]) -> None:
        """
        Updates an existing template group with a new list of templates.

        Args:
            group_name (str): The name of the template group to update.
            templates (List[Dict]): The updated list of templates for this group.
        """
        for group in self._template_groups:
            if group["group_name"] == group_name:
                group["templates"] = templates
                break

    def _reload_templates(self) -> None:
        """
        Reloads templates using the TemplateManager's reload method.
        """
        self._template_manager.reload_templates()

    def _fetch_templates(self, template_name: str) -> List[Dict]:
        """
        Fetches a list of templates by a given name using the TemplateManager.

        Args:
            template_name (str): The name of the template to fetch.

        Returns:
            List[Dict]: A list of template dictionaries fetched by name.
        """
        # todo getter for all templates
        return self._template_manager.get_templates(template_name)


# TODO'


def get_layout_state(self) -> Dict:
    """Retrieves the layout state of the publisher."""
    pass
