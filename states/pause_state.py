from .base_state import State
import pygame
import json


class PauseState(State):
    """
    Stan gry reprezentujący menu pauzy.

    Jest to stan nakładkowy (Overlay), co oznacza, że jest wyświetlany
    "na wierzchu" zatrzymanej rozgrywki, nie usuwając jej z pamięci.

    Attributes:
        _paused_state (State): Obiekt stanu gry (GameState), który został
                               zatrzymany i do którego można wrócić.
        _play_button (Button): Przycisk wznawiający grę.
        _retry_button (Button): Przycisk restartujący poziom.
        _quit_button (Button): Przycisk cofający do menu głównego.
    """
    def __init__(self, screen_size: pygame.Vector2, paused_state: State):
        """
        Inicjalizuje menu pauzy.

        Wczytuje konfigurację wizualną z pliku JSON i zapamiętuje stan,
        z którego pauza została wywołana. Wywołuje tworzenie przycisków

        Args:
            screen_size (pygame.Vector2): Wymiary okna gry.
            paused_state (State): Stan gry (GameState), który ma zostać
                                  wznowiony po wyjściu z pauzy.
        """
        self._paused_state = paused_state
        with open('objects_config_files/pause.json') as file_handle:
            data = json.load(file_handle)
            super().__init__(screen_size, data)
            self._create_buttons()

    def get_paused_state(self) -> State:
        """
        Zwraca stan gry, który został zapauzowany.

        Returns:
            State: Zapamiętany obiekt GameState.
        """
        return self._paused_state

    def get_level(self) -> int:
        """
        Zwraca numer poziomu z zapauzowanej gry.

        Returns:
            int: Numer poziomu.
        """
        return self._paused_state.get_level()

    def _create_buttons(self):
        """
        Przypisuje przyciski do zmiennych.
        """
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._settings_button = self._buttons_dict['settings_button']
        self._quit_button = self._buttons_dict['quit_button']

    def update(self, events: list) -> str:
        """
        Obsługuje interakcję z menu pauzy (przyciski i klawisze).

        Args:
            events (list): Lista zdarzeń Pygame.

        Returns:
            str: Komenda sterująca (np. 'UNPAUSE_GAME', 'RESTART_LEVEL').
                 Zwraca 'STAY', jeśli nie podjęto żadnej akcji.
        """
        next_state = "STAY"
        if self._play_button.is_clicked(events):
            return "UNPAUSE_GAME"
        if self._retry_button.is_clicked(events):
            return 'RESTART_LEVEL'
        if self._settings_button.is_clicked(events):
            # Tu można dodać ekran ustawień aplikacji
            pass
        if self._quit_button.is_clicked(events):
            return "GO_TO_MENU"

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                next_state = "UNPAUSE_GAME"

        return next_state

    def draw(self, screen):
        """
        Rysuje menu pauzy na ekranie.

        Najpierw rysuje zapauzowaną grę (jako tło), a następnie
        elementy interfejsu pauzy na wierzchu.

        Args:
            screen (pygame.Surface): Powierzchnia, na której ma
                                     zostać narysowany stan.
        """
        self._paused_state.draw(screen)
        self._draw_objects(screen)
