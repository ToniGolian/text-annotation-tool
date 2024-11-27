class TagManager:
    def __init__(self, document_model):
        self.tags = []
        self.text = ""

    def add_tag(self, tag_data: dict) -> None:
        """
        Simulates adding a tag by appending it to the tags list and updating the text.
        """
        self.tags.append(tag_data)
        self.text += f"\n{tag_data}"
        self._print_state("add_tag")

    def edit_tag(self, tag_id: str, tag_data: dict) -> None:
        """
        Simulates editing a tag by updating the corresponding tag in the tags list.
        """
        for tag in self.tags:
            if tag.get("id") == tag_id:
                tag.update(tag_data)
                break
        self._print_state("edit_tag")

    def delete_tag(self, tag_id: str) -> None:
        """
        Simulates deleting a tag by removing it from the tags list.
        """
        self.tags = [tag for tag in self.tags if tag.get("id") != tag_id]
        self._print_state("delete_tag")

    def _print_state(self, method_name: str) -> None:
        """
        Prints the current state of tags and text after a method is executed.
        """
        print(f"Method: {method_name}")
        print(f"Tags: {self.tags}")
        print(f"Text: {self.text.strip()}")
        print("-" * 40)
