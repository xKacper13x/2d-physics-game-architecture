import pygame


class Button:
    def __init__(self, left, top, width, height):
        self._button_rect = pygame.Rect(left, top, width, height)

    def rect(self):
        return self._button_rect


class State:
    def __init__(self):
        pass

    def update(self):
        return self

    def draw(self, screen):
        screen.fill((255, 255, 255))


class TitleScreenState(State):
    def __init__(self):
        super().__init__()
        self.pressed_keys = []
        self._img_adress = 'images/Title-Screen.png'
        self._background_image = pygame.image.load(self._img_adress).convert()

    def update(self):
        self.pressed_keys = pygame.key.get_pressed()
        if True in self.pressed_keys:
            return MainMenuState()
        else:
            return self

    def draw(self, screen):
        middle = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        screen.blit(self._background_image, middle)
        screen.fill((0, 255, 0))


class MainMenuState(State):
    def __init__(self):
        super().__init__()
        self.mpos = pygame.mouse.get_pos()

    def update(self):
        return super().update()

    def draw(self, screen):
        middle = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
        self.button = Button(middle[0], middle[1], 50, 50)

        super().draw(screen)
        pygame.draw.rect(screen, (255, 255, 0), self.button.rect())
