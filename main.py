from states.base_state import State
from states.main_menu_state import MainMenuState
from states.gameplay_states import GameState, PauseState, LevelCompleteState
import pygame
import sys
import ctypes


class AngryKnightsApp:
    """
    Główna klasa aplikacji zarządzająca cyklem życia gry 'Angry Knights'.

    Klasa ta odpowiada za:
    - Inicjalizację biblioteki Pygame i okna gry.
    - Obsługę głównej pętli (game loop).
    - Przechwytywanie globalnych zdarzeń (np. zamknięcie okna,
                                        przełączenie pełnego ekranu).
    - Zarządzanie maszyną stanów (przełączanie między Menu, Grą, Pauzą itp)

    Attributes:
        _screen (pygame.Surface): Główna powierzchnia rysowania (okno gry).
         _is_fullscreen (bool): Flaga określająca,
                                        czy gra jest w trybie pełnoekranowym.
        _screen_size (pygame.Vector2): Wymiary okna gry.
        _clock (pygame.time.Clock): Zegar kontrolujący liczbę klatek na
                                                                sekundę (FPS).
        _running (bool): Flaga sterująca główną pętlą gry.
        _state (State): Aktualnie aktywny stan gry (np. Menu, Rozgrywka).
    """
    def __init__(self):
        """
        Inicjalizuje aplikację, ustawia okno, jego rozmiar, ikonę oraz
        Stan początkowy(Menu)
        W przypadku braku pliku ikony, błąd jest ignorowany,
        aby nie przerywać gry
        """
        pygame.init()

        try:
            icon_path = 'assets/images/Title_Screen_button.png'
            icon_image = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_image)
        except FileNotFoundError:
            pass

        self._screen = pygame.display.set_mode((1920, 1080), pygame.SCALED)
        self._is_fullscreen = False
        pygame.display.set_caption("Angry Knights")
        self._screen_size = self.screen_size()
        self._clock = pygame.time.Clock()
        self._running = True

        self._state = MainMenuState(self._screen_size)

    def screen_size(self) -> pygame.Vector2:
        """
        Zwraca ustawiony rozmiar okna

        Returns:
            pygame.Vector2: Wektor zawierający szerokość i wysokość okna
        """
        screen_x = self._screen.get_width()
        screen_y = self._screen.get_height()
        return pygame.Vector2(screen_x, screen_y)

    def _change_screen_mode(self) -> None:
        """
        Przełącza tryb wyświetlania między oknem a pełnym ekranem (Fullscreen).

        Zachowuje rozdzielczość logiczną 1920x1080 dzięki fladze pygame.SCALED.
        """
        if self._is_fullscreen:
            self._screen = pygame.display.set_mode((1920, 1080), pygame.SCALED)
            self._is_fullscreen = False
        else:
            self._screen = pygame.display.set_mode((1920, 1080),
                                                   pygame.FULLSCREEN |
                                                   pygame.SCALED)
            self._is_fullscreen = True

    def _manage_states(self, result: str) -> State:
        """
        Centrala zarządzająca maszyną stanów.
        Interpretuje otrzymane wyniki w postaci stringa.

        Args:
            result (str): Komenda sterująca stanami.

        Returns:
            State: Nowy obiekt stanu, który ma zostać aktywowany w następnej
                   klatce, lub obecny stan, jeśli nie nastąpiła żadna zmiana.
        """
        # Obsluga Komend sterujących
        if result == "GO_TO_MENU":
            state = MainMenuState(self._screen_size)

        elif result == "START_GAME":
            # Rozpoczęcie nowej gry od poziomu 1
            state = GameState(self._screen_size, 1)

        elif result == "PAUSE_GAME":
            # Zapauzowanie gry, przekazuje obecny stan do stanu pauzy,
            # żeby móc do niego wrócić
            state = PauseState(self._screen_size, self._state)

        elif result == "UNPAUSE_GAME":
            # wymaga y get_paused_state w stanie PauseState
            # Wraca do wstrzymanego momentu rozgrywki
            state = self._state.get_paused_state()

        elif result == "END_LEVEL":
            # Zakończenie poziomu i wyświetlenie jego podsumowania (wyniki)
            state = LevelCompleteState(self._screen_size, self._state)

        elif result == "NEXT_LEVEL":
            # wymaga metody get_completed_level() w klasie LevelCompleteState
            current_level = self._state.get_level()
            try:
                # Próbujemy uruchomić następny poziom gry
                next_level_index = current_level + 1
                state = GameState(self._screen_size, next_level_index)
                # Oznacza, że nie ukończyliśmy ostatni poziom
            except FileNotFoundError:
                # Wykryty wyjątek oznacza, że ukończony właśnie poziom był
                # ostatnim w grze, przechodzimy do menu głównego
                state = MainMenuState(self._screen_size)

        elif result == "RESTART_LEVEL":
            # Uruchamia ponownie właśnie zakończony poziom gry
            current_level = self._state.get_level()
            state = GameState(self._screen_size, current_level)

        else:
            # Jeśli brak zmian - zostajemy w tym samym stanie
            state = self._state
        return state

    def run(self) -> None:
        """
        Główna pętla programu. Aktualizuje i rysuje stany.
        Otrzymane z update() stanów komendy sterujące przekazuje do
        metody _manage_states(), po czym ustawia nowy Stan gry.

        Wykrywa:
        - Zamknięcie programu: Przerywa pętlę.
        - Wciśniecie klawisza F11: Zmienia tryb wyświetlania aplikacji.
        """
        delta_time = 0.1
        while self._running:
            events = pygame.event.get()

            # 1. Przekaż obsługę logiki do aktualnego stanu
            # Stan zwraca samego siebie lub NOWY stan
            result = self._state.update(events)
            self._state = self._manage_states(result)

            # 2. Rysowanie
            self._state.draw(self._screen)

            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._change_screen_mode()
            pygame.display.flip()
            delta_time = self._clock.tick(60) / 1000
            delta_time = max(0.001, min(0.1, delta_time))


if __name__ == '__main__':

    if sys.platform == "win32":
        myappid = 'mojanazwa.gra.knights.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    App = AngryKnightsApp()
    App.run()
