import pygame
import helpers


class Button:
    def __init__(self, pos, size, img_path):
        helpers.check_pos(pos)
        helpers.check_size(size)
        self._image = self.load_image(img_path, size)
        self._button_rect = self._image.get_rect()
        self._button_rect.center = pos

    def position(self):
        return self._button_rect.center

    def size(self):
        return self._button_rect.size

    def rect(self):
        return self._button_rect

    def load_image(self, img_path, img_size=None):
        return helpers.load_image(img_path, img_size)

    def draw(self, screen):
        screen.blit(self._image, self._button_rect)
        screen.blit(self._text_surface, self._text_rect)

    def is_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    m_collision = self._button_rect.collidepoint(event.pos)
                    if m_collision:
                        return True
        return False

    def add_text(self, text, font_path, font_size):
        self._button_font = helpers.initialize_font(font_path, font_size)
        text_color = (235, 213, 174)
        self._text_surface = self._button_font.render(text, True, text_color)
        self._text_rect = self._text_surface.get_rect()
        self._text_rect.center = (self._button_rect.center)
