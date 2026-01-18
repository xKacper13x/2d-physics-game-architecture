from .base_state import State
from core.signals import GameSignal
from services.base_service import BaseService
import pygame


class LevelCompleteState(State):
    """
    Stan podsumowania poziomu.

    Wyświetlany po zakończeniu poziomu rozgrywki.
    Prezentuje wynik punktowy, high score oraz umożliwia przejście dalej,
    restart lub wyjście.

    Attributes:
        _current_score (int): Wynik uzyskany w zakończonym poziomie.
        _high_score (int): Rekord punktowy poziomu.
        _level (int): Numer zakończonego poziomu.
        _completed_level (State): Obiekt zakończonej gry (do tła).
        _overlay (pygame.Surface): Półprzezroczysta warstwa
                                   przyciemniająca tło.
        _overlay_rect (pygame.Rect): Pozycja warstwy przyciemniającej.
    """
    def __init__(self, screen_size: pygame.Vector2, completed_level: State):
        """
        Inicjalizuje ekran końca poziomu.

        Pobiera wyniki z zakończonej gry, wczytuje konfigurację UI
        oraz przygotowuje grafikę przyciemnienia tła.

        Args:
            screen_size (pygame.Vector2): Wymiary okna gry.
            completed_level (State): Stan zakończonej gry (GameState),
                                     z którego pobierane są wyniki
                                     i numer poziomu.
        """
        scores = completed_level.get_scores()
        self._current_score, self._high_score = scores
        self._completed_level = completed_level
        self._level = self._completed_level.get_level()

        path = 'level_summary.json'
        service = BaseService()
        data = service.load_data(path)
        super().__init__(screen_size, data)
        self._create_buttons()

        self._update_score_labels(self._current_score,
                                  self._high_score)

    def get_completed_level_state(self) -> State:
        """
        Zwraca obiekt stanu ukończonego poziomu.

        Returns:
            State: Obiekt stanu zakończonego poziomu.
        """
        return self._completed_level

    def get_level(self) -> int:
        """
        Zwraca numer ukończonego poziomu.

        Returns:
            int: Numer poziomu.
        """
        return self._level

    def _create_buttons(self) -> None:
        """
        Przypisuje obiekty przycisków ze słownika do dedykowanych atrybutów.

        Ułatwia to odwoływanie się do nich w metodzie obsługi wejścia.
        """
        self._play_button = self._buttons_dict['play_button']
        self._retry_button = self._buttons_dict['retry_button']
        self._quit_button = self._buttons_dict['quit_button']

    def _handle_input(self, events: list) -> str:
        """
        Sprawdza interakcję gracza z przyciskami interfejsu.

        Args:
            events (list): Lista zdarzeń Pygame.

        Returns:
            str: Komenda sterująca zmianą stanu (lub 'STAY').
        """
        next_state = GameSignal.STAY
        if self._play_button.is_clicked(events):
            if self._current_score > 0:
                next_state = GameSignal.NEXT_LEVEL
            else:
                next_state = GameSignal.RESTART_LEVEL
        elif self._retry_button.is_clicked(events):
            next_state = GameSignal.RESTART_LEVEL
        elif self._quit_button.is_clicked(events):
            next_state = GameSignal.GO_TO_MENU
        return next_state

    def update(self, events):
        """
        Główna metoda aktualizacji logiki podsumowania.

        Args:
            events (list): Lista zdarzeń Pygame.

        Returns:
            str: Komenda sterująca oznaczająca następny stan
                 lub pozostanie w aktualnym.
        """
        next_state = self._handle_input(events)
        return next_state

    def draw(self, screen):
        """
        Rysuje ekran podsumowania.

        Kolejność:
        1. Tło (zakończony poziom).
        2. Przyciemnienie (Overlay).
        3. UI (przyciski, teksty).

        Args:
            screen (pygame.Surface): Ekran docelowy.
        """
        self._completed_level.draw(screen)

        overlay = pygame.Surface((self._screen_size.x / 2,
                                  self._screen_size.y),
                                 pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        overlay_rect = overlay.get_rect()
        overlay_rect.center = (self._screen_size / 2)
        screen.blit(overlay, overlay_rect)

        self._draw_objects(screen)
        self._draw_texts(screen)
