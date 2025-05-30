class AnnotationModeModel:
    """
    Manages the current annotation mode and supports temporary suspension of automatic mode.

    This model tracks whether the annotation system is in 'manual' or 'auto' mode, and allows 
    auto mode to be temporarily paused and resumed. It also keeps track of whether the pause 
    was explicitly triggered to ensure correct reactivation behavior.
    """

    def __init__(self):
        # Current mode: 'manual' or 'auto'
        self._mode = "manual"
        # Internal flag to indicate whether auto mode is paused
        self._auto_paused = False
        # Flag to remember if pause was explicitly requested
        self._pause_requested = False

    def set_manual_mode(self) -> None:
        """Switches the mode to manual and clears pause state."""
        self._mode = "manual"
        self._auto_paused = False
        self._pause_requested = False

    def set_auto_mode(self) -> None:
        """Switches the mode to auto and clears pause state."""
        self._mode = "auto"
        self._auto_paused = False
        self._pause_requested = False

    def get_mode(self) -> str:
        """Returns the current annotation mode ('manual' or 'auto')."""
        return self._mode

    def is_manual_mode(self) -> bool:
        """Returns True if the current mode is manual."""
        return self._mode == "manual"

    def is_auto_mode(self) -> bool:
        """Returns True if the current mode is auto and not paused."""
        return self._mode == "auto" and not self._auto_paused

    def pause_auto_mode(self) -> None:
        """
        Pauses auto mode, if currently active.

        This sets a flag to indicate that auto mode is temporarily suspended.
        """
        if self._mode == "auto":
            self._auto_paused = True
            self._pause_requested = True

    def resume_auto_mode(self) -> None:
        """
        Resumes auto mode only if it was previously paused.

        If auto mode was not paused explicitly, this method has no effect.
        """
        if self._mode == "auto" and self._pause_requested:
            self._auto_paused = False
            self._pause_requested = False

    def is_auto_paused(self) -> bool:
        """Returns True if auto mode is currently paused."""
        return self._auto_paused

    def was_pause_requested(self) -> bool:
        """Returns True if pause_auto_mode was explicitly called."""
        return self._pause_requested
