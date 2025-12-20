import pygame
from game_gui import TitleScreenState


class AngryBirdsApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        screen_x = self.screen.get_width()
        screen_y = self.screen.get_height()
        self._screen_size = pygame.Vector2(screen_x, screen_y)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = TitleScreenState(self._screen_size)

    def screen_size(self):
        return self._screen_size

    def run(self):
        delta_time = 0.1
        while self.running:
            # 1. Przekaż obsługę logiki do aktualnego stanu
            # Stan zwraca samego siebie lub NOWY stan
            self.state = self.state.update()

            # 2. Rysowanie
            self.state.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()
            delta_time = self.clock.tick(60) / 1000
            delta_time = max(0.001, min(0.1, delta_time))


if __name__ == '__main__':
    App = AngryBirdsApp()
    App.run()
