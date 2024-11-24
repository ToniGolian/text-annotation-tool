class MockAddTagCommand:
    def __init__(self, tag_manager, tag_data: dict):
        self._tag_manager = tag_manager
        self._tag_data = tag_data

    def execute(self) -> None:
        """
        Simulates executing the add tag command.
        """
        print(f"Executing AddTagCommand with data: {self._tag_data}")
        self._tag_manager.add_tag(self._tag_data)

    def undo(self) -> None:
        """
        Simulates undoing the add tag command.
        """
        print(f"Undoing AddTagCommand with data: {self._tag_data}")
        self._tag_manager.delete_tag(self._tag_data.get("id"))

    def redo(self) -> None:
        """
        Simulates redoing the add tag command.
        """
        print(f"Redoing AddTagCommand with data: {self._tag_data}")
        self._tag_manager.add_tag(self._tag_data)


class MockEditTagCommand:
    def __init__(self, tag_manager, tag_id: str, tag_data: dict):
        self._tag_manager = tag_manager
        self._tag_id = tag_id
        self._tag_data = tag_data

    def execute(self) -> None:
        """
        Simulates executing the edit tag command.
        """
        print(
            f"Executing EditTagCommand for ID: {self._tag_id} with data: {self._tag_data}")
        self._tag_manager.edit_tag(self._tag_id, self._tag_data)

    def undo(self) -> None:
        """
        Simulates undoing the edit tag command.
        """
        print(f"Undoing EditTagCommand for ID: {self._tag_id}")
        # No actual undo logic for mock; replace with real logic if needed.

    def redo(self) -> None:
        """
        Simulates redoing the edit tag command.
        """
        print(
            f"Redoing EditTagCommand for ID: {self._tag_id} with data: {self._tag_data}")
        self._tag_manager.edit_tag(self._tag_id, self._tag_data)


class MockDeleteTagCommand:
    def __init__(self, tag_manager, tag_id: str):
        self._tag_manager = tag_manager
        self._tag_id = tag_id

    def execute(self) -> None:
        """
        Simulates executing the delete tag command.
        """
        print(f"Executing DeleteTagCommand for ID: {self._tag_id}")
        self._tag_manager.delete_tag(self._tag_id)

    def undo(self) -> None:
        """
        Simulates undoing the delete tag command.
        """
        print(f"Undoing DeleteTagCommand for ID: {self._tag_id}")
        # No actual undo logic for mock; replace with real logic if needed.

    def redo(self) -> None:
        """
        Simulates redoing the delete tag command.
        """
        print(f"Redoing DeleteTagCommand for ID: {self._tag_id}")
        self._tag_manager.delete_tag(self._tag_id)
