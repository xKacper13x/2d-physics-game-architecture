from states.base_state import State
from states.main_menu_state import MainMenuState
from states.gameplay_states import GameState
import pygame
import sys
import ctypes


class AngryKnightsApp:
    def __init__(self):
        pygame.init()
        icon_image = pygame.image.load('assets/images/Title_Screen_button.png')
        pygame.display.set_icon(icon_image)

        self._screen = pygame.display.set_mode((1920, 1080), pygame.SCALED)
        self._is_fullscreen = False
        pygame.display.set_caption("Angry Knights")
        self._screen_size = self.screen_size()
        self.clock = pygame.time.Clock()
        self.running = True

        self._state = MainMenuState(self._screen_size)

    def screen_size(self) -> pygame.Vector2:
        screen_x = self._screen.get_width()
        screen_y = self._screen.get_height()
        return pygame.Vector2(screen_x, screen_y)

    def _change_screen_mode(self) -> None:
        if self._is_fullscreen:
            self._screen = pygame.display.set_mode((1920, 1080), pygame.SCALED)
            self._is_fullscreen = False
        else:
            self._screen = pygame.display.set_mode((1920, 1080),
                                                   pygame.FULLSCREEN |
                                                   pygame.SCALED)
            self._is_fullscreen = True

    def run(self) -> None:
        delta_time = 0.1
        while self.running:
            events = pygame.event.get()
            # 1. Przekaż obsługę logiki do aktualnego stanu
            # Stan zwraca samego siebie lub NOWY stan
            result = self._state.update(events)
            self._state = self._manage_states(result)

            # 2. Rysowanie
            self._state.draw(self._screen)

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._change_screen_mode()
            pygame.display.flip()
            delta_time = self.clock.tick(60) / 1000
            delta_time = max(0.001, min(0.1, delta_time))

    def _manage_states(self, result: State | str) -> State:
        if isinstance(result, State):
            return result
        elif result == "GO_TO_MENU":
            self.state = MainMenuState(self._screen_size)
        elif result == "START_GAME":
            self.state = GameState(self._screen_size, 1)
        return self.state


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
