from .base_state import State
import json
import pygame


class MainMenuState(State):
    """
    Stan gry reprezentujący menu główne.
    Zarządza interakcją z użytkownikiem przed rozpoczęciem rozgrywki.

    Posiada trzy przyciski, które obsługuje:
    - wciśnięcie przycisku 'play' uruchamia pierwszy poziom gry
    - wciśnięcie przycisku 'options' przełącza tryb wyświetlania
        między oknem a pełnym ekranem (Fullscreen).
    - wciśnięcie przycisku 'quit' zamyka program

    Attributes:
        _play_button (TextButton) - Przycisk uruchamiający grę.
        _options_button (TextButton) - Przycisk przełączający
                                       tryb wyświetlania okna.
        _quit_button (TextButton) - Przycisk wyłączający grę.
    """
    def __init__(self, screen_size: pygame.Vector2):
        """
        Inicjalizuje obiekt klasy MainMenuState.
        Otwiera plik konfiguracyjny json, z którego dane
        przekazuje do konstruktora klasy bazowej.
        Pobiera z pliku konfiguracyjnego ścieżkę do tła.
        Wywołuje metody tworzące przyciski i ustawiające tło.

        Args:
            screen_size (pygame.Vector2): Rozmiar okna gry.
        """
        with open('objects_config_files/menu.json') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()
            background_img_path = data["background_img"]
            self._set_background(background_img_path)

    def _create_buttons(self) -> None:
        """
        Przypisuje przyciski z utworzonego w konstruktorze słownika
        do zmiennych.
        """
        self._play_button = self._buttons_dict['play_menu_button']
        self._options_button = self._buttons_dict['options_menu_button']
        self._quit_button = self._buttons_dict['quit_menu_button']

    def update(self, events: list) -> str:
        """
        Wykrywa naciśnięcia przycisków, oraz zwraca adekwatne do nich
        komendy sterujące w postaci stringa.

        Args:
            events (list): Lista wydarzeń wykrywanych przez bibliotekę pygame.

        Returns:
            str: Komenda sterująca (np 'START_GAME', 'STAY')
        """
        next_state = 'STAY'

        if self._play_button.is_clicked(events):
            next_state = 'START_GAME'

        elif self._options_button.is_clicked(events):
            new_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11)
            pygame.event.post(new_event)

        elif self._quit_button.is_clicked(events):
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)

        return next_state

    def draw(self, screen: pygame.Surface) -> None:
        """
        Wywołuje metodę rysującą klasy bazowej.

        Args:
            screen (pygame.Surface): Powierzchnia, na której
                                     rysowany jest stan.
        """
        super().draw(screen)
