import pygame
from menu_states import TitleScreenState


class AngryBirdsApp:
    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((1920, 1080))
        self._screen_size = self.screen_size()
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = TitleScreenState(self._screen_size)

    def screen_size(self):
        screen_x = self._screen.get_width()
        screen_y = self._screen.get_height()
        return pygame.Vector2(screen_x, screen_y)

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

            pygame.display.flip()
            delta_time = self.clock.tick(60) / 1000
            delta_time = max(0.001, min(0.1, delta_time))


if __name__ == '__main__':
    App = AngryBirdsApp()
    App.run()
