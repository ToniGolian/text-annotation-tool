class TagDeletionProhibitedError(Exception):
    """Raised when an attempt is made to delete a referenced tag."""
    pass
