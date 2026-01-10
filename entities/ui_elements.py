from .static_objects import GameObject
import pygame
import helpers


class Text:
    """
    Klasa reprezentująca element tekstowy w grze.

    Odpowiada za renderowanie tekstu, obsługę czcionek, kolorów
    oraz pozycjonowanie względem ekranu lub innego obiektu (np. przycisku).

    Attributes:
        _surface (pygame.Vector2 | pygame.Rect): Powierzchnia lub rozmiar
                                                 odniesienia do pozycjonowania.
        _name (str): Nazwa elementu (ID).
        _text (str): Aktualnie wyświetlany tekst.
        _initial_text (str): Tekst początkowy.
        _text_color (tuple): Kolor tekstu (R, G, B).
        _font (pygame.font.Font): Obiekt czcionki.
        _text_surface (pygame.Surface): Wyrenderowany obraz tekstu.
        _text_rect (pygame.Rect): Prostokąt otaczający tekst.
    """
    def __init__(self, data: dict,
                 surface: pygame.Vector2 | pygame.Rect):
        """
        Inicjalizuje obiekt tekstowy.

        Args:
            data (dict): Słownik konfiguracyjny.
            surface (pygame.Vector2 | pygame.Rect): Wymiary ekranu (Vector2)
                                    lub prostokąt rodzica (Rect),
                                    względem którego tekst ma być wyśrodkowany.
        """
        self._surface = surface
        self._name = data.get('name', '')

        text = str(data.get('text', ''))
        self._initial_text = text
        self._text = text

        text_color_R = data.get('text_color_R', 0)
        text_color_G = data.get('text_color_G', 0)
        text_color_B = data.get('text_color_B', 0)
        self._text_color = (text_color_R, text_color_G, text_color_B)

        self._font_path = data.get('font_path', '')
        self._font_size = data.get('font_size', 10)

        self._font_size = int(self._font_size)

        self._font = helpers.initialize_font(self._font_path,
                                             self._font_size)

        self._anchor = data.get('anchor', 'center')

        self._x_offset = data.get('x_offset', 0)
        self._y_offset = data.get('y_offset', 0)
        self._update_render()

    def name(self) -> str:
        """Zwraca nazwę elementu."""
        return self._name

    def get_text(self) -> str:
        """Zwraca aktualną treść tekstu."""
        return self._text

    def get_text_color(self) -> tuple:
        """Zwraca kolor tekstu."""
        return tuple(self._text_color)

    def get_initial_text(self) -> str:
        """Zwraca tekst początkowy (szablon)."""
        return self._initial_text

    def get_font_size(self) -> int:
        """Zwraca rozmiar czcionki."""
        return self._font_size

    def _update_render(self) -> None:
        """
        Renderuje powierzchnię tekstu i aktualizuje jego pozycję.

        Wywoływana automatycznie przy zmianie tekstu, koloru lub czcionki.
        """
        try:
            self._text_surface = self._font.render(self._text, True,
                                                   self._text_color)
        except ValueError:
            self._text_color = (0, 0, 0)
            self._text_surface = self._font.render(self._text, True,
                                                   self._text_color)

        self._text_rect = self._text_surface.get_rect()
        self._update_position()

    def _update_position(self) -> None:
        """Oblicza pozycję tekstu na podstawie kotwicy (anchor) i offsetu."""
        if isinstance(self._surface, pygame.Rect):
            self._pos = pygame.Vector2(self._surface.center)
        else:
            position = helpers.base_pos_on_anchor(self._anchor, self._surface)
            self._pos = pygame.Vector2(position)
        self._pos += pygame.Vector2(self._x_offset, self._y_offset)

        try:
            setattr(self._text_rect, self._anchor, self._pos)
        except AttributeError:
            setattr(self._text_rect, 'center', self._pos)

    def set_text(self, new_text: str = '') -> None:
        """
        Ustawia nową treść tekstu i przerysowuje go.

        Args:
            new_text (str): Nowy tekst.
        """
        if new_text == '':
            return

        self._text = new_text
        self._update_render()

    def set_text_color(self, new_color: tuple):
        """
        Ustawia nowy kolor tekstu. W przypadku podania
        niepoprawnych danych ustawia kolor na czarny.

        Args:
            new_color (tuple): Krotka (R, G, B).
        """
        try:
            r = min(255, max(0, new_color[0]))
            g = min(255, max(0, new_color[1]))
            b = min(255, max(0, new_color[2]))

            self._text_color = (r, g, b)
        except ValueError:
            self._text_color = (0, 0, 0)
        self._update_render()

    def set_font_size(self, new_size: int) -> None:
        """Zmienia rozmiar czcionki."""
        if isinstance(new_size, (int, float)):
            self._font_size = max(1, new_size)

            self._font = helpers.initialize_font(self._font_path,
                                                 self._font_size)
            self._update_render()

    def draw(self, screen):
        """Rysuje tekst na ekranie."""
        if self._text_surface is not None:
            screen.blit(self._text_surface, self._text_rect)


