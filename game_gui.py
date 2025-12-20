import pygame


class Button:
    def __init__(self, left, top, width, height):
        self._button_rect = pygame.Rect(left, top, width, height)

    def rect(self):
        return self._button_rect


class State:
    def __init__(self, screen_size):
        self._screen_size = screen_size
        self._mpos = pygame.mouse.get_pos()
        if not pygame.font.get_init():
            pygame.font.init()
        self._main_font = pygame.font.Font('fonts/angrybirds-regular.ttf', 20)

    def update(self):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))

    def get_font(self) -> pygame.font.Font:
        return self._main_font


class TitleScreenState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)
        self.pressed_keys = []
        self._img_adress = 'images/Title-Screen.png'
        self._background_image = pygame.image.load(self._img_adress).convert()
        img = self._background_image
        self._background_image = pygame.transform.scale(img, self._screen_size)

    def update(self):
        self.pressed_keys = pygame.key.get_pressed()
        if True in self.pressed_keys:
            return MainMenuState(self._screen_size)
        else:
            return self

    def draw(self, screen):
        screen.blit(self._background_image, (0, 0))


class MainMenuState(State):
    def __init__(self, screen_size):
        super().__init__(screen_size)


    def update(self):
        return super().update()

    def draw(self, screen):
        middle = pygame.Vector2(self._screen_size / 4)
        self.button = Button(middle[0], middle[1], 50, 50)

        super().draw(screen)
        pygame.draw.rect(screen, (255, 255, 0), self.button.rect())
