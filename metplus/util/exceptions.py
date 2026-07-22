class MPWarningError(Exception):
    """Raised when a warning is encountered and EXIT_ON_WARN is True"""

    def __init__(self):
        # Pass a clear error message to the base Exception class
        super().__init__(
            "Encountered a warning when EXIT_ON_WARN is set."
            " Ending METplus run now."
        )