class Button(GameObject):
    """
    Klasa reprezentująca interaktywny przycisk.

    Dziedziczy po GameObject (grafika, pozycja).
    Dodaje obsługę kliknięć myszą.

    Attributes:
        _pos (pygame.Vector2): Pozycja środka przycisku.
        _text (Text): tekst wyświetlany na przycisku.
    """

    def __init__(self, object_data: dict, screen_size: pygame.Vector2):
        """
        Inicjalizuje przycisk.

        Oblicza jego pozycję na podstawie kotwicy (anchor) względem ekranu.

        Args:
            object_data (dict): Słownik z konfiguracją.
            screen_size (pygame.Vector2): Rozmiar ekranu.
        """
        anchor = object_data.get('anchor', 'center')  # Domyślnie środek
        off_x = object_data.get('x_offset', 0)
        off_y = object_data.get('y_offset', 0)

        # Obliczamy punkt bazowy na podstawie kotwicy

        self._pos = pygame.Vector2(helpers.base_pos_on_anchor(anchor,
                                                              screen_size))
        self._pos += pygame.Vector2(off_x, off_y)
        super().__init__(object_data)

    def size(self) -> tuple:
        """Zwraca rozmiar przycisku (szer, wys)."""
        return self._object_rect.size

    def rect(self) -> pygame.Rect:
        """Zwraca prostokąt kolizji przycisku."""
        return self._object_rect

    def is_clicked(self, events: list) -> bool:
        """
        Sprawdza, czy przycisk został kliknięty w bieżącej klatce.

        Args:
            events (list): Lista zdarzeń Pygame.

        Returns:
            bool: True, jeśli nastąpiło kliknięcie LPM na przycisku.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    m_collision = self._object_rect.collidepoint(event.pos)
                    if m_collision:
                        return True
        return False


class TextButton(Button):
    """
    Przycisk z napisem w środku.

    Rozszerza klasę Button o obiekt Text wyśrodkowany względem przycisku.
    """
    def __init__(self, object_data: dict, screen_size: pygame.Vector2):
        """
        Inicjalizuje przycisk z tekstem.

        Args:
            object_data (dict): Słownik konfiguracyjny.
            screen_size (pygame.Vector2): Rozmiar ekranu.
        """
        super().__init__(object_data, screen_size)
        # To zabezpiecza przed pustą listą [], która prześlizgnęła się przez
        # initialize_buttons
        texts_list = object_data.get('texts', [])
        if texts_list and len(texts_list) > 0:
            text_data = texts_list[0]
        else:
            # Awaryjny tekst, żeby gra nie padła
            text_data = {'text': 'Error', 'font_size': 35}

        self._text = Text(text_data, self._object_rect)

    def draw(self, screen):
        """Wyświetla tekst na guziku."""
        super().draw(screen)
        self._text.draw(screen)
