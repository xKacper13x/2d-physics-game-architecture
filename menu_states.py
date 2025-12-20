import buttons
import pygame
import helpers


class State:
    def __init__(self, screen_size):
        self._screen_size = screen_size

    def update(self, events):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))

    def load_image(self, img_path, img_size=None):
        if img_size is None:
            img_size = self._screen_size
        return helpers.load_image(img_path, img_size)

    def initialize_font(self, font_path, font_size):
        helpers.check_path(font_path)
        helpers.check_size(font_size)
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.Font(font_path, font_size)
        return font
# 'fonts/angrybirds-regular.ttf'


class TitleScreenState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.pressed_keys = []
        self._background_image = self.load_image(
            'assets/images/Title_Screen.jpg')

        # font_path = 'assets/fonts/Dalek.ttf'
        # self.title_font = self.initialize_font(font_path, font_size=20)
        # text_color = (0, 0, 0)
        # self.text_surface = self.title_font.render("MAIN MENU", True, text_color)
        # self.text_rect = self.text_surface.get_rect()
        # self.text_rect.center = (self._screen_size[0] // 2, self._screen_size[1] // 2)

    def update(self, events):
        self.pressed_keys = pygame.key.get_pressed()
        if True in self.pressed_keys:
            return MainMenuState(self._screen_size)
        else:
            return self

    def draw(self, screen):
        screen.blit(self._background_image, (0, 0))
        # screen.blit(self.text_surface, self.text_rect)


class MainMenuState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)

    def update(self, events):
        return super().update(events)

    def draw(self, screen):
        middle = pygame.Vector2(self._screen_size / 4)
        self.button = buttons.Button(middle[0], middle[1], 50, 50)

        super().draw(screen)
        pygame.draw.rect(screen, (255, 255, 0), self.button.rect())
