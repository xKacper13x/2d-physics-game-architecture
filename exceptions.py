class GameError(Exception):
    """Bazowa klasa dla wyjątków w moim projekcie gry."""
    pass


# Konkretne wyjątki dziedziczące po bazowym.

class StateError(GameError):
    """Ogólny błąd związany ze stanami gry."""
    pass


class MissingResourceError(GameError):
    """Rzucany, gdy nie można znaleźć pliku (obrazka, czcionki)."""
    def __init__(self, path):
        self.path = path
        message = f"Nie udało się załadować zasobu ze ścieżki: {self.path}"
        super().__init__(message)


class InvalidConfigurationError(GameError):
    """Rzucany, gdy parametry gry (np. rozmiar czcionki) są nieprawidłowe."""
    def __init__(self, message):
        super().__init__(message)
