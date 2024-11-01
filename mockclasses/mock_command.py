from commands.interfaces import ICommand

class IMockCommand(ICommand):
    def execute(self) -> None:
        """Executes the command's primary action."""
        print("Mockcommand executed")

    def undo(self) -> None:
        """Reverses the actions performed by execute."""
        print("Mockcommand undone")

    def redo(self) -> None:
        """Reapplies the actions undone by undo."""
        print("Mockcommand redone")
