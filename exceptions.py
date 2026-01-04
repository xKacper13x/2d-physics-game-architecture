class GameError(Exception):
    """Bazowa klasa dla wszystkich wyjątków w moim projekcie gry."""
    pass


# Konkretne wyjątki dziedziczące po bazowym.

class StateError(GameError):
    """Ogólny błąd związany ze stanami gry."""
    pass


class MissingResourceError(GameError):
    """Rzucany, gdy nie można znaleźć pliku (obrazka, czcionki)."""
    def __init__(self, path):
        # Możemy dostosować komunikat błędu
        self.path = path
        message = f"Nie udało się załadować zasobu ze ścieżki: {self.path}"
        # Wywołujemy konstruktor klasy nadrzędnej z naszym komunikatem
        super().__init__(message)


class InvalidConfigurationError(GameError):
    """Rzucany, gdy parametry gry (np. rozmiar czcionki) są nieprawidłowe."""
    def __init__(self, message):
        super().__init__(message)

# Chyba nie będę robil zapisu, ale się zobaczy
# class SaveGameCorruptedError(GameError):
#     """Rzucany, gdy plik zapisu jest uszkodzony."""
#     pass
