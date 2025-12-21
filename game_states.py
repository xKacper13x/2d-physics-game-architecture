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


class GameObject:
    def __init__(self, pos, size, img_path):
        helpers.check_size(size)
        self._image = self.load_image(img_path, size)
        self._button_rect = self._image.get_rect()
        self._button_rect.center = pos

    def draw(self, screen):
        screen.blit(self._image, self._button_rect)
        if self._text_surface is not None:
            screen.blit(self._text_surface, self._text_rect)


class GameState(State):
    def __init__(self, screen_size, level):
        super().__init__(screen_size)
        self._level = level

    def draw(self, screen):
        screen.fill((255, 255, 255))
