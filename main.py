from menu_states import TitleScreenState
import pygame
import sys
import ctypes


class AngryKnightsApp:
    def __init__(self):
        pygame.init()
        icon_image = pygame.image.load('assets/images/Title_Screen_button.png')
        pygame.display.set_icon(icon_image)

        self._set_screen_mode(True)
        self._is_fullscreen = True
        pygame.display.set_caption("Angry Knights")
        self._screen_size = self.screen_size()
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = TitleScreenState(self._screen_size)

    def screen_size(self):
        screen_x = self._screen.get_width()
        screen_y = self._screen.get_height()
        return pygame.Vector2(screen_x, screen_y)

    def _set_screen_mode(self, fullscreen: bool):
        # Sprawdza, jaki mamy monitor
        info = pygame.display.Info()
        screen_w = info.current_w
        screen_h = info.current_h
        if screen_w >= 1920 and screen_h >= 1080:
            if fullscreen:
                self._screen = pygame.display.set_mode((1920, 1080),
                                                       pygame.FULLSCREEN)
            else:
                self._screen = pygame.display.set_mode((1920, 1080))
        else:
            if fullscreen:
                self._screen = pygame.display.set_mode((1920, 1080),
                                                       pygame.FULLSCREEN
                                                       | pygame.SCALED)
            else:
                self._screen = pygame.display.set_mode((1920, 1080),
                                                       pygame.SCALED)

    def _change_screen_mode(self):
        if self._is_fullscreen:
            self._set_screen_mode(False)
            self._is_fullscreen = False
        else:
            self._set_screen_mode(True)
            self._is_fullscreen = True

    def run(self):
        delta_time = 0.1
        while self.running:
            events = pygame.event.get()
            # 1. Przekaż obsługę logiki do aktualnego stanu
            # Stan zwraca samego siebie lub NOWY stan
            self.state = self.state.update(events)

            # 2. Rysowanie
            self.state.draw(self._screen)

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._change_screen_mode()
            pygame.display.flip()
            delta_time = self.clock.tick(60) / 1000
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
