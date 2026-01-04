from game_objects import GameObject
import pygame
import helpers


class Button(GameObject):
    def __init__(self, object_data, x_pos):
        offset = object_data['offset']
        self._pos = (x_pos + offset, object_data['y_pos'])
        super().__init__(object_data)

    def size(self):
        return self._object_rect.size

    def rect(self):
        return self._object_rect

    def draw(self, screen):
        super().draw(screen)

    def is_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    m_collision = self._object_rect.collidepoint(event.pos)
                    if m_collision:
                        return True
        return False


class TextButton(Button):
    def __init__(self, object_data, x_pos):
        super().__init__(object_data, x_pos)
        self._text = object_data['text']

        self._text_color = (235, 213, 174)
        self._font_path = object_data['font_path']
        self._font_size = object_data['font_size']
        self._text_surface = None
        self._text_rect = None
        self._add_text()

    def _add_text(self):
        self._button_font = helpers.initialize_font(self._font_path,
                                                    self._font_size)

        self._text_surface = self._button_font.render(self._text, True,
                                                      self._text_color)
        self._text_rect = self._text_surface.get_rect()
        self._text_rect.center = (self._object_rect.center)

    def draw(self, screen):
        super().draw(screen)
        if self._text_surface is not None:
            screen.blit(self._text_surface, self._text_rect)
