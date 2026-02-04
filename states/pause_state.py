from .base_state import State
from core.signals import GameSignal
from core.input_handler import InputData
from services.base_service import BaseService
import pygame


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
        service = BaseService()
        data = service.load_data('pause.json')
        super().__init__(screen_size, data)
        self._create_buttons()

    @property
    def paused_state(self) -> State:
        """
        Zwraca stan gry, który został zapauzowany.

        Returns:
            State: Zapamiętany obiekt GameState.
        """
        return self._paused_state

    @property
    def level(self) -> int:
        """
        Zwraca numer poziomu z zapauzowanej gry.

        Returns:
            int: Numer poziomu.
        """
        return self._paused_state.level

    def _create_buttons(self) -> None:
        """
        Przypisuje przyciski do zmiennych.
        """
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._settings_button = self._buttons_dict['settings_button']
        self._quit_button = self._buttons_dict['quit_button']

    def update(self, input_data: InputData) -> GameSignal:
        """
        Obsługuje interakcję z menu pauzy (przyciski i klawisze).

        Args:
            events (list): Lista zdarzeń Pygame.

        Returns:
            str: Komenda sterująca (np. 'UNPAUSE_GAME', 'RESTART_LEVEL').
                 Zwraca 'STAY', jeśli nie podjęto żadnej akcji.
        """
        next_state = GameSignal.STAY
        if self._play_button.is_clicked(input_data.lmb_clicked,
                                        input_data.mouse_pos):
            return GameSignal.UNPAUSE_GAME
        if self._retry_button.is_clicked(input_data.lmb_clicked,
                                         input_data.mouse_pos):
            return GameSignal.RESTART_LEVEL
        if self._settings_button.is_clicked(input_data.lmb_clicked,
                                            input_data.mouse_pos):
            # Tu można dodać ekran ustawień aplikacji
            pass
        if self._quit_button.is_clicked(input_data.lmb_clicked,
                                        input_data.mouse_pos):
            return GameSignal.GO_TO_MENU

        if input_data.key_esc_down:
            next_state = GameSignal.UNPAUSE_GAME

        return next_state

    def draw(self, screen: pygame.Surface) -> None:
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
