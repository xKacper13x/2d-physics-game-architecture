import pytest
import pygame
import helpers
import exceptions

# --- Testy dla check_size (czysta logika) ---


def test_check_size_correct():
    """Sprawdza czy funkcja akceptuje poprawne dane."""
    helpers.check_size(100)
    helpers.check_size((800, 600))
    helpers.check_size(pygame.Vector2(50, 50))
    # Brak błędu oznacza sukces


def test_check_size_errors():
    """Sprawdza czy funkcja rzuca błędy dla złych danych."""
    # Zero
    with pytest.raises(exceptions.InvalidConfigurationError):
        helpers.check_size(0)

    # Ujemne
    with pytest.raises(exceptions.InvalidConfigurationError):
        helpers.check_size(-10)

    # Krotka z zerem
    with pytest.raises(exceptions.InvalidConfigurationError):
        helpers.check_size((100, 0))

# --- Testy dla check_path (na prawdziwych plikach tymczasowych) ---


def test_check_path_existing_file(tmp_path):
    """
    tmp_path to funkcja pytesta, która tworzy prawdziwy folder tymczasowy.
    """
    # 1. Tworzymy prawdziwy plik w folderze tymczasowym
    real_file = tmp_path / "testowy_plik.txt"
    real_file.write_text("witaj")

    # 2. Przekazujemy ścieżkę jako string
    path_str = str(real_file)

    # 3. To powinno przejść bez błędu, bo plik fizycznie istnieje
    helpers.check_path(path_str)


def test_check_path_missing_file():
    """Sprawdza reakcję na brak pliku."""
    with pytest.raises(exceptions.MissingResourceError):
        helpers.check_path("ten_plik_nie_istnieje_123.png")


def test_check_path_none():
    """Sprawdza reakcję na None."""
    with pytest.raises(exceptions.MissingResourceError):
        helpers.check_path(None)

# --- Testy dla create_placeholder ---


def test_create_placeholder_returns_surface():
    """Sprawdza czy funkcja zwraca obiekt pygame.Surface."""
    result = helpers.create_placeholder((30, 40))

    assert isinstance(result, pygame.Surface)
    assert result.get_width() == 30
    assert result.get_height() == 40

    # Sprawdź kolor (czy jest różowy - R=255, G=0, B=255)
    color = result.get_at((0, 0))
    assert color == (255, 0, 255, 255)

# --- Testy dla base_pos_on_anchor ---


def test_base_pos_calculation():
    """Sprawdza matematykę obliczania pozycji."""
    screen = (800, 600)

    # Sprawdzamy środek
    assert helpers.base_pos_on_anchor('center', screen) == (400, 300)

    # Sprawdzamy narożnik
    assert helpers.base_pos_on_anchor('topright', screen) == (800, 0)

# --- Testy integracyjne load_image (bez mocków) ---


def test_load_image_missing_file_returns_placeholder():
    """
    Sprawdza, czy próba załadowania nieistniejącego pliku
    zwraca różowy kwadrat zamiast wywalić program.
    """
    # Próbujemy załadować plik, którego nie ma
    result = helpers.load_image("nieistniejacy_obrazek.png", img_size=(20, 20))

    # Funkcja powinna złapać błąd w środku i zwrócić placeholder
    assert isinstance(result, pygame.Surface)
    # Placeholder powinien mieć zadany rozmiar
    assert result.get_size() == (20, 20)
    # I różowy kolor
    assert result.get_at((0, 0)) == (255, 0, 255, 255)
