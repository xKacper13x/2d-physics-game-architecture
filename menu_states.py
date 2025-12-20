import buttons
import pygame
import exceptions
import os


class State:
    def __init__(self, screen_size):
        self._screen_size = screen_size

    def update(self):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))

    def check_path(self, path):
        if not os.path.exists(path):
            raise exceptions.MissingResourceError(path)

    def check_font_size(self, size=0):
        if size <= 0:
            msg = f"Font size must be > 0. Provided: {size}"
            raise exceptions.InvalidConfigurationError(msg)

    def load_image(self, img_path, img_size=None):
        self.check_path(img_path)

        if img_size is None:
            img_size = self._screen_size

        image = pygame.image.load(img_path).convert()
        image = pygame.transform.scale(image, img_size)
        return image

    def initialize_font(self, font_path, font_size):
        self.check_path(font_path)
        self.check_font_size(font_size)
        if not pygame.font.get_init():
            pygame.font.init()
        font = pygame.font.Font(font_path, font_size)
        return font
# 'fonts/angrybirds-regular.ttf'


class TitleScreenState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.pressed_keys = []
        self._background_image = self.load_image('images/Title-Screen.png')

        # font_path = 'fonts/angrybirds-regular.ttf'
        # self.title_font = self.initialize_font(font_path, font_size=50)
        # text_color = (255, 255, 255)
        # self.text_surface = self.menu_font.render("MAIN MENU", True, text_color)
        # self.text_rect = self.text_surface.get_rect()
        # self.text_rect.center = (self._screen_size[0] // 2, self._screen_size[1] // 2)

    def update(self):
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

    def update(self):
        return super().update()

    def draw(self, screen):
        middle = pygame.Vector2(self._screen_size / 4)
        self.button = buttons.Button(middle[0], middle[1], 50, 50)

        super().draw(screen)
        pygame.draw.rect(screen, (255, 255, 0), self.button.rect())
