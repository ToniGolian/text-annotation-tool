from typing import List, Optional

from commands.interfaces import ICommand


class UndoRedoModel:
    """
    Model that maintains an undo and redo stack for a certain view.
    """

    def __init__(self) -> None:
        """
        Initializes the UndoRedoModel with empty undo and redo stacks.
        """
        self.undo_stack: List[ICommand] = []
        self.redo_stack: List[ICommand] = []

    def execute_command(self, command: ICommand) -> None:
        """
        Executes a command by adding it to the undo stack and clearing the redo stack.

        Args:
            command (ICommand): The command object to execute.
        """
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo_command(self) -> Optional[ICommand]:
        """
        Performs an undo operation by popping the last command from the undo stack,
        adding it to the redo stack, and returning it.

        Returns:
            Optional[ICommand]: The command that was undone, or None if the undo stack is empty.
        """
        if self.undo_stack:
            command = self.undo_stack.pop()
            self.redo_stack.append(command)
            return command
        return None

    def redo_command(self) -> Optional[ICommand]:
        """
        Performs a redo operation by popping the last command from the redo stack,
        adding it to the undo stack, and returning it.

        Returns:
            Optional[ICommand]: The command that was redone, or None if the redo stack is empty.
        """
        if self.redo_stack:
            command = self.redo_stack.pop()
            self.undo_stack.append(command)
            return command
        return None

    def reset(self) -> None:
        """
        Clears both the undo and redo stacks.

        This method resets the state by removing all stored undo and redo actions, 
        effectively discarding any command history.

        Returns:
            None
        """
        self.undo_stack.clear()
        self.redo_stack.clear()
