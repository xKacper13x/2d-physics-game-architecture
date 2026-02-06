class GameError(Exception):
    """
    The root exception class for the Angry Knights engine.

    Acts as a base for all project-specific errors, allowing for
    centralized error handling and logging across the application.
    """
    pass


class StateError(GameError):
    """Exception generally connected to states."""
    pass


class MissingResourceError(GameError):
    """
    Raised when a critical external asset (image, font, or JSON config)
    is unreachable at the provided path.
    """
    def __init__(self, path):
        self.path = path
        message = f"Couldn't load from path: {self.path}"
        super().__init__(message)


class InvalidConfigurationError(GameError):
    """Raised, when game parameters are incorrect (for example font size)"""
    def __init__(self, message):
        super().__init__(message)
