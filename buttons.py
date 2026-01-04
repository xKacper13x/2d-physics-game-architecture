from game_objects import GameObject
import pygame
import helpers


class Button(GameObject):
    def __init__(self, object_data, screen_size: pygame.Vector2):
        screen_w, screen_h = screen_size
        anchor = object_data.get('anchor', 'center')  # Domyślnie środek
        off_x = object_data.get('x_offset', 0)
        off_y = object_data.get('y_offset', 0)

        # Obliczamy punkt bazowy na podstawie kotwicy
        base_x, base_y = 0, 0

        if anchor == 'center':
            base_x, base_y = screen_w / 2, screen_h / 2
        elif anchor == 'top_left':
            base_x, base_y = 0, 0
        elif anchor == 'top_right':
            base_x, base_y = screen_w, 0
        elif anchor == 'bottom_left':
            base_x, base_y = 0, screen_h
        elif anchor == 'bottom_right':
            base_x, base_y = screen_w, screen_h

        self._pos = (base_x + off_x, base_y + off_y)
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
    def __init__(self, object_data, screen_size: pygame.Vector2):
        super().__init__(object_data, screen_size)
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
