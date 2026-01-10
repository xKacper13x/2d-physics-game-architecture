import pygame
from entities import ui_elements


# --- Testy klasy Text ---

def test_text_creation_and_properties():
    """
    Tworzy obiekt Text na prawdziwym silniku Pygame
    (używając domyślnej czcionki).
    """
    # Dane konfiguracyjne
    data = {
        'name': 'TestLabel',
        'text': 'Hello World',
        'font_size': 20,
        'text_color_R': 255,
        'text_color_G': 100,
        'text_color_B': 0,
        'anchor': 'center'
    }
    # Kontener (np. ekran)
    screen_rect = pygame.Rect(0, 0, 800, 600)

    # Tworzymy obiekt (helpers.initialize_font załaduje domyślną
    # czcionkę systemową, gdy path brak)
    text_obj = ui_elements.Text(data, screen_rect)

    # Sprawdzenia
    assert text_obj.name() == 'TestLabel'
    assert text_obj.get_text() == 'Hello World'
    assert text_obj.get_text_color() == (255, 100, 0)

    # Sprawdzamy, czy Pygame faktycznie wyrenderował tekst
    # (powinien powstać obiekt pygame.Surface)
    assert isinstance(text_obj._text_surface, pygame.Surface)
    # Tekst "Hello World" powinien mieć szerokość większą niż 0
    assert text_obj._text_surface.get_width() > 0


def test_text_positioning():
    """Sprawdza, czy tekst centruje się na ekranie."""
    data = {'text': 'X', 'anchor': 'center'}
    screen_rect = pygame.Rect(0, 0, 800, 600)  # Środek to (400, 300)

    text_obj = ui_elements.Text(data, screen_rect)

    # Prostokąt tekstu powinien mieć środek w (400, 300)
    # Uwaga: używamy int(), bo pozycje mogą być float
    assert int(text_obj._text_rect.centerx) == 400
    assert int(text_obj._text_rect.centery) == 300

# --- Testy klasy Button ---


def test_button_position_and_size():
    """
    Testuje tworzenie przycisku.
    Ponieważ nie mamy pliku graficznego, helpers.load_image zwróci
    różowy placeholder 50x50 (lub inny domyślny).
    """
    data = {
        'img_path': 'nieistniejacy_plik.png',
        'width': 100,
        'height': 50,
        'anchor': 'topleft',
        'x_offset': 10,
        'y_offset': 10
    }
    screen_size = pygame.Vector2(800, 600)

    # Tworzymy przycisk
    btn = ui_elements.Button(data, screen_size)

    # Sprawdzamy rozmiar
    assert btn.size() == (100, 50)

    # Sprawdzamy pozycję
    assert btn._object_rect.center == (10, 10)


# --- Testy klasy TextButton ---

def test_text_button_structure():
    """Sprawdza, czy TextButton poprawnie tworzy obiekt Text wewnątrz."""
    data = {
        'img_path': 'dummy.png',
        'texts': [{'text': 'START', 'font_size': 15}],
        'anchor': 'center'
    }
    screen_size = pygame.Vector2(800, 600)

    # To zadziała, bo helpers.load_image obsłuży brak pliku
    # a helpers.initialize_font obsłuży brak czcionki
    txt_btn = ui_elements.TextButton(data, screen_size)

    # Sprawdzamy czy w środku jest obiekt Text
    assert isinstance(txt_btn._text, ui_elements.Text)

    # Sprawdzamy czy tekst się zgadza
    assert txt_btn._text.get_text() == 'START'
